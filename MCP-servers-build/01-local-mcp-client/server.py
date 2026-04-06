"""Local FastMCP server exposing SQLite-backed tools over SSE.

Run with:
    python server.py
The server listens on http://127.0.0.1:8000/sse
"""

import sqlite3
from fastmcp import FastMCP

DB_PATH = "demo.db"

mcp = FastMCP("local-sqlite-mcp")


def _init_db() -> None:
    """Create the people table if it does not already exist."""
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS people (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                profession TEXT NOT NULL
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


@mcp.tool()
def add_data(name: str, age: int, profession: str) -> str:
    """Insert a new person record into the SQLite `people` table.

    Use this tool whenever the user wants to add, save, store, insert,
    or record a new person. Requires the person's name, age, and
    profession. Returns a confirmation string with the new row id.

    Args:
        name: Full name of the person.
        age: Age of the person in years.
        profession: Job title or profession.
    """
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.execute(
            "INSERT INTO people (name, age, profession) VALUES (?, ?, ?)",
            (name, age, profession),
        )
        conn.commit()
        return f"Inserted person id={cur.lastrowid}: {name}, {age}, {profession}"
    finally:
        conn.close()


@mcp.tool()
def read_data() -> list[dict]:
    """Read every person record from the SQLite `people` table.

    Use this tool whenever the user wants to list, show, read, query,
    fetch, or look up the people that have been stored. Takes no
    arguments and returns a list of dicts with id, name, age, and
    profession for every row in the table.
    """
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT id, name, age, profession FROM people ORDER BY id"
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


if __name__ == "__main__":
    _init_db()
    # Serve over SSE on the default host/port (127.0.0.1:8000)
    mcp.run(transport="sse", host="127.0.0.1", port=8000)
