
import json
import os
import uuid
from pathlib import Path

import requests
import streamlit as st

st.set_page_config(
    page_title="TaxSaathi - AI Tax Assistant",
    page_icon="💰",
    layout="wide"
)

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/agent")
FEEDBACK_FILE = Path("data/feedback.json")

st.title("💰 TaxSaathi")
st.caption("Your AI-powered Income Tax Assistant")

st.divider()


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "pending_approval" not in st.session_state:
    st.session_state.pending_approval = None


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def format_rupees(amount):
    """Format an amount in Indian Rupees."""
    try:
        return f"₹{float(amount):,.0f}"
    except (TypeError, ValueError):
        return "₹0"


def save_feedback(message_id, feedback):
    """Save feedback to JSON file."""

    FEEDBACK_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    if FEEDBACK_FILE.exists():
        try:
            with open(FEEDBACK_FILE, "r", encoding="utf-8") as file:
                feedback_data = json.load(file)

            if not isinstance(feedback_data, list):
                feedback_data = []

        except (json.JSONDecodeError, OSError):
            feedback_data = []
    else:
        feedback_data = []

    # Keep only the latest feedback for each message.
    feedback_data = [
        item for item in feedback_data
        if item.get("message_id") != message_id
    ]

    feedback_data.append({
        "message_id": message_id,
        "feedback": feedback,
        "thread_id": st.session_state.thread_id
    })

    with open(FEEDBACK_FILE, "w", encoding="utf-8") as file:
        json.dump(
            feedback_data,
            file,
            indent=4
        )


def display_sources(sources):
    """Display source titles and clickable URLs."""

    if not sources:
        return

    with st.expander("📚 Sources / References"):
        for index, source in enumerate(sources, start=1):

            if isinstance(source, str):
                st.markdown(f"{index}. [{source}]({source})")
                continue

            if not isinstance(source, dict):
                st.write(source)
                continue

            title = (
                source.get("topic")
                or source.get("title")
                or source.get("id")
                or f"Source {index}"
            )

            summary = source.get("summary", "")

            url = (
                source.get("source_url")
                or source.get("url")
                or source.get("link")
            )

            st.markdown(f"**{index}. {title}**")

            if summary:
                st.write(summary)

            if url:
                st.markdown(f"[Open official source]({url})")

            st.divider()


def display_comparison(comparison):
    """Display Old vs New Regime comparison card."""

    if not comparison:
        return

    new_regime = comparison.get("new_regime", {})
    old_regime = comparison.get("old_regime", {})

    if not new_regime or not old_regime:
        return

    better = comparison.get("better_regime")
    saving = comparison.get("tax_saving", 0)

    st.markdown("### 📊 Tax Regime Comparison")

    if better == "new":
        st.success(
            f"🏆 New Regime is better — "
            f"Estimated tax saving: {format_rupees(saving)}"
        )
    elif better == "old":
        st.success(
            f"🏆 Old Regime is better — "
            f"Estimated tax saving: {format_rupees(saving)}"
        )
    else:
        st.info("Both regimes have the same estimated tax.")

    col1, col2 = st.columns(2)

    with col1:
        if better == "new":
            st.success("NEW REGIME — Lower estimated tax")
        else:
            st.subheader("NEW REGIME")

        st.metric(
            "Total Tax",
            format_rupees(new_regime.get("total_tax", 0))
        )

        st.write(
            "**Taxable Income:**",
            format_rupees(new_regime.get("taxable_income", 0))
        )

        st.write(
            "**Slab Tax:**",
            format_rupees(new_regime.get("slab_tax", 0))
        )

        st.write(
            "**Section 87A Rebate:**",
            format_rupees(new_regime.get("rebate_87a", 0))
        )

        st.write(
            "**Tax after Rebate:**",
            format_rupees(new_regime.get("tax_after_rebate", 0))
        )

        st.write(
            "**Health & Education Cess:**",
            format_rupees(new_regime.get("cess_4_percent", 0))
        )

    with col2:
        if better == "old":
            st.success("OLD REGIME — Lower estimated tax")
        else:
            st.subheader("OLD REGIME")

        st.metric(
            "Total Tax",
            format_rupees(old_regime.get("total_tax", 0))
        )

        st.write(
            "**Taxable Income:**",
            format_rupees(old_regime.get("taxable_income", 0))
        )

        st.write(
            "**Slab Tax:**",
            format_rupees(old_regime.get("slab_tax", 0))
        )

        st.write(
            "**Section 87A Rebate:**",
            format_rupees(old_regime.get("rebate_87a", 0))
        )

        st.write(
            "**Tax after Rebate:**",
            format_rupees(old_regime.get("tax_after_rebate", 0))
        )

        st.write(
            "**Health & Education Cess:**",
            format_rupees(old_regime.get("cess_4_percent", 0))
        )

    st.markdown("#### Slab-wise Tax Breakdown")

    breakdown_col1, breakdown_col2 = st.columns(2)

    with breakdown_col1:
        st.markdown("**New Regime Slabs**")

        new_breakdown = new_regime.get("breakdown", [])

        if new_breakdown:
            st.dataframe(
                [
                    {
                        "Slab": item.get("slab", ""),
                        "Rate": f'{item.get("rate_percent", 0)}%',
                        "Income": format_rupees(
                            item.get("income_in_slab", 0)
                        ),
                        "Tax": format_rupees(item.get("tax", 0))
                    }
                    for item in new_breakdown
                ],
                hide_index=True,
                use_container_width=True
            )

    with breakdown_col2:
        st.markdown("**Old Regime Slabs**")

        old_breakdown = old_regime.get("breakdown", [])

        if old_breakdown:
            st.dataframe(
                [
                    {
                        "Slab": item.get("slab", ""),
                        "Rate": f'{item.get("rate_percent", 0)}%',
                        "Income": format_rupees(
                            item.get("income_in_slab", 0)
                        ),
                        "Tax": format_rupees(item.get("tax", 0))
                    }
                    for item in old_breakdown
                ],
                hide_index=True,
                use_container_width=True
            )

    st.caption(
        "Note: This comparison uses the tax rules and deduction assumptions "
        "currently implemented in this project. Old-regime deductions such "
        "as 80C, 80D and HRA are not fully considered. Verify actual tax "
        "liability using the official Income Tax portal."
    )

    st.markdown(
        "[Income Tax Department – Official Portal]"
        "(https://www.incometax.gov.in/iec/foportal/)"
    )


def display_agent_steps(steps):
    """Display agent tool execution steps."""

    if steps:
        with st.expander("⚙️ Calculation / Agent Steps"):
            st.json(steps)


# --------------------------------------------------
# DISPLAY CHAT HISTORY
# --------------------------------------------------

for index, message in enumerate(st.session_state.messages):

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

        # Regime comparison card
        comparison = message.get("comparison")

        if comparison:
            display_comparison(comparison)

        # Sources
        display_sources(message.get("sources", []))

        # Agent steps
        display_agent_steps(message.get("steps", []))

        # Feedback
        if (
            message["role"] == "assistant"
            and message.get("feedback_enabled")
        ):

            col1, col2 = st.columns(2)

            with col1:
                if st.button(
                    "👍 Helpful",
                    key=f"like_{index}"
                ):
                    save_feedback(
                        message["id"],
                        "positive"
                    )
                    st.success("Thanks for your feedback!")

            with col2:
                if st.button(
                    "👎 Not Helpful",
                    key=f"dislike_{index}"
                ):
                    save_feedback(
                        message["id"],
                        "negative"
                    )
                    st.success("Thanks for your feedback!")


# --------------------------------------------------
# CHAT INPUT
# --------------------------------------------------

question = st.chat_input(
    "Ask your income tax question...",
    disabled=st.session_state.pending_approval is not None
)

if question:

    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.markdown(question)

    try:

        with st.spinner("TaxSaathi is thinking..."):

            response = requests.post(
                API_URL,
                json={
                    "question": question,
                    "thread_id": st.session_state.thread_id
                },
                timeout=60
            )

            response.raise_for_status()
            data = response.json()

        if data.get("status") == "awaiting_approval":

            st.session_state.pending_approval = {
                "thread_id": data["thread_id"],
                "question": question,
                "details": data.get("approval_required", {}),
                "steps": data.get("steps", []),
                "sources": data.get("sources", []),
                "comparison": data.get("comparison")
            }

            st.session_state.messages.append({
                "role": "assistant",
                "content": (
                    "Approval is required before completing "
                    "this request."
                ),
                "id": str(uuid.uuid4()),
                "feedback_enabled": False
            })

        else:

            st.session_state.messages.append({
                "role": "assistant",
                "content": data.get("answer", "No answer received."),
                "id": str(uuid.uuid4()),
                "sources": data.get("sources", []),
                "steps": data.get("steps", []),
                "comparison": data.get("comparison"),
                "feedback_enabled": True
            })

    except requests.exceptions.RequestException as error:

        st.session_state.messages.append({
            "role": "assistant",
            "content": f"Backend connection error: {error}",
            "id": str(uuid.uuid4()),
            "feedback_enabled": False
        })

    st.rerun()


# --------------------------------------------------
# HUMAN APPROVAL SECTION
# --------------------------------------------------

if st.session_state.pending_approval is not None:

    pending = st.session_state.pending_approval

    st.divider()
    st.warning("⏳ Human approval required.")

    st.markdown("**Question:**")
    st.write(pending["question"])

    with st.expander("Approval Details"):
        st.json(pending["details"])

    # Show comparison preview, if available
    if pending.get("comparison"):
        display_comparison(pending["comparison"])

    col1, col2 = st.columns(2)

    with col1:

        if st.button("✅ Approve", type="primary"):

            try:

                with st.spinner("Completing approved request..."):

                    result = requests.post(
                        API_URL,
                        json={
                            "question": pending["question"],
                            "thread_id": pending["thread_id"],
                            "approved": True
                        },
                        timeout=60
                    )

                    result.raise_for_status()
                    answer_data = result.json()

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer_data.get(
                        "answer",
                        "No answer received."
                    ),
                    "id": str(uuid.uuid4()),
                    "sources": answer_data.get("sources", []),
                    "steps": answer_data.get("steps", []),
                    "comparison": answer_data.get("comparison"),
                    "feedback_enabled": True
                })

                st.session_state.pending_approval = None
                st.rerun()

            except requests.exceptions.RequestException as error:
                st.error(f"Approval error: {error}")

    with col2:

        if st.button("❌ Reject"):

            try:

                result = requests.post(
                    API_URL,
                    json={
                        "question": pending["question"],
                        "thread_id": pending["thread_id"],
                        "approved": False
                    },
                    timeout=60
                )

                result.raise_for_status()

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "Request rejected by user.",
                    "id": str(uuid.uuid4()),
                    "feedback_enabled": False
                })

                st.session_state.pending_approval = None
                st.rerun()

            except requests.exceptions.RequestException as error:
                st.error(f"Rejection error: {error}")
