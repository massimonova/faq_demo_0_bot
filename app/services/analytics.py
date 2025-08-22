from __future__ import annotations
import os, csv, datetime
import aiosqlite
from typing import List, Tuple

DB_PATH = "data/analytics.sqlite3"

async def init_db() -> None:
    os.makedirs("data", exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript("""
CREATE TABLE IF NOT EXISTS events(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts TEXT NOT NULL,
  user_id INTEGER,
  action TEXT,
  payload TEXT
);
CREATE TABLE IF NOT EXISTS faq_stats(
  cat_id TEXT,
  idx INTEGER,
  views INTEGER DEFAULT 0,
  helpful_yes INTEGER DEFAULT 0,
  helpful_no INTEGER DEFAULT 0,
  PRIMARY KEY(cat_id, idx)
);
CREATE TABLE IF NOT EXISTS searches(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts TEXT NOT NULL,
  user_id INTEGER,
  query TEXT,
  results INTEGER
);
""")
        await db.commit()

def _now() -> str:
    return datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z"

async def log_event(user_id: int, action: str, payload: str = "") -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO events(ts,user_id,action,payload) VALUES(?,?,?,?)",
            (_now(), user_id, action, payload),
        )
        await db.commit()

async def log_search(user_id: int, query: str, results: int) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO searches(ts,user_id,query,results) VALUES(?,?,?,?)",
            (_now(), user_id, query, results),
        )
        await db.commit()

async def inc_view(cat_id: str, idx: int) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO faq_stats(cat_id,idx,views,helpful_yes,helpful_no) "
            "VALUES(?,?,1,0,0) ON CONFLICT(cat_id,idx) DO UPDATE SET views=views+1",
            (cat_id, idx),
        )
        await db.commit()

async def mark_helpful(cat_id: str, idx: int, yes: bool) -> None:
    field = "helpful_yes" if yes else "helpful_no"
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            f"INSERT INTO faq_stats(cat_id,idx,views,helpful_yes,helpful_no) "
            f"VALUES(?,?,0,0,0) ON CONFLICT(cat_id,idx) DO UPDATE SET {field}={field}+1",
            (cat_id, idx),
        )
        await db.commit()

async def top_questions(limit: int = 5) -> List[Tuple[str,int,int,int,int]]:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "SELECT cat_id, idx, views, helpful_yes, helpful_no "
            "FROM faq_stats ORDER BY views DESC LIMIT ?", (limit,)
        )
        return await cur.fetchall()

async def failed_queries(limit: int = 5) -> List[Tuple[str,int]]:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "SELECT query, COUNT(*) as cnt FROM searches WHERE results=0 "
            "GROUP BY query ORDER BY cnt DESC LIMIT ?", (limit,)
        )
        return await cur.fetchall()

async def export_csv() -> list[str]:
    paths = []
    async with aiosqlite.connect(DB_PATH) as db:
        # events
        cur = await db.execute("SELECT ts,user_id,action,payload FROM events ORDER BY id DESC")
        rows = await cur.fetchall()
        p1 = "data/events.csv"
        with open(p1, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f); w.writerow(["ts","user_id","action","payload"]); w.writerows(rows)
        paths.append(p1)
        # faq_stats
        cur = await db.execute("SELECT cat_id,idx,views,helpful_yes,helpful_no FROM faq_stats")
        rows = await cur.fetchall()
        p2 = "data/faq_stats.csv"
        with open(p2, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f); w.writerow(["cat_id","idx","views","helpful_yes","helpful_no"]); w.writerows(rows)
        paths.append(p2)
        # searches
        cur = await db.execute("SELECT ts,user_id,query,results FROM searches ORDER BY id DESC")
        rows = await cur.fetchall()
        p3 = "data/searches.csv"
        with open(p3, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f); w.writerow(["ts","user_id","query","results"]); w.writerows(rows)
        paths.append(p3)
    return paths
