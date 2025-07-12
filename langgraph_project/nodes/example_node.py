from langchain_core.messages import SystemMessage, HumanMessage
from ..llm_config import llm
from ..state import AgentState


def planner_node(state: AgentState):
    """
    This node acts as the "Manager". It takes the initial user task
    and creates a plan for the other agents to follow.
    """
    print("---PLANNING---")
    messages = [
        SystemMessage(content="You are an expert project planner. Create a simple, step-by-step plan to accomplish the user's task. Your plan should be clear and concise."),
        HumanMessage(content=state['task'])
    ]
    response = llm.invoke(messages)
    return {"plan": response.content}


def researcher_node(state: AgentState):
    """
    This node acts as the "Researcher". It takes the plan
    and researches the topic.
    (For this starter, it will just generate a placeholder draft).
    """
    print("---RESEARCHING---")
    messages = [
        SystemMessage(content="You are a world-class researcher. Based on the following plan, research the topic and provide a detailed summary of your findings."),
        HumanMessage(content=state['plan'])
    ]
    response = llm.invoke(messages)
    return {"draft": response.content}


def writer_node(state: AgentState):
    """
    This node acts as the "Writer". It takes the research draft
    and writes the final report.
    """
    print("---WRITING---")
    messages = [
        SystemMessage(content="You are an expert technical writer. Take the following research draft and write a polished, final report."),
        HumanMessage(content=state['draft'])
    ]
    response = llm.invoke(messages)
    return {"review": response.content}
