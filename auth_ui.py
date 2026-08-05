import streamlit as st
import time
import auth

def render_custom_css():
    pass

def render_login_form():
    st.markdown("<div style='text-align: center;'><h2 style='margin-bottom: 0px; font-weight: 700;'>Welcome Back</h2><p style='color: #94a3b8; margin-top: 5px; font-size: 0.95rem; font-weight: 500;'>Please login to access your learning history.</p></div>", unsafe_allow_html=True)
    
    with st.form("login_form"):
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        submitted = st.form_submit_button("Log In", use_container_width=True, type="primary")
        
        if submitted:
            if not username or not password:
                st.error("Please fill in all fields.")
            else:
                success, msg = auth.login_user(username, password)
                if success:
                    st.success(msg)
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.force_login = False  # Ensure redirected to chat
                    st.rerun()
                else:
                    st.error(msg)

def render_signup_form():
    st.markdown("<div style='text-align: center;'><h2 style='margin-bottom: 0px; font-weight: 700;'>Create Account</h2><p style='color: #94a3b8; margin-top: 5px; font-size: 0.95rem; font-weight: 500;'>Join EduAgent to save your courses forever.</p></div>", unsafe_allow_html=True)
    
    with st.form("signup_form"):
        new_user = st.text_input("Choose Username", placeholder="e.g. learner123")
        new_email = st.text_input("Email Address", placeholder="name@example.com")
        new_pass = st.text_input("Choose Password", type="password")
        
        submitted = st.form_submit_button("Sign Up", use_container_width=True, type="primary")
        
        if submitted:
            if not new_user or not new_pass:
                st.error("Username and Password are required.")
            else:
                success, msg = auth.signup_user(new_user, new_pass, new_email)
                if success:
                    st.success("Account created! Logging you in...")
                    # Auto Login Logic
                    st.session_state.logged_in = True
                    st.session_state.username = new_user
                    st.session_state.force_login = False  # Ensure redirected to chat
                    time.sleep(1) # lush ux delay
                    st.rerun()
                else:
                    st.error(msg)

def render_forgot_password():
    st.markdown("<div style='text-align: center;'><h2 style='margin-bottom: 0px; font-weight: 700;'>Reset Password</h2><p style='color: #94a3b8; margin-top: 5px; font-size: 0.95rem; font-weight: 500;'>Don't worry, it happens to the best of us.</p></div>", unsafe_allow_html=True)
    
    with st.form("reset_form"):
        f_user = st.text_input("Username")
        n_pass = st.text_input("New Password", type="password")
        
        submitted = st.form_submit_button("Update Password", use_container_width=True)
        
        if submitted:
            if auth.update_password(f_user, n_pass):
                st.success("Password updated! Please login.")
                st.session_state.auth_mode = "Login"
                st.rerun()
            else:
                st.error("User not found.")

def render_auth_page():
    """Main entry point for auth rendering"""
    render_custom_css()
    
    # Center the card using columns
    col1, col2, col3 = st.columns([1, 1.5, 1])
    
    with col2:
        # Hyper-localized styling to utterly destroy the legacy red line and force centering
        st.markdown("""
            <style>
                div[data-testid="stTabs"] div[data-baseweb="tab-list"] {
                    justify-content: center !important;
                    border-bottom: 0px solid transparent !important;
                    margin-bottom: 0px !important;
                }
                div[data-testid="stTabs"] button[data-baseweb="tab"] {
                    border-bottom-width: 0px !important;
                }
                div[data-testid="stTabs"] [data-baseweb="tab-highlight"], 
                div[data-testid="stTabs"] [data-baseweb="tab-border"] {
                    display: none !important;
                    visibility: hidden !important; 
                }
                div[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] {
                    border-bottom: 3px solid #3b82f6 !important;
                }
            </style>
        """, unsafe_allow_html=True)
        # Auth Mode Switcher (Tabs)
        tabs = st.tabs(["Login", "Sign Up", "Recovery"])
        
        with tabs[0]:
            render_login_form()
            
        with tabs[1]:
            render_signup_form()
            
        with tabs[2]:
            render_forgot_password()
