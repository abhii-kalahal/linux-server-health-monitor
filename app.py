import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

from monitor import get_system_metrics, get_system_info
from database import (
    initialize_database,
    save_metrics,
    get_metrics_history,
    save_security_event,
    get_security_events
)
from log_analyzer import analyze_logs

st.set_page_config(
    page_title="ServerGuard | Linux Monitor",
    page_icon="🛡️",
    layout="wide"
)

st.markdown("""
<style>
.stApp {background-color: #0b1120; color: #e5e7eb;}
[data-testid="stMetric"] {
    background: #172338;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #263750;
}
[data-testid="stMetricLabel"] {color: #9ca3af;}
h1, h2, h3 {color: #e5e7eb;}
</style>
""", unsafe_allow_html=True)

initialize_database()

st.sidebar.title("🛡️ ServerGuard")
st.sidebar.caption("Linux Server Health & Security Monitor")
page = st.sidebar.radio(
    "Navigation",
    ["Overview", "System Details", "Log Analysis",
     "Monitoring History", "About"]
)

st.sidebar.divider()
st.sidebar.caption("Python • Linux • SQLite • Streamlit")

metrics = get_system_metrics()
info = get_system_info()

save_metrics(metrics)

st.title("🛡️ ServerGuard")
st.caption("Real-time Linux Server Health Monitoring & Log Analysis")
st.caption(f"Last updated: {metrics['timestamp']}")

if page == "Overview":
    st.subheader("System Overview")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("CPU Usage", f"{metrics['cpu']}%")
    c2.metric("Memory Usage", f"{metrics['memory']}%")
    c3.metric("Disk Usage", f"{metrics['disk']}%")
    c4.metric("Uptime", f"{metrics['uptime']} hrs")

    st.divider()
    st.subheader("Resource Health")

    for label, value in [
        ("CPU", metrics["cpu"]),
        ("Memory", metrics["memory"]),
        ("Disk", metrics["disk"])
    ]:
        st.write(f"**{label} Usage**")
        st.progress(min(int(value), 100))

        if value >= 90:
            st.error(f"High {label} usage detected!")
        elif value >= 75:
            st.warning(f"{label} usage is elevated.")
        else:
            st.success(f"{label} usage is within the configured threshold.")

    st.divider()
    st.subheader("Recent Security Events")

    events = get_security_events(10)

    if events:
        df = pd.DataFrame(
            events,
            columns=["Timestamp", "Event Type", "Details"]
        )
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No security events recorded yet. Run Log Analysis to scan available logs.")

    if st.button("Refresh Dashboard"):
        st.rerun()

elif page == "System Details":
    st.subheader("System Information")

    left, right = st.columns(2)

    with left:
        st.write("**Hostname:**", info["hostname"])
        st.write("**Operating System:**", info["os"])
        st.write("**Processor:**", info["processor"] or "Not reported")

    with right:
        st.write("**CPU Cores:**", info["cpu_cores"])
        st.write("**Total RAM:**", f"{info['total_ram']} GB")
        st.write("**Total Disk:**", f"{info['disk_total']} GB")

    st.divider()
    st.subheader("Current Resource Utilization")

    resource_df = pd.DataFrame({
        "Resource": ["CPU", "Memory", "Disk"],
        "Usage": [
            metrics["cpu"],
            metrics["memory"],
            metrics["disk"]
        ]
    })

    fig = px.bar(
        resource_df,
        x="Resource",
        y="Usage",
        color="Resource",
        range_y=[0, 100],
        title="Current System Resource Usage (%)"
    )
    st.plotly_chart(fig, use_container_width=True)

elif page == "Log Analysis":
    st.subheader("Security Log Analyzer")
    st.write("Scan available Linux authentication logs for suspicious login indicators.")

    st.warning(
        "A matching log entry is an indicator for investigation, "
        "not proof of a successful attack."
    )

    if st.button("Run Security Log Scan"):
        with st.spinner("Analyzing available logs..."):
            found_events = analyze_logs()

            for event in found_events:
                save_security_event(
                    event["timestamp"],
                    event["event_type"],
                    event["details"]
                )

        st.session_state["last_scan_count"] = len(found_events)

        if found_events:
            st.error(f"Found {len(found_events)} matching log entries.")
        else:
            st.success("No matching entries found in the available logs.")

    if "last_scan_count" in st.session_state:
        st.metric("Last Scan Matches", st.session_state["last_scan_count"])

    events = get_security_events(100)

    if events:
        df = pd.DataFrame(
            events,
            columns=["Timestamp", "Event Type", "Details"]
        )
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No security events stored yet.")

    st.caption(
        "Log access depends on file permissions and available system logs. "
        "The analyzer checks auth.log, secure, and SSH journal entries."
    )

elif page == "Monitoring History":
    st.subheader("Historical Monitoring Data")

    history = get_metrics_history(100)

    if history:
        df = pd.DataFrame(
            history,
            columns=["Timestamp", "CPU", "Memory", "Disk", "Uptime"]
        )

        fig = px.line(
            df,
            x="Timestamp",
            y=["CPU", "Memory", "Disk"],
            markers=True,
            title="Server Resource Usage History"
        )
        fig.update_layout(yaxis_title="Usage (%)")
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(df, use_container_width=True, hide_index=True)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download Monitoring History CSV",
            csv,
            "monitoring_history.csv",
            "text/csv"
        )
    else:
        st.info("Monitoring history will appear as measurements are collected.")

elif page == "About":
    st.subheader("About ServerGuard")

    st.markdown("""
    **ServerGuard** is a Python-based Linux server health monitoring
    and log analysis application.

    ### Main Features
    - CPU, RAM and disk usage monitoring
    - System uptime tracking
    - Linux authentication log analysis
    - Failed login and invalid user detection
    - SQLite-based monitoring history
    - Interactive charts and CSV export

    ### Technology Stack
    - Python
    - Linux
    - Streamlit
    - SQLite
    - Pandas
    - Plotly
    - Psutil

    ### Future Enhancements
    - Docker containerization
    - GitHub Actions CI/CD
    - Prometheus and Grafana integration
    - AWS cloud deployment
    - Email-based alerts
    """)

st.sidebar.divider()
st.sidebar.caption("ServerGuard | Academic Project")
