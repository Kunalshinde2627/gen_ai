
from typing import TypedDict, List, Dict, Any

from langgraph.graph import StateGraph, START, END


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


# 3. Approval Node
def approval_node(state: AgentState):
    print("\nApproval Required")
    print("Question:", state["question"])
    print("Proposed Answer:", state["answer"])

    approval = input("Approve this answer? (yes/no): ").strip().lower()

    return {
        "approved": approval == "yes"
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

# 6. Compile Graph
graph = builder.compile()


# 7. Run Graph
def run_graph(question: str):
    initial_state = {
        "question": question,
        "answer": "",
        "steps": [],
        "approved": False
    }

    return graph.invoke(initial_state)


if __name__ == "__main__":
    question = input("Ask TaxSaathi: ")

    result = run_graph(question)

    print("\nFinal Answer:", result["answer"])
