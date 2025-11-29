# ProductScout AI - 代码架构设计

## 1. 项目目录结构

```
product_scout_ai/
│
├── README.md                          # 项目说明文档
├── CODE_ARCHITECTURE.md               # 本文档 - 代码架构说明
├── DEVELOPMENT_TODOLIST.md            # 开发任务清单
├── pyproject.toml                     # Python项目配置
├── requirements.txt                   # 依赖清单
├── .env.example                       # 环境变量示例
├── .gitignore                         # Git忽略文件
│
├── src/                               # 源代码目录
│   ├── __init__.py
│   │
│   ├── config/                        # 配置模块
│   │   ├── __init__.py
│   │   ├── settings.py                # 应用配置
│   │   └── prompts.py                 # Prompt模板集中管理
│   │
│   ├── schemas/                       # 数据模型
│   │   ├── __init__.py
│   │   ├── input_schemas.py           # 输入数据模型
│   │   ├── output_schemas.py          # 输出数据模型
│   │   └── state_schemas.py           # Session状态模型
│   │
│   ├── tools/                         # 自定义工具
│   │   ├── __init__.py
│   │   ├── base_tool.py               # 工具基类
│   │   ├── trend_tools.py             # 趋势分析工具
│   │   ├── market_tools.py            # 市场分析工具
│   │   ├── competition_tools.py       # 竞争分析工具
│   │   └── profit_tools.py            # 利润计算工具
│   │
│   ├── agents/                        # Agent模块
│   │   ├── __init__.py
│   │   ├── base_agent.py              # Agent基类/工厂
│   │   ├── trend_agent.py             # 趋势分析Agent
│   │   ├── market_agent.py            # 市场分析Agent
│   │   ├── competition_agent.py       # 竞争分析Agent
│   │   ├── profit_agent.py            # 利润评估Agent
│   │   ├── evaluator_agent.py         # 综合评估Agent
│   │   └── report_agent.py            # 报告生成Agent
│   │
│   ├── workflows/                     # 工作流编排
│   │   ├── __init__.py
│   │   ├── analysis_pipeline.py       # 分析流水线
│   │   └── orchestrator.py            # 主协调器
│   │
│   ├── services/                      # 服务层
│   │   ├── __init__.py
│   │   ├── session_service.py         # Session管理服务
│   │   ├── runner_service.py          # Runner服务封装
│   │   └── report_service.py          # 报告生成服务
│   │
│   ├── api/                           # API层（可选）
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI入口
│   │   └── routes.py                  # API路由
│   │
│   └── cli/                           # 命令行接口
│       ├── __init__.py
│       └── main.py                    # CLI入口
│
├── tests/                             # 测试目录
│   ├── __init__.py
│   ├── conftest.py                    # Pytest配置和fixtures
│   │
│   ├── unit/                          # 单元测试
│   │   ├── __init__.py
│   │   ├── tools/                     # 工具测试
│   │   │   ├── test_trend_tools.py
│   │   │   ├── test_market_tools.py
│   │   │   ├── test_competition_tools.py
│   │   │   └── test_profit_tools.py
│   │   ├── schemas/                   # Schema测试
│   │   │   └── test_schemas.py
│   │   └── services/                  # 服务测试
│   │       └── test_services.py
│   │
│   ├── integration/                   # 集成测试
│   │   ├── __init__.py
│   │   ├── test_agents.py             # Agent集成测试
│   │   ├── test_workflows.py          # 工作流测试
│   │   └── test_pipeline.py           # 端到端流水线测试
│   │
│   └── fixtures/                      # 测试数据
│       ├── sample_inputs.json
│       ├── mock_trend_data.json
│       └── expected_outputs.json
│
├── examples/                          # 示例代码
│   ├── quick_start.py                 # 快速开始示例
│   ├── smart_home_analysis.py         # 智能家居分析示例
│   └── portable_blender_analysis.py   # 便携榨汁机分析示例
│
├── scripts/                           # 脚本工具
│   ├── setup.sh                       # 环境安装脚本
│   └── deploy.sh                      # 部署脚本
│
└── docs/                              # 文档
    ├── api_reference.md               # API参考
    ├── deployment.md                  # 部署指南
    └── images/                        # 架构图等
        └── architecture.png
```

---

## 2. 模块职责说明

### 2.1 配置层 (config/)

#### `settings.py`
**职责**: 集中管理所有配置项

```python
# 核心配置项
- GOOGLE_API_KEY: Gemini API密钥
- MODEL_NAME: 使用的模型名称 (gemini-2.0-flash)
- APP_NAME: 应用名称
- SESSION_TTL: Session过期时间
- MAX_RETRIES: API重试次数
- LOG_LEVEL: 日志级别
```

**依赖**: 无
**被依赖**: 几乎所有模块

#### `prompts.py`
**职责**: 集中管理所有Agent的Prompt模板

```python
# Prompt模板
- TREND_AGENT_INSTRUCTION: 趋势分析Agent指令
- MARKET_AGENT_INSTRUCTION: 市场分析Agent指令
- COMPETITION_AGENT_INSTRUCTION: 竞争分析Agent指令
- PROFIT_AGENT_INSTRUCTION: 利润评估Agent指令
- EVALUATOR_AGENT_INSTRUCTION: 综合评估Agent指令
- REPORT_AGENT_INSTRUCTION: 报告生成Agent指令
```

**依赖**: 无
**被依赖**: agents/

---

### 2.2 数据模型层 (schemas/)

#### `input_schemas.py`
**职责**: 定义用户输入的数据模型

```python
@dataclass
class AnalysisRequest:
    category: str              # 产品品类
    target_market: str         # 目标市场 (US, EU, etc.)
    budget_range: str          # 预算范围 (low/medium/high)
    business_model: str        # 业务模式 (amazon_fba, dropshipping, etc.)
    keywords: List[str]        # 关键词列表

@dataclass
class UserPreferences:
    risk_tolerance: str        # 风险承受度
    min_margin: float          # 最低利润率要求
    preferred_categories: List[str]
```

**测试要点**: 输入验证、默认值、边界条件

#### `output_schemas.py`
**职责**: 定义各Agent的输出数据模型

```python
@dataclass
class TrendAnalysis:
    trend_score: int           # 1-100
    trend_direction: str       # rising/stable/declining
    seasonality: dict
    related_queries: List[dict]

@dataclass
class MarketAnalysis:
    market_size: dict          # TAM/SAM/SOM
    growth_rate: float
    customer_segments: List[dict]
    maturity_level: str

@dataclass
class CompetitionAnalysis:
    competitors: List[dict]
    competition_score: int     # 1-100
    pricing_analysis: dict
    opportunities: List[str]

@dataclass
class ProfitAnalysis:
    unit_economics: dict
    margins: dict
    monthly_projection: dict
    assessment: dict

@dataclass
class EvaluationResult:
    opportunity_score: int     # 1-100
    swot_analysis: dict
    recommendation: str        # go/no-go/cautious
    key_risks: List[str]
    success_factors: List[str]

@dataclass
class FinalReport:
    summary: str
    trend_analysis: TrendAnalysis
    market_analysis: MarketAnalysis
    competition_analysis: CompetitionAnalysis
    profit_analysis: ProfitAnalysis
    evaluation: EvaluationResult
    action_items: List[str]
```

**测试要点**: 序列化/反序列化、字段验证

#### `state_schemas.py`
**职责**: 定义Session状态结构

```python
@dataclass
class AnalysisState:
    request: AnalysisRequest
    trend_analysis: Optional[TrendAnalysis]
    market_analysis: Optional[MarketAnalysis]
    competition_analysis: Optional[CompetitionAnalysis]
    profit_analysis: Optional[ProfitAnalysis]
    evaluation_result: Optional[EvaluationResult]
    analysis_history: List[dict]
    created_at: datetime
    updated_at: datetime
```

**测试要点**: 状态更新、历史记录

---

### 2.3 工具层 (tools/)

#### `base_tool.py`
**职责**: 工具基类，提供通用功能

```python
class BaseTool:
    - name: str
    - description: str
    - async execute(**kwargs) -> dict
    - validate_input(**kwargs) -> bool
    - handle_error(error) -> dict
```

#### `trend_tools.py`
**职责**: 趋势分析相关工具

```python
# 工具函数
def analyze_search_trends(keywords: List[str], geo: str, timeframe: str) -> dict
    """分析Google搜索趋势"""

def get_related_queries(keyword: str, geo: str) -> List[dict]
    """获取相关搜索词"""

def detect_seasonality(trend_data: dict) -> dict
    """检测季节性模式"""

def calculate_trend_score(trend_data: dict) -> int
    """计算趋势得分"""
```

**输入**: 关键词列表、地区、时间范围
**输出**: 趋势数据字典
**测试要点**: Mock API响应、边界条件、错误处理

#### `market_tools.py`
**职责**: 市场分析相关工具

```python
def estimate_market_size(category: str, market: str) -> dict
    """估算市场规模 (TAM/SAM/SOM)"""

def analyze_customer_segments(category: str) -> List[dict]
    """分析目标客户群体"""

def assess_market_maturity(market_data: dict) -> str
    """评估市场成熟度"""
```

**测试要点**: 估算逻辑、数据解析

#### `competition_tools.py`
**职责**: 竞争分析相关工具

```python
def identify_competitors(category: str, market: str) -> List[dict]
    """识别主要竞争对手"""

def analyze_pricing_strategy(competitors: List[dict]) -> dict
    """分析定价策略"""

def calculate_competition_score(competition_data: dict) -> int
    """计算竞争强度得分"""

def find_market_gaps(competition_data: dict) -> List[str]
    """发现市场空白"""
```

**测试要点**: 数据聚合、得分计算

#### `profit_tools.py`
**职责**: 利润计算相关工具

```python
def calculate_unit_economics(
    selling_price: float,
    product_cost: float,
    shipping_cost: float,
    platform_fee_rate: float,
    marketing_cost_rate: float,
    return_rate: float
) -> dict
    """计算单位经济模型"""

def project_monthly_revenue(
    unit_economics: dict,
    monthly_units: int
) -> dict
    """预测月度收入"""

def calculate_roi(
    unit_economics: dict,
    initial_investment: float,
    monthly_units: int
) -> dict
    """计算投资回报率"""

def assess_profitability(profit_data: dict) -> dict
    """评估盈利能力"""
```

**测试要点**: 数学计算准确性、边界条件（零值、负值）

---

### 2.4 Agent层 (agents/)

#### `base_agent.py`
**职责**: Agent工厂和基础配置

```python
from google.adk.agents import LlmAgent

class AgentFactory:
    @staticmethod
    def create_llm_agent(
        name: str,
        instruction: str,
        tools: List = None,
        output_key: str = None,
        description: str = None
    ) -> LlmAgent:
        """创建标准LlmAgent"""

    @staticmethod
    def get_model() -> str:
        """获取配置的模型名称"""
```

#### `trend_agent.py`
**职责**: 趋势分析Agent

```python
def create_trend_agent() -> LlmAgent:
    """
    创建趋势分析Agent

    功能:
    - 分析搜索趋势
    - 识别季节性模式
    - 发现相关机会

    输出key: trend_analysis
    """
```

**工具依赖**: trend_tools, google_search
**输出**: TrendAnalysis

#### `market_agent.py`
**职责**: 市场分析Agent

```python
def create_market_agent() -> LlmAgent:
    """
    创建市场分析Agent

    功能:
    - 估算市场规模
    - 分析客户群体
    - 评估市场成熟度

    输出key: market_analysis
    """
```

**工具依赖**: market_tools, google_search
**输出**: MarketAnalysis

#### `competition_agent.py`
**职责**: 竞争分析Agent

```python
def create_competition_agent() -> LlmAgent:
    """
    创建竞争分析Agent

    功能:
    - 识别竞争对手
    - 分析定价策略
    - 发现差异化机会

    输出key: competition_analysis
    """
```

**工具依赖**: competition_tools, google_search
**输出**: CompetitionAnalysis

#### `profit_agent.py`
**职责**: 利润评估Agent

```python
def create_profit_agent() -> LlmAgent:
    """
    创建利润评估Agent

    功能:
    - 计算利润率
    - 分析成本结构
    - 预测ROI

    输出key: profit_analysis
    """
```

**工具依赖**: profit_tools
**输出**: ProfitAnalysis

#### `evaluator_agent.py`
**职责**: 综合评估Agent

```python
def create_evaluator_agent() -> LlmAgent:
    """
    创建综合评估Agent

    功能:
    - 综合各维度分析
    - 计算机会得分
    - 生成SWOT分析
    - 提供Go/No-Go建议

    输入: 读取state中的四个分析结果
    输出key: evaluation_result
    """
```

**依赖**: 无额外工具，读取state
**输出**: EvaluationResult

#### `report_agent.py`
**职责**: 报告生成Agent

```python
def create_report_agent() -> LlmAgent:
    """
    创建报告生成Agent

    功能:
    - 汇总所有分析结果
    - 生成结构化报告
    - 提供行动建议

    输入: 读取state中的所有分析结果
    输出key: final_report
    """
```

**输出**: Markdown格式报告

---

### 2.5 工作流层 (workflows/)

#### `analysis_pipeline.py`
**职责**: 构建分析流水线

```python
from google.adk.agents import SequentialAgent, ParallelAgent

def create_parallel_analysis() -> ParallelAgent:
    """
    创建并行分析阶段

    同时执行:
    - trend_agent
    - market_agent
    - competition_agent
    - profit_agent
    """

def create_analysis_pipeline() -> SequentialAgent:
    """
    创建完整分析流水线

    执行顺序:
    1. ParallelAnalysis (4个Agent并行)
    2. EvaluatorAgent (综合评估)
    3. ReportAgent (报告生成)
    """
```

#### `orchestrator.py`
**职责**: 主协调器

```python
def create_orchestrator() -> LlmAgent:
    """
    创建主协调Agent

    功能:
    - 解析用户请求
    - 提取分析参数
    - 调度分析流水线
    - 返回最终报告
    """

class ProductScoutOrchestrator:
    def __init__(self, session_service, runner_service):
        self.session_service = session_service
        self.runner_service = runner_service
        self.agent = create_orchestrator()

    async def analyze(self, request: AnalysisRequest) -> FinalReport:
        """执行完整分析流程"""
```

---

### 2.6 服务层 (services/)

#### `session_service.py`
**职责**: Session管理封装

```python
class SessionManager:
    def __init__(self, session_service):
        self.service = session_service

    async def create_analysis_session(
        self, user_id: str, request: AnalysisRequest
    ) -> Session:
        """创建分析会话"""

    async def get_session(self, session_id: str) -> Session:
        """获取会话"""

    async def update_session_state(
        self, session_id: str, key: str, value: Any
    ) -> None:
        """更新会话状态"""

    async def get_analysis_history(self, user_id: str) -> List[dict]:
        """获取用户的分析历史"""
```

#### `runner_service.py`
**职责**: Runner执行封装

```python
class AnalysisRunner:
    def __init__(self, agent, session_service):
        self.runner = Runner(
            agent=agent,
            app_name=settings.APP_NAME,
            session_service=session_service
        )

    async def run_analysis(
        self, user_id: str, session_id: str, query: str
    ) -> AsyncGenerator[Event, None]:
        """执行分析并返回事件流"""

    async def run_analysis_sync(
        self, user_id: str, session_id: str, query: str
    ) -> str:
        """同步执行分析并返回最终结果"""
```

#### `report_service.py`
**职责**: 报告格式化服务

```python
class ReportFormatter:
    @staticmethod
    def to_markdown(report: FinalReport) -> str:
        """转换为Markdown格式"""

    @staticmethod
    def to_json(report: FinalReport) -> dict:
        """转换为JSON格式"""

    @staticmethod
    def to_html(report: FinalReport) -> str:
        """转换为HTML格式"""
```

---

### 2.7 接口层

#### `cli/main.py`
**职责**: 命令行接口

```python
import click

@click.group()
def cli():
    """ProductScout AI - 智能选品分析工具"""

@cli.command()
@click.option('--category', '-c', required=True, help='产品品类')
@click.option('--market', '-m', default='US', help='目标市场')
@click.option('--budget', '-b', default='medium', help='预算范围')
def analyze(category, market, budget):
    """执行产品机会分析"""

@cli.command()
@click.option('--session-id', '-s', required=True, help='会话ID')
def history(session_id):
    """查看分析历史"""
```

#### `api/main.py`
**职责**: FastAPI接口（可选）

```python
from fastapi import FastAPI

app = FastAPI(title="ProductScout AI API")

@app.post("/analyze")
async def analyze_opportunity(request: AnalysisRequest):
    """执行产品机会分析"""

@app.get("/history/{user_id}")
async def get_history(user_id: str):
    """获取分析历史"""
```

---

## 3. 模块依赖关系图

```
                                    ┌─────────────┐
                                    │   config/   │
                                    │  settings   │
                                    │  prompts    │
                                    └──────┬──────┘
                                           │
                    ┌──────────────────────┼──────────────────────┐
                    │                      │                      │
                    ▼                      ▼                      ▼
            ┌───────────────┐      ┌───────────────┐      ┌───────────────┐
            │   schemas/    │      │    tools/     │      │   services/   │
            │ input_schemas │      │ trend_tools   │      │session_service│
            │output_schemas │      │ market_tools  │      │runner_service │
            │ state_schemas │      │competition_..│      │report_service │
            └───────┬───────┘      │ profit_tools  │      └───────┬───────┘
                    │              └───────┬───────┘              │
                    │                      │                      │
                    │              ┌───────▼───────┐              │
                    │              │    agents/    │              │
                    └─────────────►│ trend_agent   │◄─────────────┘
                                   │ market_agent  │
                                   │competition_.. │
                                   │ profit_agent  │
                                   │evaluator_agent│
                                   │ report_agent  │
                                   └───────┬───────┘
                                           │
                                   ┌───────▼───────┐
                                   │  workflows/   │
                                   │analysis_pipe..│
                                   │ orchestrator  │
                                   └───────┬───────┘
                                           │
                          ┌────────────────┼────────────────┐
                          │                │                │
                          ▼                ▼                ▼
                   ┌───────────┐    ┌───────────┐    ┌───────────┐
                   │  cli/     │    │   api/    │    │ examples/ │
                   │  main.py  │    │  main.py  │    │           │
                   └───────────┘    └───────────┘    └───────────┘
```

---

## 4. 测试策略

### 4.1 测试分层

```
┌─────────────────────────────────────────────────────────────┐
│                     E2E Tests (端到端测试)                   │
│         完整流程测试：用户输入 → 最终报告                     │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                Integration Tests (集成测试)                  │
│    - Agent集成测试（Agent + Tools）                         │
│    - 工作流测试（Pipeline执行）                             │
│    - 服务集成测试                                           │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                   Unit Tests (单元测试)                      │
│    - Tools函数测试                                          │
│    - Schema验证测试                                         │
│    - 服务方法测试                                           │
│    - 工具函数测试                                           │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 测试覆盖要求

| 模块 | 覆盖率目标 | 重点测试 |
|------|-----------|----------|
| tools/ | 90%+ | 计算准确性、边界条件、错误处理 |
| schemas/ | 80%+ | 数据验证、序列化 |
| agents/ | 70%+ | Agent创建、工具绑定 |
| workflows/ | 80%+ | 流水线执行顺序、状态传递 |
| services/ | 80%+ | Session管理、Runner执行 |

### 4.3 Mock策略

```python
# tests/conftest.py

@pytest.fixture
def mock_google_search():
    """Mock Google Search API响应"""

@pytest.fixture
def mock_trend_data():
    """Mock趋势数据"""

@pytest.fixture
def mock_llm_response():
    """Mock LLM响应"""

@pytest.fixture
def sample_analysis_request():
    """示例分析请求"""
```

---

## 5. 关键设计决策

### 5.1 为什么使用分层架构？

1. **可测试性**: 每层可独立测试，不依赖外部服务
2. **可维护性**: 职责清晰，修改影响范围可控
3. **可扩展性**: 添加新Agent/Tool只需在对应层添加

### 5.2 为什么集中管理Prompts？

1. **版本控制**: Prompt变更可追踪
2. **A/B测试**: 便于对比不同Prompt效果
3. **复用性**: 共享Prompt片段

### 5.3 为什么使用Schema定义数据结构？

1. **类型安全**: 运行时数据验证
2. **文档化**: Schema即文档
3. **序列化**: 统一的JSON转换

### 5.4 错误处理策略

```python
# 统一错误处理
class ProductScoutError(Exception):
    """基础异常类"""

class ToolExecutionError(ProductScoutError):
    """工具执行错误"""

class AgentError(ProductScoutError):
    """Agent错误"""

class ValidationError(ProductScoutError):
    """数据验证错误"""
```

---

## 6. 性能考虑

### 6.1 并行执行

- 4个分析Agent并行执行，减少总耗时
- 预计单次分析耗时：30-60秒

### 6.2 缓存策略

```python
# 可考虑的缓存点
- 搜索趋势数据（TTL: 1小时）
- 竞品信息（TTL: 24小时）
- 市场规模估算（TTL: 7天）
```

### 6.3 限流保护

```python
# API调用限流
- Google Search: 10 QPS
- Gemini API: 根据配额
```

---

*文档版本: v1.0*
*最后更新: 2025-11-25*
