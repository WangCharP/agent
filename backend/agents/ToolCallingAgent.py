"""
backend.agents.ToolCallingAgent 的 Docstring
负责任务调度的 agent
"""

from typing import List, Union, Callable, Dict, Any
from langchain_core.messages import SystemMessage, BaseMessage
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode, tools_condition

class ToolCallingAgent:
    def __init__(
        self, 
        model: BaseChatModel, 
        tools: List[BaseTool], 
        system_prompt: str = ""
    ):
        """
        初始化工具调用 Agent
        
        Args:
            model: 基础 LLM 模型 (如 ChatOpenAI)
            tools: 该 Agent 可用的工具列表
            system_prompt: 该 Agent 的系统提示词 (Persona)
        """
        self.system_prompt = system_prompt
        # 关键步骤：将工具绑定到 LLM
        self.model = model.bind_tools(tools)
        self.tools = tools
        # 创建工具执行节点 (LangGraph 预置)
        self.tool_node = ToolNode(tools)

    def get_node(self) -> Callable:
        """
        返回用于 Graph 的节点函数
        """
        def agent_node(state: Dict[str, Any]):
            messages = state["messages"]
            
            # 如果是第一次调用且有系统提示词，可以将其插入（视具体 State 结构而定）
            # 这里假设 State 是简单的 messages 列表，我们在调用模型前添加 SystemMessage
            # 注意：这不会修改全局 State 中的历史记录，只是本次调用的上下文
            prompt_messages = [SystemMessage(content=self.system_prompt)] + messages
            
            response = self.model.invoke(prompt_messages)
            
            # 返回更新的状态 (LangGraph 会自动 append 新消息)
            return {"messages": [response]}
            
        return agent_node

    def get_tool_node(self) -> Callable:
        """
        返回工具执行节点
        """
        return self.tool_node

    def get_tools(self) -> List[BaseTool]:
        return self.tools

# --- 使用示例 (伪代码，用于说明如何在 Graph 中组装) ---
# from langgraph.graph import StateGraph
# 
# # 1. 实例化
# researcher = ToolCallingAgent(llm, [search_tool], "你是研究员")
# 
# # 2. 添加节点
# workflow = StateGraph(AgentState)
# workflow.add_node("researcher_node", researcher.get_node())
# workflow.add_node("researcher_tools", researcher.get_tool_node())
# 
# # 3. 添加边和条件逻辑
# # 逻辑：Agent -> (决定调用工具?) -> ToolNode -> Agent
# workflow.add_edge("researcher_tools", "researcher_node") # 工具执行完回 Agent
# workflow.add_conditional_edges(
#     "researcher_node",
#     tools_condition, # LangGraph 预置函数，检测 last_message 是否有 tool_calls
#     {
#         "tools": "researcher_tools", # 如果有 tool_calls，去工具节点
#         END: END                     # 否则结束 (或返回 Supervisor)
#     }
# )