# ADK 增强日志功能

## 概述

本文档描述了如何为 Google ADK (Agent Development Kit) 实现增强的日志功能，以捕获 4 个分析 Agent 的详细推理过程。

## 问题背景

**当前问题:**
- ADK 的 `ParallelAgent` 执行时，只能看到整体的事件流
- 无法区分哪个事件来自哪个 Agent (trend_agent, market_agent, competition_agent, profit_agent)
- 缺少每个 Agent 的详细推理过程记录
- 无法追踪工具调用 (Google Search) 的具体情况

## 解决方案

### 1. ADK 事件分析

通过分析 ADK 源码发现：

```python
# Runner.run() 返回 Event Generator
for event in parallel_runner.run(...):
    # Event 包含丰富信息:
    # - event.get_function_calls()      # 工具调用
    # - event.get_function_responses() # 工具响应
    # - event.is_final_response()     # 最终响应
    # - event.json()                  # 完整事件数据
```

### 2. 增强日志系统

创建了 `src/utils/adk_logging.py` 模块:

#### **ADKEventLogger 类**
- **事件分类**: 区分 tool_call, tool_response, content_response, final_response
- **Agent 识别**: 从工具调用参数和内容中推断 Agent 类型
- **详细记录**: 记录每个 Agent 的推理步骤、工具使用、结果
- **性能统计**: 记录执行时间、事件数量、Agent 统计

#### **核心功能**

1. **Agent 自动识别:**
```python
def _extract_agent_from_tools(self, tools):
    query = tools[0]['args']['query'].lower()
    if any(keyword in query for keyword in ['trend', 'search', 'volume']):
        return 'trend_agent'
    elif any(keyword in query for keyword in ['market', 'size', 'segment']):
        return 'market_agent'
    # ... 其他Agent
```

2. **详细事件日志:**
```
🤖 Event 1 [2.3s]: tool_call (Agent: trend_agent)
🔧 Tool Calls (trend_agent):
  1. google_search
     Args: {"query": "portable blender market trends 2024"}

📋 Tool Responses (market_agent):
  1. google_search
     Result: {"market_size": "$2.3B", "growth_rate": "8.5%"}

💭 Agent Reasoning (profit_agent):
     Length: 245 characters
     Preview: Based on market analysis and competition data, the portable...
```

3. **执行汇总:**
```
🎯 ADK EXECUTION SUMMARY
🏱️  Total execution time: 45.67s
🤖 Agents tracked: 4

--- TREND_AGENT ---
  Events: 3
  tool_call: 1
  tool_response: 1
  content_response: 1

--- MARKET_AGENT ---
  Events: 3
  tool_call: 1
  tool_response: 1
  content_response: 1
```

## 实现细节

### 1. 新增文件

**`src/utils/adk_logging.py`**
- ADKEventLogger 类
- 事件分类和 Agent 识别逻辑
- 详细日志格式化
- 执行统计和汇总

**`examples/adk_logging_demo.py`**
- 演示脚本
- 展示增强日志功能
- 手动事件模拟演示

### 2. 修改文件

**`src/workflows/runner.py`**
- 导入 ADK 日志模块
- 集成 ADKEventLogger 到并行执行流程
- 保持向后兼容的日志输出
- 增加执行结果解析

### 3. 核心修改

```python
# 新增的增强日志代码
from src.utils.adk_logging import create_adk_logger

# 在并行执行中
adk_logger = create_adk_logger(self.logger, debug_mode=True)

for event in parallel_runner.run(...):
    # 事件详细记录
    adk_logger.log_event(event, event_count)

    # 可选: 保持原有调试日志
    self.logger.debug(f"📨 Agent event {event_count}...")

# 执行汇总
adk_logger.log_summary()

# 提取 Agent 输出
agent_outputs = adk_logger.extract_agent_outputs()
for agent_name, output in agent_outputs.items():
    self.logger.info(f"🎯 {agent_name.upper()} OUTPUT CAPTURED:")
    self.logger.info(f"   Length: {len(output)} characters")
    self.logger.info(f"   Preview: {output[:200]}...")
```

## 使用效果

### 1. 实时 Agent 跟踪

现在可以在执行过程中看到每个 Agent 的详细活动:

```
📡 Starting detailed ADK event logging...
🤖 Event 1 [1.2s]: tool_call (Agent: trend_agent)
🔧 Tool Calls (trend_agent):
  1. google_search
     Args: {"query": "portable blender trends"}

🤖 Event 2 [3.1s]: tool_response (Agent: trend_agent)
📋 Tool Responses (trend_agent):
  1. google_search
     Result: Google Search results showing rising trend for portable blenders...

🤖 Event 3 [5.8s]: content_response (Agent: trend_agent)
💭 Agent Reasoning (trend_agent):
     Length: 342 characters
     Preview: The analysis reveals strong upward trend for portable blenders...
```

### 2. Agent 输出捕获

系统能够提取每个 Agent 的最终输出:

```
🎯 TREND_AGENT OUTPUT CAPTURED:
   Length: 567 characters
   Preview: {"trend_score": 85, "trend_direction": "rising", "seasonality": {"peak_months": [5, 6, 7], ...

🎯 MARKET_AGENT OUTPUT CAPTURED:
   Length: 423 characters
   Preview: {"market_score": 78, "market_size": {"tam": 5000000000, "sam": 1500000000, ...

🎯 COMPETITION_AGENT OUTPUT CAPTURED:
   Length: 389 characters
   Preview: {"competition_score": 65, "competitors": [{"name": "NutriBullet", ...

🎯 PROFIT_AGENT OUTPUT CAPTURED:
   Length: 456 characters
   Preview: {"profit_score": 72, "unit_economics": {"selling_price": 49.99, ...
```

### 3. 完整的执行时间线

提供详细的性能分析:

```
🏱️  Total execution time: 45.67s

🤖 Agents tracked: 4

--- TREND_AGENT ---
  Events: 3
  Execution window: 1.2s - 6.3s (5.1s duration)
  Tasks: search → analysis → response

--- MARKET_AGENT ---
  Events: 3
  Execution window: 1.5s - 8.7s (7.2s duration)
  Tasks: search → analysis → response

--- COMPETITION_AGENT ---
  Events: 3
  Execution window: 1.8s - 9.2s (7.4s duration)
  Tasks: search → analysis → response

--- PROFIT_AGENT ---
  Events: 3
  Execution window: 2.1s - 12.4s (10.3s duration)
  Tasks: search → analysis → response
```

## 配置选项

### 1. 调试级别控制

```python
# 启用详细调试日志
adk_logger = create_adk_logger(base_logger, debug_mode=True)

# 仅关键信息日志
adk_logger = create_adk_logger(base_logger, debug_mode=False)
```

### 2. 日志级别设置

```python
# 在 analysis_service.py 中
logger = setup_logger("product_scout", level=logging.DEBUG)  # 详细日志
logger = setup_logger("product_scout", level=logging.INFO)   # 正常日志
```

## 扩展建议

### 1. 结果解析自动化

当前需要实现 TODO 部分:
```python
# 在 runner.py 中实现
if agent_outputs.get('trend_agent'):
    state.trend_analysis = parse_trend_result(agent_outputs['trend_agent'])
if agent_outputs.get('market_agent'):
    state.market_analysis = parse_market_result(agent_outputs['market_agent'])
# ...
```

### 2. 实时 UI 更新

可以将详细日志转发到 UI 进度回调:
```python
def on_progress(phase: str, message: str):
    if agent_logger:
        # 发送详细 Agent 状态
        agent_events = agent_logger.get_agent_timeline(phase)
        # 更新 UI 显示每个 Agent 的状态
```

### 3. 日志持久化

将详细的 Agent 执行记录保存到数据库:
```python
# 保存每个 Agent 的完整推理过程
for agent_name, timeline in agent_logger.agent_events.items():
    save_agent_execution_log(
        agent_name=agent_name,
        events=timeline,
        timestamp=datetime.now(),
        request=request
    )
```

## 总结

通过这套增强的日志系统，现在可以:

✅ **完全覆盖 4 个 Agent 的推理过程**
✅ **实时跟踪每个 Agent 的工具调用**
✅ **捕获每个 Agent 的详细输出**
✅ **提供精确的性能分析**
✅ **支持调试和问题诊断**
✅ **保持向后兼容性**

这个解决方案充分利用了 ADK 的事件机制，通过智能的事件分析和 Agent 识别，实现了对多 Agent 系统的全面可观测性。