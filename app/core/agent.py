# app/core/agent.py — rewritten for LangChain 1.2.x / LangGraph
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.prebuilt import create_react_agent
from loguru import logger

from app.core.llm_factory import get_llm
from app.core.persona import SYSTEM_PROMPT
from app.core.rag import query_knowledge
from app.tools.analytics.monte_carlo import monte_carlo_risk_assessment

# ── Tool definitions ──────────────────────────────────────

@tool
def get_facility_status(query: str = "") -> str:
    """Returns current facility operational status."""
    return (
        "All facility systems nominal. "
        "Network: online. Cameras: 0 active (pending setup). "
        "Sensors: pending IoT integration. Threat level: GREEN."
    )

@tool
def get_current_time(query: str = "") -> str:
    """Returns current date and time."""
    from datetime import datetime
    return datetime.now().strftime("Stardate %Y-%m-%d %H:%M:%S")

@tool
def query_facility_knowledge(question: str) -> str:
    """
    Query the facility knowledge base for historical data,
    device records, network maps, or past events.
    Input: a natural language question.
    """
    return query_knowledge(question)

# ── BASE_TOOLS ────────────────────────────────────────────
BASE_TOOLS = [get_facility_status, get_current_time, query_facility_knowledge, monte_carlo_risk_assessment]

# ── Agent singleton ───────────────────────────────────────
_agent = None
_history = []  # manual conversation history

def get_agent():
    global _agent
    if _agent is None:
        logger.info("Initializing Mr. House agent...")
        llm = get_llm("smart")
        _agent = create_react_agent(llm, BASE_TOOLS)
        logger.success("Agent online.")
    return _agent

def invoke(message: str) -> str:
    """
    Main entry point. Call this from chat.py.
    Maintains conversation history manually since
    LangGraph's create_react_agent handles it via messages.
    """
    global _history
    agent = get_agent()

    # Build message list: system prompt + history + new message
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + _history + [HumanMessage(content=message)]

    result = agent.invoke({"messages": messages})

    # Extract the last AI message
    ai_messages = [m for m in result["messages"] if hasattr(m, "content") and m.__class__.__name__ == "AIMessage"]
    response = ai_messages[-1].content if ai_messages else "Systems unresponsive. Stand by."

    # Update history (keep last 20 exchanges = 40 messages)
    _history.append(HumanMessage(content=message))
    _history.append(ai_messages[-1] if ai_messages else HumanMessage(content=""))
    if len(_history) > 40:
        _history = _history[-40:]

    return response