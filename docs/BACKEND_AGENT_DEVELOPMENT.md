# DeerFlow 后端 Agent 开发完整指南

本文档详细介绍在 DeerFlow 项目中开发新 Agent 的完整流程。

## 目录

- [项目结构概览](#项目结构概览)
- [开发方式选择](#开发方式选择)
- [方式 A：配置驱动的子 Agent（推荐）](#方式-a配置驱动的子-agent推荐)
- [方式 B：完整自定义 Agent](#方式-b完整自定义-agent)
- [中间件开发](#中间件开发)
- [工具开发](#工具开发)
- [配置文件设置](#配置文件设置)
- [测试验证](#测试验证)
- [快速开始模板](#快速开始模板)

---

## 项目结构概览

```
backend/
├── packages/harness/deerflow/
│   ├── agents/              # Agent 核心
│   │   ├── lead_agent/      # 主 Agent
│   │   ├── middlewares/     # 中间件（14+ 个）
│   │   ├── factory.py       # SDK 工厂
│   │   └── thread_state.py  # 状态定义
│   ├── subagents/            # 子 Agent 系统
│   │   ├── builtins/         # 内置子 Agent
│   │   └── config.py         # 子 Agent 配置类
│   ├── tools/                # 工具系统
│   ├── config/               # 配置模块
│   └── mcp_servers/          # MCP 服务器
├── app/gateway/              # FastAPI 网关
└── langgraph.json            # LangGraph 配置
```

### 关键文件参考

| 功能 | 文件路径 |
|------|---------|
| 子 Agent 配置基类 | [backend/packages/harness/deerflow/subagents/config.py](../backend/packages/harness/deerflow/subagents/config.py) |
| 主 Agent 工厂 | [backend/packages/harness/deerflow/agents/lead_agent/agent.py](../backend/packages/harness/deerflow/agents/lead_agent/agent.py) |
| SDK 工厂 | [backend/packages/harness/deerflow/agents/factory.py](../backend/packages/harness/deerflow/agents/factory.py) |
| 中间件基类 | [backend/packages/harness/deerflow/agents/middlewares/base.py](../backend/packages/harness/deerflow/agents/middlewares/base.py) |
| 特性声明 | [backend/packages/harness/deerflow/agents/features.py](../backend/packages/harness/deerflow/agents/features.py) |
| 任务工具 | [backend/packages/harness/deerflow/tools/builtins/task_tool.py](../backend/packages/harness/deerflow/tools/builtins/task_tool.py) |
| Bash Agent 示例 | [backend/packages/harness/deerflow/subagents/builtins/bash_agent.py](../backend/packages/harness/deerflow/subagents/builtins/bash_agent.py) |
| 论文写作 Agent | [backend/packages/harness/deerflow/subagents/builtins/paper_draft_agent.py](../backend/packages/harness/deerflow/subagents/builtins/paper_draft_agent.py) |

---

## 开发方式选择

DeerFlow 支持 **两种 Agent 开发方式**：

### 方式 A：配置驱动的子 Agent（推荐）
- 最简单，只需配置 `SubagentConfig`
- 通过 `task_tool` 调用
- 适合特定领域的专业 Agent

### 方式 B：完整自定义 Agent
- 完全控制 Agent 逻辑
- 需要实现工厂函数
- 适合全新的 Agent 架构

---

## 方式 A：配置驱动的子 Agent（推荐）

### 步骤 1：创建子 Agent 配置文件

在 `backend/packages/harness/deerflow/subagents/builtins/` 下创建新文件：

```python
# my_specialist_agent.py
"""我的专业 Agent"""
from deerflow.subagents.config import SubagentConfig

MY_SPECIALIST_CONFIG = SubagentConfig(
    name="my-specialist",
    description="""何时使用此 Agent：简短描述触发场景""",
    system_prompt="""你是一个专业的 XXX 助手...

核心指令：
1. ...
2. ...
3. ...
""",
    tools=["tool1", "tool2"],  # 允许的工具，None 表示继承所有
    disallowed_tools=["task", "ask_clarification"],  # 禁止的工具
    model="inherit",  # 或指定模型名
    max_turns=50,
    timeout_seconds=900,
)
```

### SubagentConfig 字段说明

| 字段 | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| `name` | str | 是 | - | 唯一标识符 |
| `description` | str | 是 | - | 何时使用此 Agent 的描述 |
| `system_prompt` | str | 是 | - | 系统提示词 |
| `tools` | list[str] \| None | 否 | None | 允许的工具列表，None 表示继承所有 |
| `disallowed_tools` | list[str] \| None | 否 | ["task"] | 禁止的工具列表 |
| `model` | str | 否 | "inherit" | 使用的模型，'inherit' 表示继承父模型 |
| `max_turns` | int | 否 | 50 | 最大 Agent 轮数 |
| `timeout_seconds` | int | 否 | 900 | 最大执行时间（秒） |

### 步骤 2：注册子 Agent

在 `backend/packages/harness/deerflow/subagents/builtins/__init__.py` 中添加：

```python
from .my_specialist_agent import MY_SPECIALIST_CONFIG

BUILTIN_SUBAGENTS = [
    # ... 现有配置
    MY_SPECIALIST_CONFIG,
]
```

### 步骤 3：配置系统提示词（可选）

如果需要动态提示词，修改 `lead_agent/prompt.py` 添加说明。

### 示例：Bash Agent

参考 [bash_agent.py](../backend/packages/harness/deerflow/subagents/builtins/bash_agent.py)：

```python
BASH_AGENT_CONFIG = SubagentConfig(
    name="bash",
    description="""Command execution specialist for running bash commands in a separate context.

Use this subagent when:
- You need to run a series of related bash commands
- Terminal operations like git, npm, docker, etc.
- Command output is verbose and would clutter main context
- Build, test, or deployment operations

Do NOT use for simple single commands - use bash tool directly instead.""",
    system_prompt="""You are a bash command execution specialist. Execute the requested commands carefully and report results clearly.

<guidelines>
- Execute commands one at a time when they depend on each other
- Use parallel execution when commands are independent
- Report both stdout and stderr when relevant
- Handle errors gracefully and explain what went wrong
- Use absolute paths for file operations
- Be cautious with destructive operations (rm, overwrite, etc.)
</guidelines>

<output_format>
For each command or group of commands:
1. What was executed
2. The result (success/failure)
3. Relevant output (summarized if verbose)
4. Any errors or warnings
</output_format>

<working_directory>
You have access to the sandbox environment:
- User uploads: `/mnt/user-data/uploads`
- User workspace: `/mnt/user-data/workspace`
- Output files: `/mnt/user-data/outputs`
</working_directory>
""",
    tools=["bash", "ls", "read_file", "write_file", "str_replace"],
    disallowed_tools=["task", "ask_clarification", "present_files"],
    model="inherit",
    max_turns=30,
)
```

---

## 方式 B：完整自定义 Agent

### 步骤 1：定义 Agent 状态（如需要）

```python
# agents/my_agent/state.py
from typing import Annotated, NotRequired
from deerflow.agents.thread_state import AgentState, merge_artifacts

class MyAgentState(AgentState):
    my_field: NotRequired[str]
    my_list: Annotated[list[str], merge_artifacts]
```

### 步骤 2：创建 Agent 工厂函数

```python
# agents/my_agent/agent.py
from langgraph.graph import StateGraph
from langgraph.checkpoint.base import BaseCheckpointSaver
from deerflow.agents.factory import create_deerflow_agent
from deerflow.agents.features import RuntimeFeatures

def make_my_agent(config: RunnableConfig):
    """创建我的自定义 Agent"""
    # 1. 解析配置
    model_name = _resolve_model_name(config)

    # 2. 构建中间件
    middlewares = _build_middlewares(config)

    # 3. 获取工具
    tools = get_available_tools(config)

    # 4. 创建 Agent
    return create_deerflow_agent(
        model=model,
        tools=tools,
        system_prompt="我的系统提示词",
        features=RuntimeFeatures(
            sandbox=True,
            memory=False,
            subagent=True,
        ),
        checkpointer=checkpointer,
        middlewares=middlewares,
    )
```

### 步骤 3：配置 LangGraph

在 `backend/langgraph.json` 中添加：

```json
{
  "graphs": {
    "my_agent": "deerflow.agents.my_agent:make_my_agent"
  }
}
```

---

## 中间件开发

### 创建自定义中间件

```python
# agents/middlewares/my_middleware.py
from deerflow.agents.middlewares.base import AgentMiddleware

@Prev(SomeAnchorMiddleware)  # 或 @Next
class MyMiddleware(AgentMiddleware):
    """我的中间件描述"""

    async def enter(self, state: ThreadState, config: RunnableConfig):
        # 进入时执行
        pass

    async def exit(self, state: ThreadState, config: RunnableConfig, result):
        # 退出时执行
        pass
```

### 注册中间件

在 `agents/features.py` 的 `RuntimeFeatures` 中添加配置。

### 中间件执行顺序

```
ThreadDataMiddleware
  → UploadsMiddleware
    → SandboxMiddleware
      → DanglingToolCallMiddleware
        → [GuardrailMiddleware]
          → ToolErrorHandlingMiddleware
            → [SummarizationMiddleware]
              → [TodoMiddleware]
                → TitleMiddleware
                  → MemoryMiddleware
                    → [ViewImageMiddleware]
                      → [SubagentLimitMiddleware]
                        → LoopDetectionMiddleware
                          → ClarificationMiddleware
```

---

## 工具开发

### 创建自定义工具

```python
# tools/builtins/my_tool.py
from langchain_core.tools import tool

@tool
def my_tool(param: str) -> str:
    """工具描述"""
    return f"处理结果: {param}"
```

### 注册工具

在 `config.yaml` 中配置：

```yaml
tools:
  - name: my_tool
    use: deerflow.tools.builtins.my_tool:my_tool
    description: 我的工具
```

---

## 配置文件设置

### 主配置 `config.yaml`

```yaml
# 模型配置
models:
  - name: gpt-4
    display_name: GPT-4
    use: langchain_openai:ChatOpenAI
    model: gpt-4
    api_key: $OPENAI_API_KEY
    request_timeout: 600.0
    max_retries: 2
    max_tokens: 4096
    temperature: 0.7
    supports_vision: true
    supports_thinking: true

# 工具配置
tools:
  - name: my_tool
    use: deerflow.tools.builtins.my_tool:my_tool
    description: 我的工具

# 工具组
tool_groups:
  - name: my_tools
    tools: ["my_tool"]
```

---

## 测试验证

### 单元测试

```python
# tests/test_my_agent.py
from deerflow.subagents.builtins import MY_SPECIALIST_CONFIG

def test_my_agent_config():
    assert MY_SPECIALIST_CONFIG.name == "my-specialist"
```

### 集成测试

使用 FastAPI 测试客户端：

```python
from app.gateway.app import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_agent_run():
    response = client.post("/runs", json={...})
    assert response.status_code == 200
```

### 运行测试

```bash
# 运行所有测试
cd backend && make test

# 运行特定测试文件
cd backend && PYTHONPATH=. uv run pytest tests/test_my_agent.py -v
```

---

## 快速开始模板

复制以下模板创建新的子 Agent：

```python
"""我的专业 Agent 模板"""
from deerflow.subagents.config import SubagentConfig

MY_AGENT_CONFIG = SubagentConfig(
    name="my-agent",
    description="""何时使用此 Agent：当用户需要 XXX 时使用""",
    system_prompt="""你是一个专业的 XXX 助手。

核心能力：
1. 能力一
2. 能力二
3. 能力三

工作流程：
1. 先分析需求
2. 制定计划
3. 执行任务
4. 总结结果

注意事项：
- 注意一
- 注意二
""",
    tools=None,  # 继承所有工具
    disallowed_tools=["task", "ask_clarification", "present_files"],
    model="inherit",
    max_turns=50,
    timeout_seconds=900,
)
```

---

## 总结

大多数情况下，推荐使用 **方式 A（配置驱动的子 Agent）**，这是最快最简便的方式。只有在需要完全控制 Agent 逻辑时才使用方式 B。

开发完成后，确保：
1. 编写单元测试
2. 更新相关文档
3. 运行完整测试套件验证
