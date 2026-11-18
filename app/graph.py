
from typing import TypedDict, List, Dict, Any

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command


# 1. Define Graph State
class AgentState(TypedDict):
    question: str
    answer: str
    steps: List[Dict[str, Any]]
    approved: bool


# 2. Agent Node
def agent_node(state: AgentState):
    from app.agent_loop import run_agent

    result = run_agent(state["question"])

    return {
        "answer": result["answer"],
        "steps": result["steps"]
    }


# 3. Approval Node using interrupt()
def approval_node(state: AgentState):

    decision = interrupt({
        "message": "Approval Required",
        "question": state["question"],
        "proposed_answer": state["answer"]
    })

    return {
        "approved": decision is True or
                    str(decision).lower() == "yes"
    }


# 4. Final Node
def final_node(state: AgentState):

    if state["approved"]:
        return {
            "answer": state["answer"]
        }

    return {
        "answer": "Answer was not approved by the user."
    }


# 5. Build Graph
builder = StateGraph(AgentState)

builder.add_node("agent", agent_node)
builder.add_node("approval", approval_node)
builder.add_node("final", final_node)

builder.add_edge(START, "agent")
builder.add_edge("agent", "approval")
builder.add_edge("approval", "final")
builder.add_edge("final", END)


# 6. MemorySaver
memory = MemorySaver()


# 7. Compile Graph
graph = builder.compile(
    checkpointer=memory
)


# 8. Graph Configuration
def get_config(thread_id: str):

    return {
        "configurable": {
            "thread_id": thread_id
        }
    }


# 9. Start Graph
def run_graph(question: str, thread_id: str = "user_101"):

    initial_state = {
        "question": question,
        "answer": "",
        "steps": [],
        "approved": False
    }

    return graph.invoke(
        initial_state,
        config=get_config(thread_id)
    )


# 10. Resume Graph after Approval
def resume_graph(thread_id: str, approved: bool):

    return graph.invoke(
        Command(resume=approved),
        config=get_config(thread_id)
    )


# 11. Main Execution
if __name__ == "__main__":

    question = input("Ask TaxSaathi: ")

    thread_id = "user_101"

    result = run_graph(question, thread_id)

    if "__interrupt__" in result:

        print("\nApproval Required")
        print(result["__interrupt__"])

        approval = input("\nApprove? (yes/no): ").strip().lower()

        final_result = resume_graph(
            thread_id,
            approval == "yes"
        )

        print("\nFinal Answer:", final_result["answer"])
