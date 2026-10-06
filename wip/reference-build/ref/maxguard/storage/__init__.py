"""Storage (v2.0): state.py (SQLite: analyses, alerts, audit) and events.py
(hourly Parquet files queried with DuckDB).

Import the class you need from its module, e.g.
`from maxguard.storage.state import StateStore`. Nothing is imported here, so
using the SQLite store never loads DuckDB.
"""
