# ProductScout AI - 开发任务清单 (TDD驱动)

> 基于测试驱动开发(TDD)原则，按模块拆解的详细开发任务清单
> 每个任务遵循: 写测试 → 实现代码 → 重构 的循环

---

## 开发阶段总览

| 阶段 | 内容 | 预计时间 | 依赖 |
|------|------|----------|------|
| Phase 0 | 项目初始化 | 0.5天 | 无 |
| Phase 1 | 基础层 (config + schemas) | 0.5天 | Phase 0 |
| Phase 2 | 工具层 (tools) | 1天 | Phase 1 |
| Phase 3 | Agent层 (agents) | 1天 | Phase 2 |
| Phase 4 | 工作流层 (workflows) | 0.5天 | Phase 3 |
| Phase 5 | 服务层 (services) | 0.5天 | Phase 4 |
| Phase 6 | 接口层 (cli/api) | 0.5天 | Phase 5 |
| Phase 7 | 集成测试 + E2E | 0.5天 | Phase 6 |
| Phase 8 | 文档 + 部署 | 1天 | Phase 7 |
| Phase 9 | 优化 + 视频 | 1天 | Phase 8 |

**总计: 7-8天**

---

## Phase 0: 项目初始化

### Task 0.1: 创建项目结构
- [ ] 0.1.1 创建项目目录结构
- [ ] 0.1.2 初始化 pyproject.toml
- [ ] 0.1.3 创建 requirements.txt
- [ ] 0.1.4 创建 .env.example
- [ ] 0.1.5 创建 .gitignore
- [ ] 0.1.6 初始化 git 仓库

### Task 0.2: 配置开发环境
- [ ] 0.2.1 创建虚拟环境
- [ ] 0.2.2 安装核心依赖 (google-adk, pytest, etc.)
- [ ] 0.2.3 配置 pytest
- [ ] 0.2.4 验证 ADK 环境可用

### Task 0.3: 创建基础文件
- [ ] 0.3.1 创建所有 `__init__.py`
- [ ] 0.3.2 创建 conftest.py 基础框架
- [ ] 0.3.3 创建 README.md 框架

**验收标准:**
```bash
# 以下命令应能成功执行
pytest --collect-only  # 能发现测试
python -c "from google.adk.agents import LlmAgent"  # ADK可导入
```

---

## Phase 1: 基础层 (config + schemas)

### Task 1.1: 配置模块 (config/)

#### 1.1.1 settings.py
```
测试文件: tests/unit/config/test_settings.py
```

- [ ] **Test**: test_settings_loads_from_env
  - 验证能从环境变量加载配置
- [ ] **Test**: test_settings_has_defaults
  - 验证有合理的默认值
- [ ] **Test**: test_settings_validates_api_key
  - 验证API Key格式验证
- [ ] **Impl**: 实现 Settings 类
- [ ] **Impl**: 实现环境变量加载
- [ ] **Impl**: 实现配置验证

```python
# 预期接口
class Settings:
    GOOGLE_API_KEY: str
    MODEL_NAME: str = "gemini-2.0-flash"
    APP_NAME: str = "product_scout_ai"
    LOG_LEVEL: str = "INFO"
    MAX_RETRIES: int = 3

settings = Settings()
```

#### 1.1.2 prompts.py
```
测试文件: tests/unit/config/test_prompts.py
```

- [ ] **Test**: test_prompts_are_non_empty
  - 验证所有Prompt非空
- [ ] **Test**: test_prompts_contain_placeholders
  - 验证包含必要的占位符
- [ ] **Test**: test_prompt_formatting
  - 验证Prompt格式化功能
- [ ] **Impl**: 定义所有Agent的Prompt模板
- [ ] **Impl**: 实现Prompt格式化辅助函数

```python
# 预期接口
TREND_AGENT_INSTRUCTION: str
MARKET_AGENT_INSTRUCTION: str
COMPETITION_AGENT_INSTRUCTION: str
PROFIT_AGENT_INSTRUCTION: str
EVALUATOR_AGENT_INSTRUCTION: str
REPORT_AGENT_INSTRUCTION: str

def format_prompt(template: str, **kwargs) -> str: ...
```

---

### Task 1.2: 数据模型 (schemas/)

#### 1.2.1 input_schemas.py
```
测试文件: tests/unit/schemas/test_input_schemas.py
```

- [ ] **Test**: test_analysis_request_valid_input
  - 验证有效输入能创建对象
- [ ] **Test**: test_analysis_request_invalid_category
  - 验证空品类抛出异常
- [ ] **Test**: test_analysis_request_default_values
  - 验证默认值正确
- [ ] **Test**: test_analysis_request_to_dict
  - 验证能转为字典
- [ ] **Test**: test_analysis_request_from_dict
  - 验证能从字典创建
- [ ] **Impl**: 实现 AnalysisRequest dataclass
- [ ] **Impl**: 实现 UserPreferences dataclass
- [ ] **Impl**: 实现验证逻辑

```python
# 预期接口
@dataclass
class AnalysisRequest:
    category: str
    target_market: str = "US"
    budget_range: str = "medium"
    business_model: str = "amazon_fba"
    keywords: List[str] = field(default_factory=list)

    def validate(self) -> bool: ...
    def to_dict(self) -> dict: ...
    @classmethod
    def from_dict(cls, data: dict) -> "AnalysisRequest": ...
```

#### 1.2.2 output_schemas.py
```
测试文件: tests/unit/schemas/test_output_schemas.py
```

- [ ] **Test**: test_trend_analysis_creation
- [ ] **Test**: test_trend_analysis_score_bounds (1-100)
- [ ] **Test**: test_market_analysis_creation
- [ ] **Test**: test_competition_analysis_creation
- [ ] **Test**: test_profit_analysis_creation
- [ ] **Test**: test_evaluation_result_creation
- [ ] **Test**: test_final_report_creation
- [ ] **Test**: test_schemas_json_serializable
- [ ] **Impl**: 实现所有输出 dataclass
- [ ] **Impl**: 实现 JSON 序列化方法

```python
# 预期接口
@dataclass
class TrendAnalysis:
    trend_score: int  # 1-100
    trend_direction: str  # rising/stable/declining
    seasonality: Dict[str, Any]
    related_queries: List[Dict[str, str]]
    raw_data: Optional[Dict] = None

    def to_dict(self) -> dict: ...
    @classmethod
    def from_dict(cls, data: dict) -> "TrendAnalysis": ...

# 类似定义其他Schema...
```

#### 1.2.3 state_schemas.py
```
测试文件: tests/unit/schemas/test_state_schemas.py
```

- [ ] **Test**: test_analysis_state_creation
- [ ] **Test**: test_analysis_state_update
- [ ] **Test**: test_analysis_state_history_append
- [ ] **Test**: test_analysis_state_to_session_dict
- [ ] **Impl**: 实现 AnalysisState dataclass
- [ ] **Impl**: 实现状态更新方法

**Phase 1 验收标准:**
```bash
pytest tests/unit/config/ tests/unit/schemas/ -v
# 所有测试通过
```

---

## Phase 2: 工具层 (tools/)

### Task 2.1: 工具基类

#### 2.1.1 base_tool.py
```
测试文件: tests/unit/tools/test_base_tool.py
```

- [ ] **Test**: test_base_tool_interface
- [ ] **Test**: test_tool_input_validation
- [ ] **Test**: test_tool_error_handling
- [ ] **Impl**: 实现 BaseTool 抽象类
- [ ] **Impl**: 实现通用验证和错误处理

---

### Task 2.2: 趋势分析工具

#### 2.2.1 trend_tools.py
```
测试文件: tests/unit/tools/test_trend_tools.py
```

**函数: analyze_search_trends**
- [ ] **Test**: test_analyze_trends_valid_keywords
  - 输入有效关键词，返回趋势数据
- [ ] **Test**: test_analyze_trends_empty_keywords
  - 空关键词列表抛出异常
- [ ] **Test**: test_analyze_trends_max_keywords
  - 超过5个关键词截断或报错
- [ ] **Test**: test_analyze_trends_invalid_geo
  - 无效地区代码处理
- [ ] **Test**: test_analyze_trends_api_error
  - API错误时的降级处理
- [ ] **Impl**: 实现 analyze_search_trends 函数

**函数: calculate_trend_score**
- [ ] **Test**: test_trend_score_rising
  - 上升趋势得分高
- [ ] **Test**: test_trend_score_declining
  - 下降趋势得分低
- [ ] **Test**: test_trend_score_bounds
  - 得分在1-100范围
- [ ] **Impl**: 实现 calculate_trend_score 函数

**函数: detect_seasonality**
- [ ] **Test**: test_detect_seasonality_holiday
  - 检测节日季节性
- [ ] **Test**: test_detect_seasonality_none
  - 无明显季节性时返回合理结果
- [ ] **Impl**: 实现 detect_seasonality 函数

**函数: get_related_queries**
- [ ] **Test**: test_related_queries_returns_list
- [ ] **Test**: test_related_queries_structure
- [ ] **Impl**: 实现 get_related_queries 函数

```python
# 预期接口
def analyze_search_trends(
    keywords: List[str],
    geo: str = "US",
    timeframe: str = "today 12-m"
) -> Dict[str, Any]: ...

def calculate_trend_score(trend_data: Dict) -> int: ...

def detect_seasonality(trend_data: Dict) -> Dict[str, Any]: ...

def get_related_queries(keyword: str, geo: str = "US") -> List[Dict]: ...
```

---

### Task 2.3: 市场分析工具

#### 2.3.1 market_tools.py
```
测试文件: tests/unit/tools/test_market_tools.py
```

**函数: estimate_market_size**
- [ ] **Test**: test_estimate_market_size_structure
  - 返回TAM/SAM/SOM结构
- [ ] **Test**: test_estimate_market_size_positive
  - 所有值为正数
- [ ] **Test**: test_estimate_market_size_hierarchy
  - TAM >= SAM >= SOM
- [ ] **Impl**: 实现 estimate_market_size 函数

**函数: analyze_customer_segments**
- [ ] **Test**: test_customer_segments_non_empty
- [ ] **Test**: test_customer_segments_percentages
  - 百分比总和合理
- [ ] **Impl**: 实现 analyze_customer_segments 函数

**函数: assess_market_maturity**
- [ ] **Test**: test_maturity_levels
  - 返回有效的成熟度等级
- [ ] **Impl**: 实现 assess_market_maturity 函数

```python
# 预期接口
def estimate_market_size(
    category: str,
    market: str = "US"
) -> Dict[str, float]: ...
# 返回: {"tam": float, "sam": float, "som": float, "currency": "USD"}

def analyze_customer_segments(category: str) -> List[Dict]: ...
# 返回: [{"name": str, "percentage": float, "description": str}, ...]

def assess_market_maturity(market_data: Dict) -> str: ...
# 返回: "emerging" | "growing" | "mature" | "declining"
```

---

### Task 2.4: 竞争分析工具

#### 2.4.1 competition_tools.py
```
测试文件: tests/unit/tools/test_competition_tools.py
```

**函数: identify_competitors**
- [ ] **Test**: test_identify_competitors_returns_list
- [ ] **Test**: test_competitor_structure
  - 包含name, market_share, price_range等字段
- [ ] **Impl**: 实现 identify_competitors 函数

**函数: analyze_pricing_strategy**
- [ ] **Test**: test_pricing_analysis_structure
- [ ] **Test**: test_pricing_range_calculation
- [ ] **Impl**: 实现 analyze_pricing_strategy 函数

**函数: calculate_competition_score**
- [ ] **Test**: test_competition_score_bounds
  - 1-100范围
- [ ] **Test**: test_high_competition_scenario
- [ ] **Test**: test_low_competition_scenario
- [ ] **Impl**: 实现 calculate_competition_score 函数

**函数: find_market_gaps**
- [ ] **Test**: test_market_gaps_returns_list
- [ ] **Test**: test_market_gaps_non_empty_strings
- [ ] **Impl**: 实现 find_market_gaps 函数

```python
# 预期接口
def identify_competitors(
    category: str,
    market: str = "US"
) -> List[Dict]: ...

def analyze_pricing_strategy(competitors: List[Dict]) -> Dict: ...
# 返回: {"min_price": float, "max_price": float, "avg_price": float, "recommended_range": dict}

def calculate_competition_score(competition_data: Dict) -> int: ...

def find_market_gaps(competition_data: Dict) -> List[str]: ...
```

---

### Task 2.5: 利润计算工具 ⭐ (核心工具)

#### 2.5.1 profit_tools.py
```
测试文件: tests/unit/tools/test_profit_tools.py
```

**函数: calculate_unit_economics** (最重要)
- [ ] **Test**: test_unit_economics_basic_calculation
  - 基本计算正确性
- [ ] **Test**: test_unit_economics_all_costs_included
  - 包含所有成本项
- [ ] **Test**: test_unit_economics_zero_price
  - 零售价为0时处理
- [ ] **Test**: test_unit_economics_negative_margin
  - 负利润率场景
- [ ] **Test**: test_unit_economics_high_margin
  - 高利润率场景
- [ ] **Test**: test_unit_economics_custom_rates
  - 自定义费率参数
- [ ] **Impl**: 实现 calculate_unit_economics 函数

**函数: project_monthly_revenue**
- [ ] **Test**: test_monthly_projection_structure
- [ ] **Test**: test_monthly_projection_zero_units
- [ ] **Test**: test_monthly_projection_scaling
  - 线性缩放正确
- [ ] **Impl**: 实现 project_monthly_revenue 函数

**函数: calculate_roi**
- [ ] **Test**: test_roi_calculation
- [ ] **Test**: test_roi_zero_investment
- [ ] **Test**: test_roi_negative_profit
- [ ] **Impl**: 实现 calculate_roi 函数

**函数: assess_profitability**
- [ ] **Test**: test_profitability_excellent
  - 净利率>25%
- [ ] **Test**: test_profitability_good
  - 净利率15-25%
- [ ] **Test**: test_profitability_fair
  - 净利率10-15%
- [ ] **Test**: test_profitability_poor
  - 净利率<10%
- [ ] **Impl**: 实现 assess_profitability 函数

```python
# 预期接口
def calculate_unit_economics(
    selling_price: float,
    product_cost: float,
    shipping_cost: float,
    platform_fee_rate: float = 0.15,
    marketing_cost_rate: float = 0.20,
    return_rate: float = 0.05
) -> Dict[str, Any]: ...
# 返回完整的单位经济模型

def project_monthly_revenue(
    unit_economics: Dict,
    monthly_units: int
) -> Dict[str, float]: ...

def calculate_roi(
    unit_economics: Dict,
    initial_investment: float,
    monthly_units: int
) -> Dict[str, float]: ...

def assess_profitability(profit_data: Dict) -> Dict[str, Any]: ...
# 返回: {"profitable": bool, "rating": str, "recommendation": str}
```

**Phase 2 验收标准:**
```bash
pytest tests/unit/tools/ -v --cov=src/tools --cov-report=term-missing
# 所有测试通过，覆盖率 >= 90%
```

---

## Phase 3: Agent层 (agents/)

### Task 3.1: Agent工厂

#### 3.1.1 base_agent.py
```
测试文件: tests/unit/agents/test_base_agent.py
```

- [ ] **Test**: test_agent_factory_creates_llm_agent
- [ ] **Test**: test_agent_factory_binds_tools
- [ ] **Test**: test_agent_factory_sets_output_key
- [ ] **Test**: test_get_model_returns_configured_model
- [ ] **Impl**: 实现 AgentFactory 类

```python
# 预期接口
class AgentFactory:
    @staticmethod
    def create_llm_agent(
        name: str,
        instruction: str,
        tools: List[Callable] = None,
        output_key: str = None,
        description: str = None
    ) -> LlmAgent: ...

    @staticmethod
    def get_model() -> str: ...
```

---

### Task 3.2: 分析Agent实现

#### 3.2.1 trend_agent.py
```
测试文件: tests/unit/agents/test_trend_agent.py
```

- [ ] **Test**: test_create_trend_agent_returns_agent
- [ ] **Test**: test_trend_agent_has_tools
  - 包含trend_tools
- [ ] **Test**: test_trend_agent_output_key
  - output_key = "trend_analysis"
- [ ] **Test**: test_trend_agent_instruction_not_empty
- [ ] **Impl**: 实现 create_trend_agent 函数

#### 3.2.2 market_agent.py
```
测试文件: tests/unit/agents/test_market_agent.py
```

- [ ] **Test**: test_create_market_agent_returns_agent
- [ ] **Test**: test_market_agent_has_tools
- [ ] **Test**: test_market_agent_output_key
  - output_key = "market_analysis"
- [ ] **Impl**: 实现 create_market_agent 函数

#### 3.2.3 competition_agent.py
```
测试文件: tests/unit/agents/test_competition_agent.py
```

- [ ] **Test**: test_create_competition_agent_returns_agent
- [ ] **Test**: test_competition_agent_has_tools
- [ ] **Test**: test_competition_agent_output_key
  - output_key = "competition_analysis"
- [ ] **Impl**: 实现 create_competition_agent 函数

#### 3.2.4 profit_agent.py
```
测试文件: tests/unit/agents/test_profit_agent.py
```

- [ ] **Test**: test_create_profit_agent_returns_agent
- [ ] **Test**: test_profit_agent_has_tools
- [ ] **Test**: test_profit_agent_output_key
  - output_key = "profit_analysis"
- [ ] **Impl**: 实现 create_profit_agent 函数

#### 3.2.5 evaluator_agent.py
```
测试文件: tests/unit/agents/test_evaluator_agent.py
```

- [ ] **Test**: test_create_evaluator_agent_returns_agent
- [ ] **Test**: test_evaluator_agent_reads_state
  - 指令中引用其他分析结果
- [ ] **Test**: test_evaluator_agent_output_key
  - output_key = "evaluation_result"
- [ ] **Impl**: 实现 create_evaluator_agent 函数

#### 3.2.6 report_agent.py
```
测试文件: tests/unit/agents/test_report_agent.py
```

- [ ] **Test**: test_create_report_agent_returns_agent
- [ ] **Test**: test_report_agent_output_key
  - output_key = "final_report"
- [ ] **Impl**: 实现 create_report_agent 函数

**Phase 3 验收标准:**
```bash
pytest tests/unit/agents/ -v
# 所有测试通过
```

---

## Phase 4: 工作流层 (workflows/)

### Task 4.1: 分析流水线

#### 4.1.1 analysis_pipeline.py
```
测试文件: tests/integration/test_workflows.py
```

**并行分析阶段**
- [ ] **Test**: test_parallel_analysis_creates_parallel_agent
- [ ] **Test**: test_parallel_analysis_contains_four_agents
- [ ] **Test**: test_parallel_analysis_agent_names
- [ ] **Impl**: 实现 create_parallel_analysis 函数

**完整流水线**
- [ ] **Test**: test_pipeline_creates_sequential_agent
- [ ] **Test**: test_pipeline_execution_order
  - 并行 → 评估 → 报告
- [ ] **Test**: test_pipeline_state_propagation
  - 状态正确传递
- [ ] **Impl**: 实现 create_analysis_pipeline 函数

```python
# 预期接口
def create_parallel_analysis() -> ParallelAgent: ...

def create_analysis_pipeline() -> SequentialAgent: ...
```

---

### Task 4.2: 主协调器

#### 4.2.1 orchestrator.py
```
测试文件: tests/integration/test_orchestrator.py
```

- [ ] **Test**: test_orchestrator_creation
- [ ] **Test**: test_orchestrator_has_pipeline
- [ ] **Test**: test_orchestrator_parses_request
- [ ] **Test**: test_orchestrator_class_init
- [ ] **Test**: test_orchestrator_analyze_method
- [ ] **Impl**: 实现 create_orchestrator 函数
- [ ] **Impl**: 实现 ProductScoutOrchestrator 类

```python
# 预期接口
def create_orchestrator() -> LlmAgent: ...

class ProductScoutOrchestrator:
    def __init__(self, session_service, runner_service): ...
    async def analyze(self, request: AnalysisRequest) -> FinalReport: ...
```

**Phase 4 验收标准:**
```bash
pytest tests/integration/test_workflows.py tests/integration/test_orchestrator.py -v
# 所有测试通过
```

---

## Phase 5: 服务层 (services/)

### Task 5.1: Session管理服务

#### 5.1.1 session_service.py
```
测试文件: tests/unit/services/test_session_service.py
```

- [ ] **Test**: test_session_manager_init
- [ ] **Test**: test_create_analysis_session
- [ ] **Test**: test_get_session
- [ ] **Test**: test_update_session_state
- [ ] **Test**: test_get_analysis_history
- [ ] **Test**: test_session_not_found
- [ ] **Impl**: 实现 SessionManager 类

```python
# 预期接口
class SessionManager:
    def __init__(self, session_service): ...
    async def create_analysis_session(self, user_id: str, request: AnalysisRequest) -> Session: ...
    async def get_session(self, session_id: str) -> Session: ...
    async def update_session_state(self, session_id: str, key: str, value: Any) -> None: ...
    async def get_analysis_history(self, user_id: str) -> List[dict]: ...
```

---

### Task 5.2: Runner服务

#### 5.2.1 runner_service.py
```
测试文件: tests/unit/services/test_runner_service.py
```

- [ ] **Test**: test_analysis_runner_init
- [ ] **Test**: test_run_analysis_returns_events
- [ ] **Test**: test_run_analysis_sync_returns_string
- [ ] **Test**: test_runner_handles_errors
- [ ] **Impl**: 实现 AnalysisRunner 类

```python
# 预期接口
class AnalysisRunner:
    def __init__(self, agent, session_service): ...
    async def run_analysis(self, user_id: str, session_id: str, query: str) -> AsyncGenerator[Event, None]: ...
    async def run_analysis_sync(self, user_id: str, session_id: str, query: str) -> str: ...
```

---

### Task 5.3: 报告服务

#### 5.3.1 report_service.py
```
测试文件: tests/unit/services/test_report_service.py
```

- [ ] **Test**: test_to_markdown_format
- [ ] **Test**: test_to_markdown_contains_sections
- [ ] **Test**: test_to_json_format
- [ ] **Test**: test_to_html_format
- [ ] **Impl**: 实现 ReportFormatter 类

```python
# 预期接口
class ReportFormatter:
    @staticmethod
    def to_markdown(report: FinalReport) -> str: ...
    @staticmethod
    def to_json(report: FinalReport) -> dict: ...
    @staticmethod
    def to_html(report: FinalReport) -> str: ...
```

**Phase 5 验收标准:**
```bash
pytest tests/unit/services/ -v --cov=src/services
# 所有测试通过，覆盖率 >= 80%
```

---

## Phase 6: 接口层 (cli/api)

### Task 6.1: CLI接口

#### 6.1.1 cli/main.py
```
测试文件: tests/unit/cli/test_cli.py
```

- [ ] **Test**: test_cli_analyze_command
- [ ] **Test**: test_cli_analyze_with_options
- [ ] **Test**: test_cli_history_command
- [ ] **Test**: test_cli_help_output
- [ ] **Impl**: 实现 CLI 命令

```python
# 使用示例
# python -m src.cli.main analyze -c "portable blender" -m US
# python -m src.cli.main history -s session_123
```

---

### Task 6.2: API接口 (可选)

#### 6.2.1 api/main.py
```
测试文件: tests/unit/api/test_api.py
```

- [ ] **Test**: test_analyze_endpoint
- [ ] **Test**: test_analyze_validation_error
- [ ] **Test**: test_history_endpoint
- [ ] **Test**: test_health_check
- [ ] **Impl**: 实现 FastAPI 路由

**Phase 6 验收标准:**
```bash
# CLI测试
python -m src.cli.main analyze -c "test" -m US --dry-run

# API测试 (如果实现)
pytest tests/unit/api/ -v
```

---

## Phase 7: 集成测试 + E2E

### Task 7.1: Agent集成测试
```
测试文件: tests/integration/test_agents.py
```

- [ ] **Test**: test_trend_agent_with_real_tools
  - Agent能调用工具并返回结果
- [ ] **Test**: test_market_agent_integration
- [ ] **Test**: test_competition_agent_integration
- [ ] **Test**: test_profit_agent_integration
- [ ] **Test**: test_evaluator_agent_integration
  - 能读取其他Agent的输出

---

### Task 7.2: 工作流集成测试
```
测试文件: tests/integration/test_pipeline.py
```

- [ ] **Test**: test_parallel_agents_execute_concurrently
- [ ] **Test**: test_pipeline_state_flow
  - 状态在Agent间正确传递
- [ ] **Test**: test_pipeline_error_handling
  - 单个Agent失败不影响其他

---

### Task 7.3: E2E测试
```
测试文件: tests/e2e/test_full_flow.py
```

- [ ] **Test**: test_full_analysis_portable_blender
  - 完整分析"便携榨汁机"
- [ ] **Test**: test_full_analysis_smart_home
  - 完整分析"智能家居"
- [ ] **Test**: test_report_generation
  - 报告包含所有必要部分

**Phase 7 验收标准:**
```bash
pytest tests/integration/ tests/e2e/ -v
# 所有测试通过
```

---

## Phase 8: 文档 + 部署

### Task 8.1: 文档完善

- [ ] 8.1.1 完善 README.md
  - 项目介绍
  - 快速开始
  - 架构说明
  - 使用示例
- [ ] 8.1.2 添加架构图 (draw.io/mermaid)
- [ ] 8.1.3 编写 API 文档
- [ ] 8.1.4 编写部署指南

---

### Task 8.2: 部署准备

- [ ] 8.2.1 创建 Dockerfile
- [ ] 8.2.2 创建 cloudbuild.yaml
- [ ] 8.2.3 配置 Cloud Run 部署
- [ ] 8.2.4 测试部署流程
- [ ] 8.2.5 验证线上环境

---

### Task 8.3: 示例代码

- [ ] 8.3.1 创建 examples/quick_start.py
- [ ] 8.3.2 创建 examples/portable_blender_analysis.py
- [ ] 8.3.3 创建 examples/smart_home_analysis.py

**Phase 8 验收标准:**
```bash
# 本地运行示例
python examples/quick_start.py

# 部署测试
gcloud run deploy --source . --dry-run
```

---

## Phase 9: 优化 + 视频

### Task 9.1: 性能优化

- [ ] 9.1.1 分析并优化API调用
- [ ] 9.1.2 添加缓存机制（可选）
- [ ] 9.1.3 优化Prompt减少Token消耗

---

### Task 9.2: 质量提升

- [ ] 9.2.1 代码Review和重构
- [ ] 9.2.2 添加更多边界测试
- [ ] 9.2.3 完善错误处理
- [ ] 9.2.4 添加日志和监控

---

### Task 9.3: Demo视频

- [ ] 9.3.1 编写视频脚本
- [ ] 9.3.2 准备Demo数据
- [ ] 9.3.3 录制Demo视频（<3分钟）
- [ ] 9.3.4 上传YouTube

**视频内容大纲:**
1. Problem Statement (30秒)
2. Solution Overview (30秒)
3. Architecture (30秒)
4. Live Demo (60秒)
5. Results & Value (30秒)

---

## 任务检查清单汇总

### Phase 0: 项目初始化 (6项)
- [ ] 项目结构
- [ ] pyproject.toml
- [ ] requirements.txt
- [ ] 环境配置
- [ ] pytest配置
- [ ] Git初始化

### Phase 1: 基础层 (15项)
- [ ] settings.py (4测试 + 实现)
- [ ] prompts.py (3测试 + 实现)
- [ ] input_schemas.py (5测试 + 实现)
- [ ] output_schemas.py (8测试 + 实现)
- [ ] state_schemas.py (4测试 + 实现)

### Phase 2: 工具层 (35项)
- [ ] base_tool.py (3测试 + 实现)
- [ ] trend_tools.py (12测试 + 实现)
- [ ] market_tools.py (6测试 + 实现)
- [ ] competition_tools.py (8测试 + 实现)
- [ ] profit_tools.py (14测试 + 实现)

### Phase 3: Agent层 (20项)
- [ ] base_agent.py (4测试 + 实现)
- [ ] trend_agent.py (4测试 + 实现)
- [ ] market_agent.py (3测试 + 实现)
- [ ] competition_agent.py (3测试 + 实现)
- [ ] profit_agent.py (3测试 + 实现)
- [ ] evaluator_agent.py (3测试 + 实现)
- [ ] report_agent.py (2测试 + 实现)

### Phase 4: 工作流层 (10项)
- [ ] analysis_pipeline.py (5测试 + 实现)
- [ ] orchestrator.py (5测试 + 实现)

### Phase 5: 服务层 (14项)
- [ ] session_service.py (6测试 + 实现)
- [ ] runner_service.py (4测试 + 实现)
- [ ] report_service.py (4测试 + 实现)

### Phase 6: 接口层 (8项)
- [ ] cli/main.py (4测试 + 实现)
- [ ] api/main.py (4测试 + 实现)

### Phase 7: 集成测试 (8项)
- [ ] Agent集成测试 (5项)
- [ ] 工作流集成测试 (3项)
- [ ] E2E测试 (3项)

### Phase 8: 文档+部署 (10项)
- [ ] README.md
- [ ] 架构图
- [ ] API文档
- [ ] 部署指南
- [ ] Dockerfile
- [ ] Cloud Run配置
- [ ] 示例代码 (3项)

### Phase 9: 优化+视频 (8项)
- [ ] 性能优化 (3项)
- [ ] 质量提升 (4项)
- [ ] Demo视频

---

## 每日开发计划建议

| Day | 目标 | Tasks |
|-----|------|-------|
| Day 1 | 项目搭建 + 基础层 | Phase 0 + Phase 1 |
| Day 2 | 工具层 (上) | Task 2.1-2.3 |
| Day 3 | 工具层 (下) | Task 2.4-2.5 |
| Day 4 | Agent层 | Phase 3 |
| Day 5 | 工作流 + 服务层 | Phase 4 + Phase 5 |
| Day 6 | 接口层 + 集成测试 | Phase 6 + Phase 7 |
| Day 7 | 文档 + 部署 | Phase 8 |
| Day 8 | 优化 + 视频 | Phase 9 |

---

*文档版本: v1.0*
*创建日期: 2025-11-25*
