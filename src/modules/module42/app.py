"""
app.py — Secure Clinical Summary View Generator
Tech: Streamlit · PyMongo · PyJWT · bcrypt · streamlit-cookies-controller
"""

import time
import streamlit as st

# ---------------------------------------------------------------------------
# Page config  (must be first Streamlit command)
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="ClinicalView — Secure Access",
    page_icon="⚕️",
    layout="wide",
    initial_sidebar_state="expanded",
)

from auth import verify_user, create_jwt, set_auth_cookie, get_current_user, remove_auth_cookie, get_controller, COOKIE_NAME
from dashboard import render_dashboard
from views.clinical import view_patient_context, view_generate_summary
from views.research import view_query_anonymized_data, view_aggregated_summaries
from views.administrative import view_system_health, view_patient_billing, view_admin_summaries
from views.legal import view_legal_summaries

# ---------------------------------------------------------------------------
# CSS
#
# KEY DESIGN RULE:
#   Streamlit breaks HTML across st.markdown() calls — you CANNOT open a
#   <div class="card"> in one call and have st.form() / st.text_input()
#   render visually inside it. The DOM is not contiguous.
#
#   Solution: drive every visual effect through global CSS selectors that
#   target the actual Streamlit DOM.  Pure-HTML blocks (logo, topbar, stat
#   cards) are safe to inject because they contain no Streamlit widgets.
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600;9..40,700&family=DM+Mono:wght@400;500&family=Playfair+Display:wght@600;700&display=swap');

    /* ── Design tokens ────────────────────────────────── */
    :root {
        --bg:           #07090f;
        --panel:        #0c1019;
        --border:       rgba(255,255,255,0.09);
        --border-focus: rgba(56,205,170,0.55);
        --teal:         #38cdaa;
        --blue:         #4b8cf5;
        --text:         #dde6f5;
        --muted:        #54677e;
        --red-bg:       rgba(255,85,85,0.12);
        --red-border:   rgba(255,85,85,0.30);
        --green-bg:     rgba(56,205,170,0.12);
        --green-border: rgba(56,205,170,0.35);
    }

    /* ── Global ───────────────────────────────────────── */
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif !important; }
    #MainMenu, footer { visibility: hidden; }
    header[data-testid="stHeader"] { 
        background: transparent !important;
    }
    .stAppDeployButton { display: none !important; }

    /* ── Native Streamlit Headers ── */
    header[data-testid="stHeader"] { 
        background: transparent !important;
    }

    .stApp {
        background: var(--bg);
        background-image:
            radial-gradient(ellipse 90% 55% at 15%  -5%, rgba(75,140,245,0.10) 0%, transparent 65%),
            radial-gradient(ellipse 70% 45% at 85% 105%, rgba(56,205,170,0.08) 0%, transparent 60%);
        min-height: 100vh;
    }

    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }

    /* ── Input labels ─────────────────────────────────── */
    .stTextInput label {
        color:          var(--muted) !important;
        font-size:      0.76rem !important;
        font-weight:    600 !important;
        letter-spacing: 0.09em !important;
        text-transform: uppercase !important;
    }

    /* ── Input boxes ──────────────────────────────────── */
    .stTextInput > div > div > input {
        background:    rgba(255,255,255,0.04) !important;
        border:        1px solid var(--border) !important;
        border-radius: 10px !important;
        color:         var(--text) !important;
        font-size:     0.92rem !important;
        font-family:   'DM Sans', sans-serif !important;
        padding:       0.64rem 0.95rem !important;
        caret-color:   var(--teal) !important;
        transition:    border-color 0.2s, box-shadow 0.2s !important;
    }
    .stTextInput > div > div > input::placeholder { color: rgba(221,230,245,0.20) !important; }
    .stTextInput > div > div > input:focus {
        border-color: var(--border-focus) !important;
        box-shadow:   0 0 0 3px rgba(56,205,170,0.11) !important;
        outline: none !important;
    }

    /* ── Form submit button ───────────────────────────── */
    .stFormSubmitButton > button {
        width:          100% !important;
        background:     linear-gradient(135deg, var(--blue), var(--teal)) !important;
        color:          #060a10 !important;
        font-weight:    700 !important;
        font-size:      0.84rem !important;
        letter-spacing: 0.07em !important;
        text-transform: uppercase !important;
        border:         none !important;
        border-radius:  10px !important;
        padding:        0.70rem 1rem !important;
        margin-top:     0.5rem !important;
        box-shadow:     0 4px 22px rgba(56,205,170,0.20) !important;
        transition:     opacity 0.2s, transform 0.15s, box-shadow 0.2s !important;
    }
    .stFormSubmitButton > button:hover {
        opacity:    0.88 !important;
        transform:  translateY(-1px) !important;
        box-shadow: 0 8px 30px rgba(56,205,170,0.30) !important;
    }
    .stFormSubmitButton > button:active { transform: translateY(0) !important; }

    /* ── Logout / secondary button ────────────────────── */
    .logout-wrap .stButton > button {
        background:     rgba(255,255,255,0.04) !important;
        border:         1px solid var(--border) !important;
        color:          var(--muted) !important;
        font-weight:    500 !important;
        font-size:      0.82rem !important;
        letter-spacing: 0.02em !important;
        text-transform: none !important;
        border-radius:  10px !important;
        box-shadow:     none !important;
        transition:     background 0.2s, color 0.2s, border-color 0.2s !important;
    }
    .logout-wrap .stButton > button:hover {
        background:   rgba(255,75,75,0.12) !important;
        border-color: rgba(255,75,75,0.30) !important;
        color:        #ff9999 !important;
        transform:    none !important;
        box-shadow:   none !important;
    }

    /* ── Shared animation ─────────────────────────────── */
    @keyframes blink {
        0%, 100% { opacity: 1; }
        50%       { opacity: 0.2; }
    }

    /* ── Brand header ─────────────────────────────────── */
    .brand-header {
        display:         flex;
        align-items:     center;
        justify-content: center;
        gap:             0.8rem;
        padding:         2.2rem 0 0;
    }
    .cross-icon {
        width: 44px; height: 44px;
        background:    linear-gradient(135deg, var(--blue), var(--teal));
        border-radius: 11px;
        display: flex; align-items: center; justify-content: center;
        font-size:  1.3rem;
        box-shadow: 0 0 26px rgba(56,205,170,0.26);
        flex-shrink: 0;
    }
    .brand-name {
        font-family: 'Playfair Display', serif;
        font-size:   1.45rem;
        font-weight: 700;
        color:       var(--text);
        line-height: 1;
    }
    .brand-sub {
        font-family:    'DM Mono', monospace;
        font-size:      0.60rem;
        color:          var(--teal);
        letter-spacing: 0.15em;
        text-transform: uppercase;
        margin-top:     3px;
    }

    .card-divider { height: 1px; background: var(--border); margin: 1.4rem 0 1.1rem; }

    .section-label {
        font-size:      0.68rem;
        font-weight:    600;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color:          var(--muted);
        margin-bottom:  0.9rem;
    }

    /* ── Login footer ─────────────────────────────────── */
    .login-foot {
        display:         flex;
        align-items:     center;
        justify-content: space-between;
        margin-top:      1.5rem;
        padding-top:     1.1rem;
        border-top:      1px solid var(--border);
        font-size:       0.68rem;
        color:           var(--muted);
        font-family:     'DM Mono', monospace;
        letter-spacing:  0.04em;
    }
    .dot-row  { display: flex; align-items: center; gap: 5px; }
    .live-dot {
        width: 6px; height: 6px;
        background: var(--teal); border-radius: 50%;
        animation: blink 2.2s ease-in-out infinite;
    }

    /* ── Dashboard topbar ─────────────────────────────── */
    .dash-topbar {
        display:         flex;
        align-items:     center;
        justify-content: space-between;
        padding-bottom:  1.2rem;
        border-bottom:   1px solid var(--border);
        margin-bottom:   1.5rem;
    }
    .topbar-brand { display: flex; align-items: center; gap: 0.6rem; }
    .cross-icon-sm {
        width: 32px; height: 32px;
        background:    linear-gradient(135deg, var(--blue), var(--teal));
        border-radius: 8px;
        display: flex; align-items: center; justify-content: center;
        font-size:  0.95rem;
        box-shadow: 0 0 16px rgba(56,205,170,0.20);
    }
    .topbar-name {
        font-family: 'Playfair Display', serif;
        font-size:   1.05rem;
        font-weight: 700;
        color:       var(--text);
    }
    .session-badge {
        display:        flex;
        align-items:    center;
        gap:            5px;
        background:     rgba(56,205,170,0.09);
        border:         1px solid rgba(56,205,170,0.20);
        color:          var(--teal);
        font-size:      0.66rem;
        font-weight:    600;
        letter-spacing: 0.10em;
        text-transform: uppercase;
        padding:        0.26rem 0.72rem;
        border-radius:  20px;
        font-family:    'DM Mono', monospace;
    }

    /* ── Stat cards (HTML grid) ───────────────────────── */
    .stat-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 10px; margin-bottom: 12px; }
    .stat-card {
        background:    var(--panel);
        border:        1px solid var(--border);
        border-radius: 13px;
        padding:       1.1rem 1.1rem 1rem;
        position:      relative;
        overflow:      hidden;
        transition:    border-color 0.2s, transform 0.2s;
    }
    .stat-card::after {
        content:    '';
        position:   absolute;
        bottom: 0; left: 0; right: 0;
        height:     2px;
        background: linear-gradient(90deg, var(--blue), var(--teal));
        opacity:    0;
        transition: opacity 0.25s;
    }
    .stat-card:hover { border-color: rgba(255,255,255,0.16); transform: translateY(-2px); }
    .stat-card:hover::after { opacity: 1; }

    .stat-icon  { font-size: 1.1rem; margin-bottom: 0.5rem; display: block; }
    .stat-value {
        font-family:   'DM Mono', monospace;
        font-size:     0.88rem;
        font-weight:   500;
        color:         var(--text);
        white-space:   nowrap;
        overflow:      hidden;
        text-overflow: ellipsis;
    }
    .stat-label {
        font-size:      0.63rem;
        font-weight:    600;
        letter-spacing: 0.10em;
        text-transform: uppercase;
        color:          var(--muted);
        margin-top:     0.28rem;
    }
    .role-pill {
        display:        inline-block;
        background:     rgba(75,140,245,0.14);
        border:         1px solid rgba(75,140,245,0.26);
        color:          #7db3ff;
        font-size:      0.68rem;
        font-weight:    600;
        padding:        0.18rem 0.65rem;
        border-radius:  20px;
        font-family:    'DM Mono', monospace;
        letter-spacing: 0.05em;
    }

    /* ── Content panel ────────────────────────────────── */
    .content-panel {
        background:    var(--panel);
        border:        1px solid var(--border);
        border-radius: 15px;
        padding:       2.6rem 1.8rem;
        text-align:    center;
        margin:        0.8rem 0;
        position:      relative;
        overflow:      hidden;
    }
    .content-panel::before {
        content:        '';
        position:       absolute;
        inset:          0;
        background:     radial-gradient(ellipse 65% 55% at 50% 0%, rgba(75,140,245,0.05) 0%, transparent 70%);
        pointer-events: none;
    }
    .panel-icon  { font-size: 2.4rem; display: block; margin-bottom: 0.75rem; }
    .panel-title {
        font-family:   'Playfair Display', serif;
        font-size:     1.2rem;
        font-weight:   600;
        color:         var(--text);
        margin-bottom: 0.42rem;
    }
    .panel-desc {
        font-size:   0.83rem;
        color:       var(--muted);
        line-height: 1.65;
        max-width:   350px;
        margin:      0 auto 1.3rem;
    }
    .status-chip {
        display:        inline-flex;
        align-items:    center;
        gap:            5px;
        background:     rgba(56,205,170,0.09);
        border:         1px solid rgba(56,205,170,0.20);
        color:          var(--teal);
        font-size:      0.65rem;
        font-weight:    600;
        letter-spacing: 0.10em;
        text-transform: uppercase;
        padding:        0.26rem 0.75rem;
        border-radius:  20px;
        font-family:    'DM Mono', monospace;
    }
    .chip-dot {
        width: 5px; height: 5px;
        background:    var(--teal);
        border-radius: 50%;
        display:       inline-block;
        animation:     blink 2.2s ease-in-out infinite;
    }

    /* ── Page footer ──────────────────────────────────── */
    .page-footer {
        text-align:     center;
        color:          rgba(84,103,126,0.45);
        font-size:      0.65rem;
        font-family:    'DM Mono', monospace;
        letter-spacing: 0.07em;
        margin-top:     1.8rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


import streamlit.components.v1 as components

# Disable browser autocomplete on inputs
components.html(
    """
    <script>
    const observer = new MutationObserver(function() {
        const doc = window.parent.document;
        doc.querySelectorAll('input').forEach(i => i.setAttribute('autocomplete', 'off'));
        doc.querySelectorAll('form').forEach(f => f.setAttribute('novalidate', 'true'));
    });
    observer.observe(window.parent.document.body, { childList: true, subtree: true });
    </script>
    """,
    height=0,
    width=0
)
# ---------------------------------------------------------------------------
# UI — Login
# ---------------------------------------------------------------------------
def render_login():
    # ── Brand / logo block — pure HTML, safe to inject standalone
    st.markdown(
        """
        <div class="brand-header">
            <div class="cross-icon">⚕️</div>
            <div>
                <div class="brand-name">ClinicalView</div>
                <div class="brand-sub">Secure Portal · v2.1</div>
            </div>
        </div>
        <div class="card-divider"></div>
        <div class="section-label">Sign in to your account</div>
        """,
        unsafe_allow_html=True,
    )

    # ── Form — NOT nested inside a custom HTML div.
    #    Streamlit renders form elements in their own DOM nodes; the CSS above
    #    styles them via .stTextInput and .stFormSubmitButton selectors.
    with st.form("login_form", clear_on_submit=False):
        username  = st.text_input("Username", placeholder="Enter your username")
        password  = st.text_input("Password", type="password", placeholder="••••••••••••")
        submitted = st.form_submit_button("Sign In →", use_container_width=True)

    if submitted:
        if not username or not password:
            st.error("⚠️  Please enter both username and password.")
        else:
            with st.spinner("Verifying credentials…"):
                user = verify_user(username, password)
            if user is None:
                st.error("❌  Invalid username or password.")
            else:
                token = create_jwt(user)
                set_auth_cookie(token)
                st.success(f"✅  Welcome back, **{user.get('full_name', username)}**!")
                time.sleep(1.2)
                st.rerun()

    # ── Login footer
    st.markdown(
        """
        <div class="login-foot">
            <div class="dot-row">
                <span class="live-dot"></span>
                <span>Secure · Encrypted · HIPAA-aware</span>
            </div>
            <span>© 2026 ClinicalView</span>
        </div>
        """,
        unsafe_allow_html=True,
    )





# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    if "user" not in st.session_state:
        st.session_state.user = None

    controller = get_controller()
    token = controller.get(COOKIE_NAME)

    if token and not st.session_state.user:
        user_payload = get_current_user()
        if user_payload:
            st.session_state.user = {
                "_id": user_payload.get("user_id"),
                "role": user_payload.get("role", "Clinical"),
                "username": user_payload.get("username"),
                "full_name": user_payload.get("full_name", ""),
                "exp": user_payload.get("exp")
            }
        else:
            remove_auth_cookie()
            st.session_state.user = None
            st.rerun()
    elif not token and st.session_state.user:
        st.session_state.user = None

    if st.session_state.user:
        user = st.session_state.user
        role = user.get("role")

        st.sidebar.title(f"Welcome, {user.get('full_name') or user.get('username')}")
        st.sidebar.write(f"**Role:** {role}")

        if st.sidebar.button("🚪 Logout"):
            remove_auth_cookie()
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

        st.sidebar.markdown("---")
        st.sidebar.subheader("Navigation")

        if role == 'Clinical':
            menu_options = ["Dashboard", "View Patient Context", "Generate Summary"]
        elif role == 'Research':
            menu_options = ["Dashboard", "Query Anonymized Data", "View Aggregated Summaries"]
        elif role == 'Administrative':
            menu_options = ["Dashboard", "System Health", "Patient Billing", "Administrative Summaries"]
        elif role == 'Legal':
            menu_options = ["Dashboard", "Legal Queries"]
        else:
            menu_options = ["Dashboard"]

        choice = st.sidebar.radio("Go to", menu_options)

        if choice == "Dashboard":
            render_dashboard(st.session_state.user)
        elif choice == "View Patient Context":
            view_patient_context()
        elif choice == "Generate Summary":
            view_generate_summary()
        elif choice == "Query Anonymized Data":
            view_query_anonymized_data()
        elif choice == "View Aggregated Summaries":
            view_aggregated_summaries()
        elif choice == "System Health":
            view_system_health()
        elif choice == "Patient Billing":
            view_patient_billing()
        elif choice == "Administrative Summaries":
            view_admin_summaries()
        elif choice == "Legal Queries":
            view_legal_summaries()
    else:
        render_login()


if __name__ == "__main__":
    main()