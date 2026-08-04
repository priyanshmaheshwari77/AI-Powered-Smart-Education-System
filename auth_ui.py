import streamlit as st
import time
import auth

def render_custom_css():
    st.markdown("""
        <style>
            /* The Auth Card is now handled by the Light Mode global css */
            .glass-card {
                background: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 16px;
                padding: 2rem;
                box-shadow: 0 10px 25px rgba(0,0,0,0.05);
                text-align: center;
                animation: fadeIn 0.4s ease-in-out;
            }
            .glass-card * {
                color: #111111 !important;
            }
            .stTextInput input {
                background-color: #f8fafc !important;
                border: 1px solid #cbd5e1 !important;
                color: #111111 !important;
                border-radius: 8px;
                padding: 10px;
                font-weight: 500 !important;
            }
            
            .stTextInput input:focus {
                border-color: #2563eb !important;
                box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2) !important;
            }
            
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
        </style>
    """, unsafe_allow_html=True)

def render_login_form():
    st.markdown("## 👋 Welcome Back")
    st.caption("Please login to access your learning history.")
    
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
    st.markdown("## 🚀 Create Account")
    st.caption("Join EduAgent to save your courses forever.")
    
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
    st.markdown("## 🔐 Reset Password")
    st.caption("Don't worry, it happens to the best of us.")
    
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
        # Glassmorphic Container Start
        st.markdown('<div class="glass-card" style="padding-top: 1rem;">', unsafe_allow_html=True)
        
        # Auth Mode Switcher (Tabs)
        tabs = st.tabs(["Login", "Sign Up", "Recovery"])
        
        with tabs[0]:
            render_login_form()
            
        with tabs[1]:
            render_signup_form()
            
        with tabs[2]:
            render_forgot_password()
            
        st.markdown('</div>', unsafe_allow_html=True)
