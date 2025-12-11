from typing import Any
import os
from langgraph.graph import StateGraph, END
from langgraph.types import Command
from langgraph.graph import MessagesState
from langchain_core.messages import SystemMessage, AIMessage
from app.utils.plsql import get_data_db
from app.agent.model import llm
from pathlib import Path
from dotenv import load_dotenv
from app.agent.DBScheme import DB_SCHEMA
from langchain_core.runnables import RunnableConfig

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

CHAN_DATABASE_URL = os.getenv("CHAN_DATABASE_URL")
REDDIT_DATABASE_URL = os.getenv("REDDIT_DATABASE_URL")


class SQLAgentState(MessagesState):
    sql: str = ""
    result: Any = None
    db_used: str = ""


def run_sql(database_url, query: str):
    return get_data_db(database_url, query)


async def choose_database(question: str) -> str:
    prompt = f"""
    Choose the correct database for this question.

    Rules:
    - If the question mentions 4chan data, board_name, post_no → output: chan
    - If the question mentions reddit data, subreddit, unique_name → output: reddit

    Output format:
    Return ONLY one word: chan or reddit

    Question: {question}
    """
    try:
        config = RunnableConfig(recursion_limit=25, metadata={})
        resp = await llm.ainvoke([SystemMessage(content=prompt)], config)
        ans = resp.content.strip().lower()
        return "reddit" if "reddit" in ans else "chan"
    except Exception as e:
        print(e)


async def interpret(state: SQLAgentState, config):
    messages = state["messages"]
    user_msg = messages[-1].content.strip()

    # small talk
    if user_msg.lower() in ["hi", "hello", "hey", "yo"]:
        resp = AIMessage(content="Hello! How can I help with database questions?")
        return Command(update={"messages": messages + [resp]}, goto=END)

    # determine DB
    db_choice = await choose_database(user_msg)
    print("db_choice", db_choice)
    # generate SQL
    prompt = f"""
        You are an agent generating SQL for Oracle/Postgres.

        Use ONLY the tables defined below:

        {DB_SCHEMA}

        User question:
        {user_msg}

        Target database: {db_choice.upper()}

        Output format:
        Return ONLY a valid SQL query.
        Do NOT include explanations, comments, markdown, or surrounding text.
        Return SQL ONLY.
        Do not include database Name [for Example reddit_crawler.toxicity just give toxicity]
        """

    sql_msg = await llm.ainvoke([SystemMessage(content=prompt)], config)
    sql = sql_msg.content.strip()

    return Command(
        update={
            "messages": messages + [sql_msg],
            "sql": sql,
            "db_used": db_choice,
        },
        goto="execute_sql",
    )


async def execute_sql(state: SQLAgentState, config):
    sql = state["sql"]
    db_used = state["db_used"]
    messages = state["messages"]

    database_url = REDDIT_DATABASE_URL if db_used == "reddit" else CHAN_DATABASE_URL

    try:
        result = run_sql(database_url, sql)
    except Exception as e:
        result = f"SQL Error: {str(e)}"

    return Command(update={"result": result}, goto="answer")


async def answer(state: SQLAgentState, config):
    messages = state["messages"]
    result = state.get("result")

    if result is None:
        fail_msg = AIMessage(content="I could not produce any SQL result.")
        return Command(update={"messages": messages + [fail_msg]}, goto=END)

    prompt = f"""
    Question: {messages[-2].content}
    SQL Result: {result}

    Explain this in clear, simple English.
    """

    final_msg = await llm.ainvoke([SystemMessage(content=prompt)], config)

    return Command(update={"messages": messages + [final_msg]}, goto=END)


graph = StateGraph(SQLAgentState)
graph.add_node("interpret", interpret)
graph.add_node("execute_sql", execute_sql)
graph.add_node("answer", answer)

graph.set_entry_point("interpret")
graph.add_edge("execute_sql", "answer")
graph.add_edge("answer", END)

from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()
sql_agent = graph.compile(checkpointer=memory)
