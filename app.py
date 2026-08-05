import streamlit as st
import streamlit.components.v1 as components
import os
import base64
import time
import auth
import auth_ui
import database
import ast
from dotenv import load_dotenv
from education_agent.agents.orchestrator import Orchestrator

# Load environment variables
load_dotenv()

# Cache the Orchestrator so LLM client is reused
@st.cache_resource
def get_orchestrator():
    return Orchestrator()

# --- Page Config ---
st.set_page_config(
    page_title="AI Powered Smart Education System",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ================= PREMIUM BACKGROUND =================
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def add_premium_background():
    # Override with Solid High-Contrast Dark Theme Background
    st.markdown("""
    <style>
        [data-testid="stAppViewContainer"] {
            background-color: #0f172a !important;
            background-image: none !important;
        }
        body {
            background-color: #0f172a !important;
        }
        div[data-testid="stAppViewBlockContainer"] {
            background-color: transparent !important;
        }
    </style>
    """, unsafe_allow_html=True)

# Add background immediately
add_premium_background()

import uuid

# --- Session State Initialization ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = "Guest"
if "guest_chat_count" not in st.session_state:
    st.session_state.guest_chat_count = 0
if "messages" not in st.session_state:
    st.session_state.messages = []
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "Login" # Login, Signup, Forgot

# ================= CUSTOM CSS & JS INJECTION =================
def inject_custom_style():
    st.markdown(f"""
    <style>
    /* Hide Streamlit Default Elements (Footer, Menu, Header) */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    [data-testid="stDecoration"] {{display: none;}}
    
    /* Hide specific deployment/github icons */
    .stDeployButton {{display: none;}}
    [data-testid="stToolbar"],
    #MainMenu,
    .stAppDeployButton {{
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        pointer-events: none !important;
    }}
    .viewerBadge_container__1QSob {{display: none !important;}}

    /* PERMANENTLY BRIGHTEN ALL HEADER ICONS (Sidebar Toggle, etc) */
    header[data-testid="stHeader"] * {{
        opacity: 1 !important;
        visibility: visible !important;
        color: #ffffff !important;
        fill: #ffffff !important;
        stroke: #ffffff !important;
    }}
    
    /* RESTORE STRUCTURAL TOGGLE */
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="collapsedControl"] {{
        display: flex !important;
        visibility: visible !important;
        z-index: 1000000 !important;
        color: #ffffff !important;
        background-color: #1e293b !important;
        width: 56px !important;
        height: 56px !important;
        border-radius: 14px !important;
        border: 1px solid #334155 !important;
        transition: all 0.3s ease !important;
        cursor: pointer !important;
        pointer-events: auto !important;
        margin-top: 15px !important; 
        margin-left: 15px !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.4) !important;
        opacity: 1 !important; 
    }}
    
    [data-testid="stSidebarCollapsedControl"] svg,
    [data-testid="collapsedControl"] svg {{
        fill: #ffffff !important;
        stroke: #ffffff !important;
        opacity: 1 !important;
        width: 32px !important;
        height: 32px !important;
    }}
    
    header[data-testid="stHeader"] button,
    button[kind="header"] {{
        opacity: 1 !important;
        background-color: transparent !important;
    }}
    
    header[data-testid="stHeader"] button svg,
    button[kind="header"] svg,
    [data-testid="stSidebarCollapsedControl"] svg,
    [data-testid="collapsedControl"] svg {{
        opacity: 1 !important;
        width: 32px !important;
        height: 32px !important;
    }}

    /* NORMAL SIDEBAR TOGGLE HOVER */
    [data-testid="stSidebarCollapsedControl"]:hover,
    [data-testid="collapsedControl"]:hover,
    button[kind="header"]:hover {{
        background-color: #334155 !important;
        border-color: #475569 !important;
        transform: scale(1.08) !important;
        border-radius: 8px !important;
    }}

    /* =========================================
       SOLID DARK LAYERS
       ========================================= */
       
    html, body {{
        background-color: #0f172a !important;
        color: #f8fafc !important;
    }}

    /* 4. The inner content block (centering constraint) */
    .block-container {{
        background-color: transparent !important;
        padding-top: 2rem !important; /* Main content padding */
        max-width: 1100px;
    }}

    /* 5. Sidebar Styling */
    section[data-testid="stSidebar"] {{
        background-color: #020617 !important; 
        background: #020617 !important;
        border-right: 1px solid #1e293b !important;
        z-index: 99999 !important;
        box-shadow: 2px 0 10px rgba(0,0,0,0.5) !important;
    }}

    section[data-testid="stSidebar"] > div {{
        background-color: transparent !important;
        background: transparent !important;
    }}

    /* Force text color in sidebar */
    section[data-testid="stSidebar"] * {{
        color: #ffffff !important;
        font-weight: 500 !important;
    }}

    /* 6. Bottom Container */
    div[data-testid="stBottom"],
    div[data-testid="stBottom"] > div {{
        background-color: transparent !important;
        background: transparent !important;
        background-image: none !important;
        box-shadow: none !important;
        border: none !important;
    }}
    
    div[data-testid="stChatInputContainer"] {{
        background-color: transparent !important;
    }}
    
    div[data-testid="stChatInput"] {{
        background-color: transparent !important;
    }}
    
    .stChatInput {{
        background-color: transparent !important;
    }}
    
    /* Fix white bounding box around chat input */
    [data-testid="stChatInput"], 
    div.stChatContainer,
    .stChatFloatingInputContainer {{
        background-color: transparent !important;
        background: transparent !important;
    }}

    .stChatInput textarea {{
        background-color: #1e293b !important;
        color: #ffffff !important;
        caret-color: #ffffff !important;
        border: 2px solid #3b82f6 !important;
        border-radius: 24px !important;
        padding: 16px 20px !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3) !important;
        outline: none !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
    }}
    
    .stChatInput textarea::placeholder {{
        color: #94a3b8 !important;
        opacity: 1 !important;
    }}
    
    .stChatInput textarea:focus,
    .stChatInput textarea:active,
    .stChatInput textarea:focus-visible,
    .stChatInput textarea:focus-within {{
        background-color: #0f172a !important;
        border: 2px solid #60a5fa !important;
        border-color: #60a5fa !important;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4) !important;
        outline: none !important;
        outline-color: transparent !important;
    }}

    div[data-testid=\"stChatInput\"] *,
    div[data-testid=\"stChatInputContainer\"] * {{
        outline: none !important;
        outline-color: transparent !important;
    }}

    /* =========================================
       CHAT MESSAGE STYLING (Solid Dark Mode)
       ========================================= */
    [data-testid="stChatMessage"] {{
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 12px !important;
        padding: 1.5rem !important;
        margin-bottom: 1rem !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3) !important;
    }}
    
    [data-testid="stChatMessage"] * {{
        color: #ffffff !important;
    }}
    
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p {{
        font-size: 1.15rem !important;
        line-height: 1.7 !important;
        color: #ffffff !important;
        font-weight: 600 !important;
    }}

    /* =========================================
       GLOBAL BUTTON STYLING (Solid Dark Mode)
       ========================================= */
    .stButton > button {{
        background-color: #3b82f6 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.5rem 1rem !important;
        transition: all 0.2s ease !important;
    }}
    
    .stButton > button:hover {{
        background-color: #60a5fa !important;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4) !important;
        transform: translateY(-1px) !important;
    }}
    
    .stButton > button * {{
        color: #ffffff !important;
    }}

    /* =========================================
       LOGIN PAGE STYLING (Solid Dark Mode)
       ========================================= */
    [data-testid="stForm"] {{
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 16px !important;
        padding: 3rem 2rem !important;
        box-shadow: 0 15px 35px rgba(0,0,0,0.5) !important;
    }}
    
    [data-testid="stForm"] * {{
        color: #ffffff !important;
        font-size: 1.1rem !important;
        font-weight: 500 !important;
    }}
    
    /* FIX CAPTIONS & INSTRUCTIONS */
    [data-testid="stCaptionContainer"] * {{
        color: #f8fafc !important;
        font-size: 1rem !important;
        font-weight: 500 !important;
        opacity: 1 !important;
    }}
    
    [data-testid="InputInstructions"], 
    span[data-testid="InputInstructions"], 
    div[data-testid="InputInstructions"] {{
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
    }}
    
    div[data-baseweb="input"],
    div[data-baseweb="base-input"] {{
        background-color: #000000 !important;
        border-color: #475569 !important;
        border-radius: 8px !important;
    }}
    
    div[data-baseweb="input"] *,
    div[data-baseweb="base-input"] * {{
        color: #ffffff !important;
        background-color: transparent !important;
        background: transparent !important;
        -webkit-text-fill-color: #ffffff !important;
    }}
    
    [data-testid="stForm"] input,
    .stTextInput input,
    .stTextInput textarea {{
        background-color: transparent !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 1.15rem !important;
    }}
    
    /* GLOBAL MARKDOWN BRIGHTNESS */
    [data-testid="stMarkdownContainer"] * {{
        color: #ffffff !important;
    }}
    
    /* FIX STREAMLIT TABS BRIGHTNESS */
    button[data-baseweb="tab"] * {{
        color: #e2e8f0 !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        opacity: 1 !important;
    }}
    button[data-baseweb="tab"][aria-selected="true"] * {{
        color: #60a5fa !important;
    }}
    
    [data-testid="stForm"] button {{
        background-color: #3b82f6 !important;
        color: white !important;
        font-weight: bold !important;
        border: none !important;
        transition: all 0.3s ease !important;
    }}
    
    [data-testid="stForm"] button:hover {{
        background-color: #60a5fa !important;
        transform: scale(1.02) !important;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4) !important;
    }}

    /* =========================================
       RESPONSIVE DESIGN ADAPTERS
       ========================================= */
    @media (max-width: 768px) {{
        .sidebar-title {{
            font-size: 1.5rem !important;
            margin-top: -10px !important;
        }}
        div[data-testid="stAppViewBlockContainer"] {{
            padding-top: 2rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }}
        .stChatInput {{
            bottom: 10px !important;
        }}
    }}
    
    @media (min-width: 769px) {{
        .sidebar-title {{
            font-size: 2.2rem !important;
            margin-top: -20px !important;
        }}
    }}
    </style>
    """, unsafe_allow_html=True)

# Apply UI styles
inject_custom_style()



# --- Auth Logic (If Limit Reached or Manual Login) ---
if "force_login" not in st.session_state:
    st.session_state.force_login = False
if "show_profile" not in st.session_state:
    st.session_state.show_profile = False

LIMIT_REACHED = False # Chat limit removed as per user request

if LIMIT_REACHED or st.session_state.force_login:
    # Render the new premium Auth UI
    auth_ui.render_auth_page()
    
    if st.button("Back to Guest Mode", use_container_width=False):
        st.session_state.force_login = False
        st.rerun()
        
    st.stop() # Stop execution if limit reached or manual login requested

# --- Sidebar ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>🔮</h2>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; margin-top: -20px;'>AI Powered Smart Education System</h3>", unsafe_allow_html=True)
    st.markdown("---")
    
    # New Chat Button
    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.show_profile = False
        st.rerun()

    # Profile Dropdown
    if st.session_state.logged_in:
        with st.expander(f"👤 {st.session_state.username}"):
            if st.button("My Profile"):
                st.session_state.show_profile = True
                st.rerun()
                
            if st.button("Logout"):
                st.session_state.logged_in = False
                st.session_state.username = "Guest"
                st.session_state.messages = []
                st.session_state.show_profile = False
                st.rerun()
    else:
        st.info("👤 Guest Mode")
        # Chat limit logic removed
        
        if st.button("Login / Signup"):
             # We rely on LIMIT_REACHED logic or manual force
             st.session_state.force_login = True 
             st.rerun()

    st.markdown("---")
    
    # History Section
    if st.session_state.logged_in:
        st.markdown("### 🕒 History")
        history = database.get_user_history(st.session_state.username)
        if history:
            for item in history:
                # Use a unique key for each button
                if st.button(f"📄 {item['topic']}", key=str(item['_id'])):
                    # Load into chat
                    st.session_state.messages = [{"role": "user", "content": item['topic']}, 
                                                 {"role": "assistant", "content": item['full_content']}]
                    st.session_state.show_profile = False
                    st.rerun()
        else:
            st.caption("No history yet.")
    
    st.markdown("---")


# --- Profile View ---
if st.session_state.show_profile and st.session_state.logged_in:
    user_data = database.get_user(st.session_state.username)
    if user_data:
        st.markdown(f"""
        <div class="glass-card">
            <h1>👤 User Profile</h1>
            <p><strong>Username:</strong> {user_data['username']}</p>
            <p><strong>Email:</strong> {user_data.get('email', 'N/A')}</p>
            <p><strong>Member Since:</strong> {user_data.get('join_date', 'Unknown')}</p>
            <hr style="border-color: #333;">
            <p><em>Use the sidebar to view your learning history.</em></p>
        </div>
        """, unsafe_allow_html=True)
    st.stop()

# --- Main Interface ---
# Using a container for the scrollable content area
main_container = st.container()

with main_container:
    # Header (Only show if no content generated yet)
    if not st.session_state.messages:
        st.markdown("""
            <div style="text-align: center; margin-bottom: 3rem; margin-top: 5rem;">
                <h1 style="font-size: 4rem; font-weight: 900; color: #ffffff;">AI Powered Smart Education System</h1>
                <p style="font-size: 1.2rem; color: #94a3b8;">Empowering your learning journey with dynamic articles, flashcards, and interactive quizzes.</p>
            </div>
        """, unsafe_allow_html=True)

    # --- Helper: Render Content ---
    def render_content(content, msg_idx="new"):
        # ATTEMPT TO PARSE STRINGIFIED DICT (Recovery for old data)
        if isinstance(content, str) and content.strip().startswith("{") and "'article':" in content:
            try:
                content = ast.literal_eval(content)
            except:
                pass

        if isinstance(content, dict):
            # 1. Article
            st.markdown("""
            <div style="background: #1e293b; border-left: 5px solid #38bdf8; padding: 10px 15px; margin: 20px 0; border-radius: 4px;">
                <h3 style="margin: 0; color: #38bdf8; font-weight: bold;">📚 Course Material</h3>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(content.get('article', ''))
            
            # 2. Flashcards (Multimodal)
            flashcards = content.get('flashcards')
            if flashcards and 'flashcards' in flashcards:
                st.markdown("""
                <div style="background: #1e293b; border-left: 5px solid #a855f7; padding: 10px 15px; margin: 25px 0 15px 0; border-radius: 4px;">
                    <h3 style="margin: 0; color: #d8b4fe; font-weight: bold;">🎴 Concept Flashcards</h3>
                </div>
                """, unsafe_allow_html=True)
                # Create a horizontal scroll or grid for flashcards
                cols = st.columns(min(len(flashcards['flashcards']), 3))
                for idx, fc in enumerate(flashcards['flashcards']):
                    with cols[idx % 3]:
                        st.markdown(f"""
                        <div style="border: 1px solid #334155; border-radius: 12px; padding: 15px; background: #0f172a; margin-bottom: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
                            <h4 style="margin-top:0; color: #c084fc;">{fc['concept']}</h4>
                            <p style="font-size: 0.9rem; color: #e2e8f0;">{fc['description']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if fc.get('image_b64'):
                            st.image(f"data:image/png;base64,{fc['image_b64']}", use_container_width=True)
                st.markdown("---")

            # 3. Quiz (Improved UI)
            quiz = content.get('quiz')
            if quiz and 'questions' in quiz:
                st.markdown("""
                <div style="background: #1e293b; border-left: 5px solid #ec4899; padding: 10px 15px; margin: 25px 0 15px 0; border-radius: 4px;">
                    <h3 style="margin: 0; color: #f472b6; font-weight: bold;">🧠 Knowledge Check</h3>
                </div>
                """, unsafe_allow_html=True)
                st.markdown("""
                <style>
                .quiz-card {
                    background: #1e293b;
                    border: 1px solid #334155;
                    border-left: 4px solid #3b82f6;
                    border-radius: 12px;
                    padding: 20px;
                    margin-bottom: 20px;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
                    color: #ffffff;
                    font-size: 1.1rem;
                }
                .quiz-card p, .quiz-card label, .quiz-card div {
                    color: #ffffff !important;
                    font-weight: 500 !important;
                    font-size: 1.1rem !important;
                }
                </style>
                """, unsafe_allow_html=True)
                
                for idx, q in enumerate(quiz['questions']):
                    with st.container():
                        st.markdown(f'<div class="quiz-card">', unsafe_allow_html=True)
                        st.markdown(f"**Question {idx+1}:** {q['question']}")
                        
                        key = f"quiz_{msg_idx}_{idx}_{hash(str(q['question']))}"
                        answer = st.radio("Select your answer:", q['options'], key=key)
                        
                        if st.button(f"Submit Answer", key=f"btn_{key}"):
                            ans_clean = str(answer).strip().lower()
                            corr_clean = str(q['correct_answer']).strip().lower()
                            
                            # Robust matching: exact, or substring in either direction
                            is_correct = (ans_clean == corr_clean) or (ans_clean in corr_clean) or (corr_clean in ans_clean)
                            
                            if is_correct:
                                st.success(f"✅ **Correct!** {q.get('explanation', '')}")
                            else:
                                st.error(f"❌ **Incorrect.** The correct answer was **{q['correct_answer']}**. {q.get('explanation', '')}")
                        st.markdown('</div>', unsafe_allow_html=True)
                st.markdown("---")
        else:
            # Fallback for simple string messages
            st.markdown(content)

    # --- Chat Input at Top ---
    # We use chat_input which stays pinned to bottom, but the new content will render at the top!
    if prompt := st.chat_input("What do you want to learn today?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        if not os.getenv("GROQ_API_KEY"):
            st.error("❌ Groq API Key is missing.")
        else:
            with main_container:
                with st.chat_message("user"):
                    st.markdown(prompt)

                with st.chat_message("assistant"):
                    status_placeholder = st.empty()
                    
                    try:
                        status_placeholder.markdown("⚡ *Generating content...*")
                        final_content = get_orchestrator().run(prompt)
                        
                        status_placeholder.empty()
                        st.session_state.messages.append({"role": "assistant", "content": final_content})
                        
                        if st.session_state.logged_in:
                            database.save_chat_history(st.session_state.username, prompt, final_content)
                            
                        st.rerun()
                            
                    except Exception as e:
                        status_placeholder.empty()
                        st.error(f"An error occurred: {e}")

    # Display Chat in REVERSE chronological order
    if st.session_state.messages:
        for i, message in reversed(list(enumerate(st.session_state.messages))):
            with st.chat_message(message["role"]):
                render_content(message["content"], msg_idx=i)

