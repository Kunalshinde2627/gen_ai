
from typing import Any, TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt


class AgentState(TypedDict):
    question: str
    answer: str
    steps: list[dict[str, Any]]
    citations: list[dict[str, Any]]
    comparison: dict[str, Any] | None
    approved: bool


def agent_node(state):
    from app.agent_loop import run_agent

    result = run_agent(state["question"])

    return {
        "answer": result["answer"],
        "steps": result["steps"],
        "citations": result.get("citations", []),
        "comparison": result.get("comparison")
    }


def approval_node(state):

    decision = interrupt({
        "message": "Approval Required",
        "question": state["question"],
        "proposed_answer": state["answer"]
    })

    return {
        "approved": (
            decision is True
            or str(decision).lower() == "yes"
        )
    }


def final_node(state):

    if state["approved"]:

        return {
            "answer": state["answer"],
            "citations": state.get("citations", []),
            "comparison": state.get("comparison")
        }

    return {
        "answer": "Answer was not approved by the user.",
        "citations": [],
        "comparison": None
    }


builder = StateGraph(AgentState)

builder.add_node("agent", agent_node)
builder.add_node("approval", approval_node)
builder.add_node("final", final_node)

builder.add_edge(START, "agent")
builder.add_edge("agent", "approval")
builder.add_edge("approval", "final")
builder.add_edge("final", END)

memory = MemorySaver()

graph = builder.compile(
    checkpointer=memory
)


def get_config(thread_id):
    return {
        "configurable": {
            "thread_id": thread_id
        }
    }


def run_graph(question, thread_id="user_101"):

    initial_state = {
        "question": question,
        "answer": "",
        "steps": [],
        "citations": [],
        "comparison": None,
        "approved": False
    }

    return graph.invoke(
        initial_state,
        config=get_config(thread_id)
    )


def resume_graph(thread_id, approved):

    return graph.invoke(
        Command(resume=approved),
        config=get_config(thread_id)
    )
