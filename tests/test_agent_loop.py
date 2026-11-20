
from unittest.mock import patch

from app.agent_loop import run_agent


def test_agent_new_regime_tax_calculation():
    result = run_agent(
        "Calculate tax on salary 10 lakh under new regime"
    )

    assert "taxable income" in result["answer"].lower()
    assert len(result["steps"]) == 1
    assert result["steps"][0]["tool"] == "new_regime_tax"


def test_agent_old_regime_tax_calculation():
    result = run_agent(
        "Calculate tax on salary 10 lakh under old regime"
    )

    assert "taxable income" in result["answer"].lower()
    assert result["steps"][0]["tool"] == "old_regime_tax"


def test_agent_regime_comparison():
    result = run_agent(
        "Compare old and new regimes for salary 10 lakh"
    )

    assert result["comparison"] is not None
    assert result["steps"][0]["tool"] == "compare_regimes"
    assert "New Regime tax" in result["answer"]


def test_agent_missing_salary():
    result = run_agent(
        "Calculate tax under new regime"
    )

    assert "salary" in result["answer"].lower()
    assert result["steps"] == []


def test_agent_missing_regime():
    result = run_agent(
        "Calculate tax on salary 10 lakh"
    )

    assert "specify" in result["answer"].lower()
    assert result["steps"] == []


@patch("app.agent_loop.answer_question")
def test_agent_general_question_uses_rag(mock_answer):
    mock_answer.return_value = {
        "answer": "You can file ITR online.",
        "citations": [],
    }

    result = run_agent("How can I file my income tax return?")

    assert result["answer"] == "You can file ITR online."
    assert result["steps"][0]["tool"] == "search_rules"
    mock_answer.assert_called_once()


@patch("app.agent_loop.answer_question")
def test_agent_rag_no_answer(mock_answer):
    from app.rag import NO_ANSWER

    mock_answer.return_value = {
        "answer": NO_ANSWER,
        "citations": [],
    }

    result = run_agent("Tell me something unknown")

    assert result["answer"] == NO_ANSWER
    assert result["citations"] == []
