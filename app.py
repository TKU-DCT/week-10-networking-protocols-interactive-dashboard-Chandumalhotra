import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import datetime

import glob

# Prefer `log.db` in the root if present, otherwise auto-discover any `*.db` files
DEFAULT_DB_ORDER = ["log.db", "log.db7.db", "log.db8.db"]


def find_db_files():
    # Look for exact preferred files first
    found = []
    for name in DEFAULT_DB_ORDER:
        if os.path.exists(name):
            found.append(name)

    # then include any other .db files in repository root
    for fn in glob.glob("*.db") + glob.glob("*.sqlite") + glob.glob("*.db3"):
        if fn not in found:
            found.append(fn)

    # if nothing found, attempt log.db7.db / log.db8.db too
    for alt in ["log.db7.db", "log.db8.db"]:
        if os.path.exists(alt) and alt not in found:
            found.append(alt)

    return found

st.set_page_config(page_title="Networking & Protocols Dashboard", layout="wide")

st.sidebar.title("📂 Navigation")
page = st.sidebar.radio("Select Page", ["Dashboard", "Settings", "About"])


def load_db(path: str, table: str | None = None) -> pd.DataFrame:
    if not os.path.exists(path):
        return pd.DataFrame()
    conn = sqlite3.connect(path)
    # choose a table automatically if system_log doesn't exist
    try:
        if table:
            df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
        else:
            df = pd.read_sql_query("SELECT * FROM system_log", conn)
    except Exception:
        # try first available table
        tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        if not tables:
            conn.close()
            return pd.DataFrame()
        df = pd.read_sql_query(f"SELECT * FROM {tables[0]}", conn)
    conn.close()

    # make sure timestamp is a datetime
    if "timestamp" in df.columns:
        try:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
        except Exception:
            pass
    return df


def combine_dbs(selection: str, db_files: list, table: str | None = None) -> pd.DataFrame:
    # selection is a filename or "Both" to join all discovered DBs
    dfs = []
    if selection == "Both":
        for fn in db_files:
            d = load_db(fn, table=table)
            if not d.empty:
                d = d.copy()
                d["source"] = os.path.basename(fn)
                dfs.append(d)
    else:
        d = load_db(selection, table=table)
        if not d.empty:
            d = d.copy()
            d["source"] = os.path.basename(selection)
            dfs.append(d)

    if dfs:
        # if timestamp exists, sort by it
        try:
            return pd.concat(dfs, ignore_index=True).sort_values("timestamp")
        except Exception:
            return pd.concat(dfs, ignore_index=True)
    return pd.DataFrame()


def list_tables(path: str) -> list:
    if not os.path.exists(path):
        return []
    conn = sqlite3.connect(path)
    rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    conn.close()
    return [r[0] for r in rows]


def detect_timestamp_col(df: pd.DataFrame) -> str | None:
    candidates = [c for c in df.columns if "time" in c.lower() or "date" in c.lower()]
    if not candidates:
        # fallback: any column of datetime type
        for c in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[c]):
                return c
        return None
    return candidates[0]


def detect_numeric_cols(df: pd.DataFrame) -> list:
    numerics = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    return numerics


def detect_ping_col(df: pd.DataFrame) -> str | None:
    for c in df.columns:
        if "ping_status" in c.lower() or c.lower() in ("status", "ping_state"):
            return c
    # try a categorical column that contains UP/DOWN values
    for c in df.columns:
        if df[c].dtype == object:
            vals = set(df[c].dropna().unique())
            if "UP" in vals or "DOWN" in vals:
                return c
    return None


def format_timestamp(df: pd.DataFrame):
    if "timestamp" in df.columns:
        try:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
        except Exception:
            pass


if page == "Dashboard":
    st.title("🌐 Networking & Protocols — Interactive Dashboard")

    st.sidebar.markdown("---")
    db_files = find_db_files()
    if not db_files:
        st.warning("No .db files detected in the repository root. Please place your `log.db` or other .db files in the folder.")
        st.stop()

    options = db_files.copy()
    if len(db_files) > 1:
        options.append("Both")
    data_choice = st.sidebar.selectbox("Choose dataset", options)

    st.sidebar.markdown("### Filters")
    st.sidebar.write("Choose Ping status & CPU threshold to filter the data")

    ping_filter = st.sidebar.selectbox("Ping status", ["All", "UP", "DOWN"], index=0)
    cpu_threshold = st.sidebar.slider("Min CPU %", 0, 100, 0)

    # Table selection: detect available tables for the chosen DB(s)
    chosen_table = None
    if data_choice == "Both":
        # find common tables across db_files
        table_sets = [set(list_tables(fn)) for fn in db_files]
        common = set.intersection(*table_sets) if table_sets else set()
        if not common:
            st.warning("No common tables found across the chosen databases. Choose a single DB to continue.")
            st.stop()
        chosen_table = st.sidebar.selectbox("Choose table (common to all DBs)", sorted(list(common)))
        df_all = combine_dbs(data_choice, db_files, table=chosen_table)
    else:
        tables = list_tables(data_choice)
        if not tables:
            st.warning(f"No tables found in {data_choice} — check the file or pick a different DB.")
            st.stop()
        chosen_table = st.sidebar.selectbox("Choose table", tables, index=0)
        df_all = combine_dbs(data_choice, [data_choice], table=chosen_table)
    format_timestamp(df_all)

    if df_all.empty:
        st.warning("No data found for the selected dataset. Make sure the DB files exist in the repository root.")
    else:
        # detect timestamp column and numeric/ping columns
        ts_col = detect_timestamp_col(df_all)
        numeric_cols = detect_numeric_cols(df_all)
        ping_col = detect_ping_col(df_all)

        # date filter bounds (only if timestamp available)
        if ts_col:
            try:
                min_ts = pd.to_datetime(df_all[ts_col]).min()
                max_ts = pd.to_datetime(df_all[ts_col]).max()
                date_range = st.sidebar.date_input("Date range", [min_ts.date(), max_ts.date()])
            except Exception:
                date_range = None
        else:
            date_range = None

        # Refresh controls
        refresh = st.sidebar.button("Refresh")
        auto_refresh = st.sidebar.checkbox("Auto refresh (5s)")

        # Apply filters
        df = df_all.copy()
        # apply ping filter if ping column exists
        if ping_filter != "All" and ping_col and ping_col in df.columns:
            df = df[df[ping_col] == ping_filter]
        # apply cpu threshold if a numeric column looks like CPU
        cpu_col = None
        # try to find a cpu-like column name
        for c in numeric_cols:
            if "cpu" in c.lower():
                cpu_col = c
                break
        if cpu_col and cpu_col in df.columns:
            df = df[df[cpu_col] >= cpu_threshold]

        # apply date range
        if len(date_range) == 2:
            start = pd.to_datetime(date_range[0])
            end = pd.to_datetime(date_range[1]) + pd.Timedelta(days=1)
            df = df[(df["timestamp"] >= start) & (df["timestamp"] < end)]

        # Header / metrics
        st.subheader(f"Dataset: {data_choice} — {len(df)} record(s)")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Records", len(df))
        if numeric_cols:
            # pick common names for display if present
            display_cpu = next((c for c in numeric_cols if "cpu" in c.lower()), None)
            display_mem = next((c for c in numeric_cols if "mem" in c.lower() or "memory" in c.lower()), None)
            display_disk = next((c for c in numeric_cols if "disk" in c.lower()), None)
            if display_cpu:
                c2.metric("Avg " + display_cpu, f"{df[display_cpu].mean():.1f}")
            if display_mem:
                c3.metric("Avg " + display_mem, f"{df[display_mem].mean():.1f}")
            if display_disk:
                c4.metric("Avg " + display_disk, f"{df[display_disk].mean():.1f}")

        # Ping status breakdown
        if ping_col and ping_col in df.columns:
            counts = df[ping_col].value_counts()
            st.bar_chart(counts)

        # Main table and download
        st.markdown("---")
        st.subheader("Filtered Records")
        st.dataframe(df.reset_index(drop=True), use_container_width=True)

        csv = df.to_csv(index=False)
        st.download_button("Download CSV", csv, file_name=f"{data_choice}_filtered.csv")

        # Charts
        st.markdown("---")
        st.subheader("📈 Resource Usage Over Time")
        if ts_col and ts_col in df.columns:
            plot_df = df.set_index(ts_col).sort_index()
        else:
            # fallback to index-based plotting
            plot_df = df.reset_index(drop=True)

        metric_cols = [c for c in numeric_cols if c in plot_df.columns]
        if metric_cols:
            st.line_chart(plot_df[metric_cols])

        # Optional auto refresh
        if auto_refresh:
            st.experimental_rerun()

elif page == "Settings":
    st.title("⚙️ Settings")
    st.write("Configure dashboard options here")
    st.write("- You can toggle auto-refresh and change the selected dataset from the sidebar.")
    st.write("- This app reads two database files in the repo root: log.db7.db (Week 7) and log.db8.db (Week 8).")

else:
    st.title("ℹ️ About")
    st.write("This dashboard demonstrates an interactive report for Week 10 of Networking & Protocols.")
    st.write("It reads `log.db7.db` and `log.db8.db` (if present) and provides filters, charts and CSV export.")
