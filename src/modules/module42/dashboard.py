import datetime
from datetime import timezone
import streamlit as st
from auth import remove_auth_cookie

def render_dashboard(payload: dict):
    # ── Topbar
    st.markdown(
        """
        <div class="dash-topbar">
            <div class="topbar-brand">
                <div class="cross-icon-sm">⚕️</div>
                <span class="topbar-name">ClinicalView</span>
            </div>
            <div class="session-badge">
                <span class="chip-dot"></span>
                Session Active
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Session countdown
    exp_ts = payload.get("exp")
    if exp_ts:
        remaining = datetime.datetime.fromtimestamp(exp_ts, tz=timezone.utc) - datetime.datetime.now(timezone.utc)
        h = max(int(remaining.total_seconds() // 3600), 0)
        m = max(int((remaining.total_seconds() % 3600) // 60), 0)
        session_text = f"{h}h {m}m"
    else:
        session_text = "—"

    full_name = payload.get("full_name", "User")
    role      = payload.get("role", "—")

    # ── Stat cards — pure HTML grid (no st.columns)
    st.markdown(
        f"""
        <div class="stat-grid">
            <div class="stat-card">
                <span class="stat-icon">👤</span>
                <div class="stat-value">{full_name}</div>
                <div class="stat-label">Signed-in user</div>
            </div>
            <div class="stat-card">
                <span class="stat-icon">🏷️</span>
                <div class="stat-value"><span class="role-pill">{role}</span></div>
                <div class="stat-label">Access role</div>
            </div>
            <div class="stat-card">
                <span class="stat-icon">⏱️</span>
                <div class="stat-value">{session_text}</div>
                <div class="stat-label">Session remaining</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Content panel removed to avoid confusion with the actual views

    # ── Sign-out button
    _, mid, _ = st.columns([2, 1, 2])
    with mid:
        st.markdown('<div class="logout-wrap">', unsafe_allow_html=True)
        if st.button("🚪  Sign Out", use_container_width=True):
            from auth import remove_auth_cookie
            remove_auth_cookie()
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        '<div class="page-footer">© 2026 CLINICALVIEW · ALL RIGHTS RESERVED</div>',
        unsafe_allow_html=True,
    )
