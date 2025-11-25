import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import datetime

import glob

# Prefer `log.db` in the root if present, otherwise auto-discover any `*.db` files
# Also detect common Week subfolders so the app can read DBs located in them.
DEFAULT_DB_ORDER = ["log.db", "log.db7.db", "log.db8.db"]
WEEK_DIRS = [
    "week-7-store-logs-in-sqlite-and-basic-query-Chandumalhotra",
    "week-8-alert-system-threshold-monitoring-Chandumalhotra-4",
]


def find_db_files():
    found = []

    # prefer exact names in repo root first
    for name in DEFAULT_DB_ORDER:
        if os.path.exists(name):
            found.append(name)

    # include other files in repo root
    for fn in glob.glob("*.db") + glob.glob("*.sqlite") + glob.glob("*.db3"):
        if fn not in found:
            found.append(fn)

    # include preferred names if present but not previously found
    for alt in ["log.db7.db", "log.db8.db"]:
        if os.path.exists(alt) and alt not in found:
            found.append(alt)

    # scan common week subfolders for db files and include them using a relative path
    for sub in WEEK_DIRS:
        if os.path.isdir(sub):
            for fn in glob.glob(os.path.join(sub, "*.db")) + glob.glob(os.path.join(sub, "*.sqlite")):
                rel = os.path.relpath(fn)
                if rel not in found:
                    found.append(rel)

    return found


st.set_page_config(page_title="Networking & Protocols Dashboard", layout="wide")

st.sidebar.title(" Navigation")
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

    # make sure timestamp is a datetime if present
    for cand in ("timestamp", "time", "date", "created_at"):
        if cand in df.columns:
            try:
                df[cand] = pd.to_datetime(df[cand])
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
        # attempt to choose the best timestamp column name
        try:
            return pd.concat(dfs, ignore_index=True).sort_values("timestamp")
        except Exception:
            try:
                return pd.concat(dfs, ignore_index=True).sort_values("created_at")
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


if page == "Dashboard":
    st.title(" Networking & Protocols — Interactive Dashboard")

    st.sidebar.markdown("---")
    db_files = find_db_files()
    if not db_files:
        st.warning("No .db files detected in the repository root or week subfolders. Please place your `log.db` or other .db files in the folder.")
        st.stop()

    options = db_files.copy()
    if len(db_files) > 1:
        options.append("Both")
    data_choice = st.sidebar.selectbox("Choose dataset", options)

    st.sidebar.markdown("### Filters")
    st.sidebar.write("Choose Ping status & thresholds to filter the data")

    ping_filter = st.sidebar.selectbox("Ping status", ["All", "UP", "DOWN"], index=0)

    # thresholds
    cpu_threshold = st.sidebar.slider("Min CPU %", 0, 100, 0)
    mem_threshold = st.sidebar.slider("Min Memory %", 0, 100, 0)
    disk_threshold = st.sidebar.slider("Min Disk %", 0, 100, 0)

    # Table selection: detect available tables for the chosen DB(s)
    chosen_table = None
    if data_choice == "Both":
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

    if df_all.empty:
        st.warning("No data found for the selected dataset. Make sure the DB files exist and contain data.")
    else:
        # normalize and detect columns
        date_col = detect_timestamp_col(df_all)
        numeric_cols = detect_numeric_cols(df_all)
        ping_col = detect_ping_col(df_all)

        # date filter bounds (only if a date/time column was found)
        if date_col and date_col in df_all.columns:
            try:
                min_ts = pd.to_datetime(df_all[date_col]).min()
                max_ts = pd.to_datetime(df_all[date_col]).max()
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

        # convert date column to datetime and standardize name for comparisons
        if date_col and date_col in df.columns:
            try:
                df[date_col] = pd.to_datetime(df[date_col])
                df = df.rename(columns={date_col: "timestamp"})
            except Exception:
                pass

        # apply ping filter
        if ping_filter != "All" and ping_col and ping_col in df.columns:
            df = df[df[ping_col] == ping_filter]

        # apply numeric thresholds (try best-effort mapping)
        cpu_col = next((c for c in numeric_cols if "cpu" in c.lower()), None)
        mem_col = next((c for c in numeric_cols if "mem" in c.lower() or "memory" in c.lower()), None)
        disk_col = next((c for c in numeric_cols if "disk" in c.lower()), None)

        if cpu_col and cpu_col in df.columns:
            df = df[df[cpu_col] >= cpu_threshold]
        if mem_col and mem_col in df.columns:
            df = df[df[mem_col] >= mem_threshold]
        if disk_col and disk_col in df.columns:
            df = df[df[disk_col] >= disk_threshold]

        # apply date range
        if date_range and len(date_range) == 2 and "timestamp" in df.columns:
            start = pd.to_datetime(date_range[0])
            end = pd.to_datetime(date_range[1]) + pd.Timedelta(days=1)
            df = df[(df["timestamp"] >= start) & (df["timestamp"] < end)]

        # Header / metrics
        st.subheader(f"Dataset: {data_choice} — {len(df)} record(s)")

        # Compute alert counts: rows that exceed high thresholds (80/85/90 by default) or configurable
        ALERT_CPU = 80.0
        ALERT_MEM = 85.0
        ALERT_DISK = 90.0

        alert_mask = pd.Series([False] * len(df))
        if cpu_col and cpu_col in df.columns:
            alert_mask = alert_mask | (df[cpu_col] >= ALERT_CPU)
        if mem_col and mem_col in df.columns:
            alert_mask = alert_mask | (df[mem_col] >= ALERT_MEM)
        if disk_col and disk_col in df.columns:
            alert_mask = alert_mask | (df[disk_col] >= ALERT_DISK)

        alert_count = int(alert_mask.sum())

        # Show top-row metrics
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Records", len(df))
        if cpu_col:
            c2.metric("Avg " + cpu_col, f"{df[cpu_col].mean():.1f}" if len(df) else "—")
        if mem_col:
            c3.metric("Avg " + mem_col, f"{df[mem_col].mean():.1f}" if len(df) else "—")
        if disk_col:
            c4.metric("Avg " + disk_col, f"{df[disk_col].mean():.1f}" if len(df) else "—")

        # second row: alert count and breakdown
        a1, a2, a3 = st.columns([1, 2, 2])
        a1.metric("Alerts (>=80/85/90)", alert_count)

        if ping_col and ping_col in df.columns:
            counts = df[ping_col].value_counts()
            a2.subheader("Ping status breakdown")
            a2.bar_chart(counts)

        # Main table and download
        st.markdown("---")
        st.subheader("Filtered Records")
        st.dataframe(df.reset_index(drop=True), use_container_width=True)

        csv = df.to_csv(index=False)
        st.download_button("Download CSV", csv, file_name=f"{os.path.basename(data_choice)}_filtered.csv")

        # Charts
        st.markdown("---")
        st.subheader(" Resource Usage Over Time")
        if "timestamp" in df.columns:
            plot_df = df.set_index("timestamp").sort_index()
        else:
            plot_df = df.reset_index(drop=True)

        metric_cols = [c for c in [cpu_col, mem_col, disk_col] if c in plot_df.columns]
        if metric_cols:
            st.line_chart(plot_df[metric_cols])

        # Optional auto refresh (very simple loop)
        if auto_refresh:
            import time
            time.sleep(5)
            st.experimental_rerun()


elif page == "Settings":
    st.title(" Settings")
    st.write("Configure dashboard options here")
    st.write("- You can toggle auto-refresh and change the selected dataset from the sidebar.")
    st.write("- This app reads two database files in the repo root: log.db7.db (Week 7) and log.db8.db (Week 8).")
    st.write("- It also auto-discovers .db files inside the typical week-7 / week-8 subfolders if present.")

else:
    st.title("ℹ About")
    st.write("This dashboard demonstrates an interactive report for Week 10 of Networking & Protocols.")
    st.write("It reads `log.db7.db` and `log.db8.db` (if present) and provides filters, charts and CSV export.")
