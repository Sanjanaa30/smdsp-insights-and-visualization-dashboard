from typing import Dict, Any
from langgraph.graph import StateGraph, END
from langgraph.types import Command
from langgraph.graph import MessagesState
from langchain_core.messages import SystemMessage, AIMessage
from app.utils.plsql import get_data_db
from app.agent.model import llm


class SQLAgentState(MessagesState):
    sql: str = ""
    result: Any = None


def run_sql(query: str):
    return get_data_db(query)


# ----------------------------
# INTERPRET NODE
# ----------------------------
async def interpret(state: SQLAgentState, config):
    messages = state["messages"]
    user_msg = messages[-1].content.strip().lower()

    # -------- SMALL TALK HANDLING --------
    if user_msg in ["hi", "hello", "hey", "yo"]:
        resp = AIMessage(content="Hello! How can I help with your database questions?")
        return Command(
            update={"messages": messages + [resp]},
            goto=END,  # <-- STOP FLOW
        )

    # -------- GENERATE SQL ----------
    prompt = f"""
Write a valid Oracle SQL query to answer this question:

{messages[-1].content}

Only output SQL.
"""
    sql_msg = await llm.ainvoke([SystemMessage(content=prompt)], config)
    sql = sql_msg.content.strip()

    return Command(
        update={"messages": messages + [sql_msg], "sql": sql}, goto="execute_sql"
    )


# ----------------------------
# EXECUTE SQL NODE
# ----------------------------
async def execute_sql(state: SQLAgentState, config):
    sql = state["sql"]
    messages = state["messages"]

    try:
        result = run_sql(sql)
    except Exception as e:
        result = f"SQL Error: {str(e)}"

    return Command(update={"result": result, "messages": messages}, goto="answer")


# ----------------------------
# ANSWER NODE
# ----------------------------
async def answer(state: SQLAgentState, config):
    messages = state["messages"]
    result = state.get("result", None)

    if result is None:
        # fallback behavior
        msg = AIMessage(content="No SQL result available.")
        return Command(update={"messages": state["messages"] + [msg]}, goto=END)

    prompt = f"""
User question: {messages[-2].content}
SQL result: {result}

Explain clearly.
"""

    final_msg = await llm.ainvoke([SystemMessage(content=prompt)], config)

    return Command(update={"messages": messages + [final_msg]}, goto=END)


# ----------------------------
# GRAPH DEFINITION
# ----------------------------
graph = StateGraph(SQLAgentState)

graph.add_node("interpret", interpret)
graph.add_node("execute_sql", execute_sql)
graph.add_node("answer", answer)

graph.set_entry_point("interpret")

# IMPORTANT: ONLY EXECUTE DYNAMIC JUMPS — NO STATIC EDGES!
# interpret decides to goto END OR execute_sql
# execute_sql always goto answer
# answer always goto END

graph.add_edge("execute_sql", "answer")
graph.add_edge("answer", END)

from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()

sql_agent = graph.compile(checkpointer=memory)
