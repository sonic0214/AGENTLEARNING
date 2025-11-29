# ProductScout AI 后端调用链路分析

## 概述

本文档详细分析了当用户点击"开始分析"按钮时，ProductScout AI 系统的完整后端调用链路。系统采用分层架构，使用 Google ADK 框架实现多智能体并行分析。

## 整体架构图

```
用户界面 (Gradio)
    ↓
[1] UI层 - analysis_tab.py
    ↓
[2] 处理器层 - analysis_handlers.py
    ↓
[3] 服务层 - analysis_service.py
    ↓
[4] 运行器层 - runner.py
    ↓
[5] 管道层 - analysis_pipeline.py
    ↓
[6] 代理层 - analysis_agents.py + base_agent.py
    ↓
[7] 配置层 - prompts.py
    ↓
[8] ADK执行层 - Google ADK + Gemini API
```

## 详细调用链路

### 第1层: UI事件处理

**文件:** `src/ui/tabs/analysis_tab.py`

**触发流程:**
```python
# 用户点击 "🚀 开始分析" 按钮
run_btn.click(
    fn=on_analyze_click,  # 触发事件处理函数
    inputs=[category_input, market_dropdown, budget_radio, model_dropdown, keywords_input],
    outputs=[...]  # 所有UI组件
)

def on_analyze_click(category, market, budget, model, keywords):
    # 1. 验证输入
    is_valid, error = validate_inputs(category, market, budget, model, keywords)

    # 2. 更新状态
    yield gr.update(value="🔄 正在分析...")

    # 3. 创建异步事件循环
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # 4. 调用分析处理器
    success, result_data, error_msg = loop.run_until_complete(
        run_analysis(category, market, budget, model, keywords, progress_callback)
    )
```

**关键功能:**
- 收集用户输入参数
- 输入验证和错误处理
- 创建异步事件循环
- 调用下一层的 `run_analysis` 函数

### 第2层: 处理器层

**文件:** `src/ui/handlers/analysis_handlers.py`

**核心函数:**
```python
async def run_analysis(category, market, budget, model, keywords, progress_callback):
    # 1. 验证输入
    is_valid, error_msg = validate_inputs(category, market, budget, model, keywords)
    if not is_valid:
        return False, {}, error_msg

    # 2. 创建请求对象
    request = create_analysis_request(category, market, budget, model, keywords)
    # 生成: AnalysisRequest(
    #     category="便携式榨汁机",
    #     target_market="US",
    #     budget_range="medium",
    #     business_model="amazon_fba",
    #     keywords=["便携", "健身"]
    # )

    # 3. 创建服务实例
    service = create_analysis_service()
    history_service = create_history_service()

    # 4. 定义进度回调
    def on_progress(phase: str, message: str):
        if progress_callback:
            desc, progress_val = PHASE_DESCRIPTIONS.get(phase, (message, 0.5))
            progress_callback(progress_val, desc)

    # 5. 执行分析
    result = await service.analyze(request, on_progress=on_progress)

    # 6. 处理结果
    if result.success:
        # 添加到历史记录
        history_service.add_entry(request, result)
        # 转换为字典格式
        result_data = convert_result_to_dict(result)
        return True, result_data, ""
    else:
        return False, {}, result.error or "分析失败"
```

**关键功能:**
- 输入验证和标准化
- 创建结构化的 `AnalysisRequest` 对象
- 服务实例创建和配置
- 进度回调管理
- 结果格式转换

### 第3层: 服务层

**文件:** `src/services/analysis_service.py`

**核心方法:**
```python
class AnalysisService:
    async def analyze(self, request: AnalysisRequest, on_progress):
        start_time = time.time()

        # 1. 记录分析开始
        log_analysis_start(self.logger, request.category, request.target_market)

        # 2. 检查缓存
        cached_result = self._get_cached_result(request)
        if cached_result:
            self.logger.info("♻️  Using cached result")
            return cached_result

        # 3. 并发控制
        async with self._semaphore:  # 最多5个并发分析
            self.logger.info(f"🔒 Acquired analysis slot")

            # 4. 初始化Pipeline
            if on_progress:
                def phase_callback(phase: str, data: Dict[str, Any]):
                    message = get_phase_description(phase)
                    self.logger.info(f"📍 Phase update: {phase}")
                    on_progress(phase, message)

                self._runner.initialize_pipeline(on_phase_complete=phase_callback)
            else:
                self._runner.initialize_pipeline()

            # 5. 创建会话
            session = await self._runner.create_session()

            # 6. 跟踪活动分析
            analysis_id = session.id if hasattr(session, 'id') else "unknown"
            state = AnalysisState(request=request)
            self._active_analyses[analysis_id] = state

            try:
                # 7. 执行分析
                result = await self._runner.run_analysis(request, session)

                # 8. 缓存结果
                if result.success:
                    self._cache_result(request, result)

                return result

            finally:
                # 9. 清理资源
                if analysis_id in self._active_analyses:
                    del self._active_analyses[analysis_id]
```

**关键功能:**
- 并发控制(信号量限制最大并发数)
- 结果缓存管理
- 会话生命周期管理
- 错误处理和资源清理
- 进度跟踪和日志记录

### 第4层: Pipeline执行器

**文件:** `src/workflows/runner.py`

**核心方法:**
```python
class PipelineRunner:
    async def run_analysis(self, request: AnalysisRequest, session: Optional[Session] = None):
        start_time = datetime.now()
        phase_times = {}

        # 1. 初始化
        if session is None:
            session = await self.create_session()

        state = AnalysisState(request=request)
        state.set_phase("initialized")

        if self._pipeline is None:
            self.initialize_pipeline()

        try:
            # === 阶段1: 并行分析 ===
            phase_start = datetime.now()
            state.set_phase("analyzing_trends")
            log_phase_start(self.logger, "parallel_analysis", "Running parallel agents...")

            # 1.1 创建Pipeline Agents
            self.logger.info("📦 Creating pipeline agents...")
            pipeline_agents = self._pipeline.create_pipeline_agents(request)

            # 返回: {
            #   "parallel_agent": ParallelAgent([...]),
            #   "trend_agent": LlmAgent,
            #   "market_agent": LlmAgent,
            #   "competition_agent": LlmAgent,
            #   "profit_agent": LlmAgent
            # }

            # 1.2 创建ADK Runner
            self.logger.info("🏃 Initializing ADK Runner...")
            parallel_runner = Runner(
                agent=pipeline_agents["parallel_agent"],
                app_name=self.config.app_name,
                session_service=self._session_service
            )

            # 1.3 执行并行分析
            self.logger.info("🚀 Executing parallel analysis agents...")

            # 创建消息对象(Google ADK要求)
            class SimpleMessage:
                def __init__(self, content):
                    self.content = content
                    self.role = "user"

            message = SimpleMessage(f"请分析产品类别 '{request.category}' 在市场 '{request.target_market}' 的机会")

            # 使用ADK Runner执行
            events = []
            event_count = 0

            for event in parallel_runner.run(
                user_id="system",
                session_id=session.id if hasattr(session, 'id') else str(uuid.uuid4()),
                new_message=message
            ):
                events.append(event)
                event_count += 1
                self.logger.debug(f"📨 Agent event {event_count}: {type(event).__name__}")

            # 获取最终结果
            result = events[-1] if events and len(events) > 0 else None

            # 1.4 TODO: 解析结果到状态
            # 这里需要实现: state.trend_analysis = parse_trend_result(result)
            #                    state.market_analysis = parse_market_result(result)
            #                    ...

            phase_times["parallel_analysis"] = (datetime.now() - phase_start).total_seconds()
            log_phase_complete(self.logger, "parallel_analysis", phase_times["parallel_analysis"])

            # === 阶段2: 评估 (TODO) ===
            # 类似的模式，调用 EvaluatorAgent
            # === 阶段3: 报告生成 (TODO) ===
            # 类似的模式，调用 ReportAgent

            # 返回结果
            execution_time = (datetime.now() - start_time).total_seconds()
            return PipelineResult(
                success=True,
                state=state,
                execution_time=execution_time,
                phase_times=phase_times
            )

        except Exception as e:
            state.set_error(str(e))
            execution_time = (datetime.now() - start_time).total_seconds()
            return PipelineResult(
                success=False,
                state=state,
                error=str(e),
                execution_time=execution_time,
                phase_times=phase_times
            )
```

**关键功能:**
- 3个分析阶段的编排
- Pipeline Agent的创建和管理
- Google ADK Runner的配置和执行
- 状态管理和错误处理
- 性能监控和时间统计

### 第5层: Pipeline编排器

**文件:** `src/workflows/analysis_pipeline.py`

**核心方法:**
```python
class AnalysisPipeline:
    def create_pipeline_agents(self, request: AnalysisRequest):
        # 1. 创建4个分析Agent
        trend_agent = self._trend_agent.create_agent(
            category=request.category,
            target_market=request.target_market
        )

        market_agent = self._market_agent.create_agent(
            category=request.category,
            target_market=request.target_market
        )

        competition_agent = self._competition_agent.create_agent(
            category=request.category,
            target_market=request.target_market
        )

        profit_agent = self._profit_agent.create_agent(
            category=request.category,
            target_market=request.target_market,
            business_model=request.business_model,
            budget_range=request.budget_range
        )

        # 2. 创建并行Agent容器
        parallel_agent = ParallelAgent(
            name="parallel_analysis",
            sub_agents=[trend_agent, market_agent, competition_agent, profit_agent],
            description="Execute all analyses concurrently"
        )

        # 3. 返回所有Agent
        return {
            "parallel_agent": parallel_agent,
            "trend_agent": trend_agent,
            "market_agent": market_agent,
            "competition_agent": competition_agent,
            "profit_agent": profit_agent,
            "request": request
        }
```

**关键功能:**
- 协调各个Agent的创建
- 使用ParallelAgent包装4个分析Agent
- 提供Agent的工厂方法
- 管理Agent之间的依赖关系

### 第6层: Agent实现层

**文件:**
- `src/agents/analysis_agents.py` (具体Agent实现)
- `src/agents/base_agent.py` (基础类)

**BaseAnalysisAgent 基础类:**
```python
class BaseAnalysisAgent:
    def __init__(self, config: AgentConfig, settings: Optional[Settings] = None):
        self.config = config
        self.settings = settings or Settings()
        self._agent: Optional[LlmAgent] = None

    def create_agent(self, **format_kwargs) -> LlmAgent:
        # 1. 格式化指令模板
        instruction = format_prompt(
            self.config.instruction_template,
            **format_kwargs  # category, target_market等动态参数
        )

        # 2. 准备工具列表
        tools = self.config.tools or []
        if google_search not in tools:
            tools = [google_search] + tools

        # 3. 创建Google ADK的LlmAgent
        self._agent = LlmAgent(
            name=self.config.name,           # 如 "trend_agent"
            model=self.settings.MODEL_NAME,  # 如 "gemini-2.0-flash-exp"
            instruction=instruction,         # 完整的分析指令
            description=self.config.description,
            tools=tools,                     # [google_search]
        )

        return self._agent
```

**具体Agent实现示例 (TrendAgent):**
```python
class TrendAgent(BaseAnalysisAgent):
    def __init__(self, settings: Optional[Settings] = None):
        config = AgentConfig(
            name="trend_agent",
            description="Analyzes market trends, search patterns, and seasonality",
            instruction_template=TREND_AGENT_INSTRUCTION,  # Prompt模板
            tools=[google_search],
            output_key="trend_analysis"
        )
        super().__init__(config, settings)

    def create_agent(self, category: str, target_market: str, **kwargs) -> LlmAgent:
        return super().create_agent(
            category=category,
            target_market=target_market,
            **kwargs
        )
```

**关键功能:**
- Agent配置和初始化
- Prompt模板的动态格式化
- Google ADK LlmAgent的创建
- 工具的管理和配置

### 第7层: Prompt配置层

**文件:** `src/config/prompts.py`

**TrendAgent Prompt示例:**
```python
TREND_AGENT_INSTRUCTION = """You are a market trend analyst specializing in e-commerce product trends.

## Your Task
Analyze search trends and market signals for product category: {category}
Target Market: {target_market}

## Analysis Requirements
1. **Search Trend Analysis**
   - Analyze current search interest levels
   - Identify year-over-year growth/decline
   - Determine trend direction (rising/stable/declining)

2. **Seasonality Detection**
   - Identify peak demand periods
   - Identify low demand periods
   - Assess seasonal impact on business

3. **Related Opportunities**
   - Find related trending searches
   - Identify emerging sub-niches
   - Spot complementary product opportunities

## Output Format
Provide your analysis as structured JSON with:
- trend_score: 1-100 (higher = better opportunity)
- trend_direction: "rising" | "stable" | "declining"
- seasonality: {{peak_months: [], low_months: [], seasonal_impact: str}}
- related_queries: [{{query: str, trend: str}}]
- analysis_summary: Brief text summary

Use available tools to gather data and support your analysis with evidence."""
```

**关键功能:**
- 定义每个Agent的角色和任务
- 指定详细的分析要求
- 规范化的JSON输出格式
- 工具使用指导

### 第8层: ADK执行层

**执行流程:**
```python
# Google ADK 内部执行逻辑
for sub_agent in parallel_agent.sub_agents:
    # 并行执行每个LlmAgent
    asyncio.create_task(execute_agent(sub_agent))

# 每个LlmAgent的执行
def execute_agent(agent):
    # 1. 调用Gemini API
    response = gemini.generate(
        model=agent.model,        # "gemini-2.0-flash-exp"
        prompt=agent.instruction, # 完整的分析指令
        tools=agent.tools         # [google_search]
    )

    # 2. 处理工具调用(如果LLM需要)
    if response.tool_calls:
        tool_results = []
        for tool_call in response.tool_calls:
            result = execute_tool(tool_call)  # 执行google_search
            tool_results.append(result)

        # 3. 将工具结果返回给LLM继续处理
        final_response = gemini.generate(
            prompt=agent.instruction,
            tool_results=tool_results
        )
        return final_response

    return response
```

**关键功能:**
- 多Agent并行执行
- LLM与工具的协调
- 工具调用的结果处理
- 异步任务管理

## 数据流转图

```
用户输入
{
  "category": "便携式榨汁机",
  "target_market": "US",
  "budget_range": "medium",
  "business_model": "amazon_fba",
  "keywords": ["便携", "健身"]
}
    ↓
AnalysisRequest 对象
    ↓
ParallelAgent([
  TrendAgent → LlmAgent(instruction=TREND_PROMPT, tools=[google_search]),
  MarketAgent → LlmAgent(instruction=MARKET_PROMPT, tools=[google_search]),
  CompetitionAgent → LlmAgent(instruction=COMPETITION_PROMPT, tools=[google_search]),
  ProfitAgent → LlmAgent(instruction=PROFIT_PROMPT, tools=[google_search])
])
    ↓
并行执行 (Google ADK)
    ↓
4个独立的分析结果(JSON格式)
{
  "trend_analysis": {
    "trend_score": 85,
    "trend_direction": "rising",
    "seasonality": {...},
    "related_queries": [...]
  },
  "market_analysis": {
    "market_score": 75,
    "market_size": {...},
    "growth_rate": 0.15,
    ...
  },
  "competition_analysis": {...},
  "profit_analysis": {...}
}
    ↓
PipelineResult(包含AnalysisState)
    ↓
转换为UI字典格式
    ↓
显示在界面上
```

## 核心设计要点

### 1. 分层架构
- **UI层**: 用户交互和事件处理
- **处理层**: 业务逻辑和数据转换
- **服务层**: 并发控制、缓存、会话管理
- **执行层**: Pipeline编排和Agent协调
- **Agent层**: 具体的分析逻辑
- **配置层**: Prompt模板和工具配置

### 2. Agent设计模式
每个Agent本质上是:
```python
LlmAgent(
    name="trend_agent",
    model="gemini-2.0-flash-exp",
    instruction="格式化的Prompt",
    tools=[google_search]
)
```

### 3. 并行执行策略
- 使用Google ADK的`ParallelAgent`实现并行
- 4个分析Agent同时执行，提高效率
- 每个Agent可以独立使用工具

### 4. 错误处理和容错
- 每层都有适当的异常处理
- 服务层有并发控制和资源管理
- 结果缓存机制

### 5. 可扩展性设计
- 基于配置的Agent创建
- 模块化的Prompt系统
- 标准化的接口设计

## 当前实现状态

### ✅ 已实现
- 完整的UI层到服务层调用链
- 4个分析Agent的创建和配置
- Google ADK并行执行框架
- 基础的错误处理和日志记录

### ⚠️ 部分实现
- Agent结果的解析和状态存储(TODO)
- EvaluatorAgent的执行(TODO)
- ReportAgent的报告生成(TODO)

### ❌ 待实现
- 结果的智能汇总和评估
- 动态的Agent编排
- 更复杂的依赖管理
- 结果的持久化存储

## 性能考虑

### 1. 并发性能
- 最多支持5个并发分析任务
- 4个Agent并行执行，理论上可以节省3/4的时间

### 2. 缓存策略
- 基于请求参数的简单缓存
- TTL为1小时，可配置

### 3. 资源管理
- 使用信号量防止资源过度使用
- 会话的及时清理
- 内存中的结果缓存

## 总结

ProductScout AI采用了现代化的分层架构，通过Google ADK框架实现了高效的多智能体并行分析系统。核心创新点在于:

1. **结构化的Prompt设计**: 每个Agent都有明确的角色定义和输出格式
2. **并行分析架构**: 4个维度同时分析，显著提升效率
3. **工具集成**: 每个Agent都可以主动使用Google Search获取实时数据
4. **灵活的配置**: 基于配置的Agent创建，易于扩展和维护

该架构为后续的功能扩展和智能化升级提供了良好的基础。