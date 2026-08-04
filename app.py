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
    try:
        bin_str = get_base64_of_bin_file('background.png')
        bg_img_css = f"""
        <style>
        [data-testid="stAppViewContainer"] {{
            background-image: url("data:image/png;base64,{bin_str}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            background-repeat: no-repeat;
        }}
        /* Ensure transparency for internal blocks */
        div[data-testid="stAppViewBlockContainer"] {{
            background-color: transparent !important;
            background: transparent !important;
        }}
        </style>
        """
        st.markdown(bg_img_css, unsafe_allow_html=True)
    except Exception as e:
        # Fallback to existing glow if image not found
        st.markdown("""
        <div class="purple-glow top-left"></div>
        <div class="purple-glow bottom-right"></div>
        <div class="purple-glow center-left"></div>
        <style>
            .purple-glow {
                position: fixed;
                width: 1000px;
                height: 1000px;
                border-radius: 50%;
                background: radial-gradient(circle, rgba(138, 43, 226, 0.3) 0%, rgba(0, 0, 0, 0) 70%);
                filter: blur(140px);
                z-index: -1;
                pointer-events: none;
            }
            .top-left {
                top: -400px;
                left: -400px;
            }
            .bottom-right {
                bottom: -400px;
                right: -400px;
            }
            .center-left {
                top: 50%;
                left: -600px;
                transform: translateY(-50%);
                width: 800px;
                height: 800px;
                background: radial-gradient(circle, rgba(138, 43, 226, 0.15) 0%, rgba(0, 0, 0, 0) 70%);
            }
            body {
                background-color: #000000 !important;
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
    [data-testid="stToolbar"] {{
        visibility: visible !important;
        background-color: transparent !important;
    }}
    [data-testid="stHeader"] {{
        visibility: visible !important;
        background-color: transparent !important;
    }}
    .viewerBadge_container__1QSob {{display: none !important;}}

    /* FORCE VISIBILITY OF SIDEBAR TOGGLE - Natural Position */
    [data-testid="stSidebarCollapsedControl"] {{
        display: flex !important;
        visibility: visible !important;
        z-index: 1000000 !important;
        color: white !important;
        background-color: rgba(255, 255, 255, 0.1) !important;
        width: 44px !important;
        height: 44px !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        backdrop-filter: blur(5px) !important;
        transition: all 0.3s ease !important;
        cursor: pointer !important;
        pointer-events: auto !important;
        margin-top: 10px !important; 
        margin-left: 10px !important;
    }}
    
    [data-testid="stSidebarCollapsedControl"]:hover {{
        background-color: rgba(255, 255, 255, 0.2) !important;
        border-color: white !important;
        transform: scale(1.05) !important;
    }}
    
    /* Ensure the icon inside is visible */
    [data-testid="stSidebarCollapsedControl"] svg {{
        fill: white !important;
        stroke: white !important;
        width: 24px !important;
        height: 24px !important;
    }}

    /* =========================================
       FORCE TRANSPARENCY ON ALL STREAMLIT LAYERS
       ========================================= */
    
    /* Force transparency on main containers */
    div[data-testid="stAppViewBlockContainer"] {{
        background-color: transparent !important;
        background: transparent !important;
    }}

    html, body {{
        background-color: transparent !important;
    }}

    /* 3. Background Styling is handled by add_premium_background */
    
    /* 4. The inner content block (centering constraint) */
    .block-container {{
        background-color: transparent !important;
        padding-top: 2rem !important; /* Main content padding */
        max-width: 1100px;
    }}

    /* 5. Sidebar transparency & Positioning */
    /* 5. Sidebar transparency & Positioning */
    section[data-testid="stSidebar"] {{
        background-color: rgba(0, 0, 0, 0.1) !important; 
        background: rgba(0, 0, 0, 0.1) !important;
        backdrop-filter: blur(1px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
        z-index: 99999 !important;
    }}

    section[data-testid="stSidebar"] > div {{
        background-color: transparent !important;
        background: transparent !important;
    }}

    /* Force text color in sidebar */
    section[data-testid="stSidebar"] * {{
        color: white !important;
    }}

    /* Move sidebar content up */
    section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] {{
        padding-top: 1rem !important;
        gap: 0.5rem !important;
    }}
    
    /* 6. Bottom Container - FORCE TRANSPARENCY */
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
    
    .stChatInput textarea {{
        background-color: rgba(15, 20, 30, 0.95) !important;
        color: #eeeeee !important;
        caret-color: #ffffff !important;
        border: 2px solid rgba(0, 200, 83, 0.6) !important;
        border-radius: 24px !important;
        padding: 14px 20px !important;
        box-shadow: 0 0 8px rgba(0, 200, 83, 0.15) !important;
        outline: none !important;
    }}
    
    .stChatInput textarea:focus,
    .stChatInput textarea:active,
    .stChatInput textarea:focus-visible,
    .stChatInput textarea:focus-within {{
        background-color: rgba(15, 20, 30, 1.0) !important;
        border: 2px solid rgba(0, 200, 83, 0.9) !important;
        border-color: rgba(0, 200, 83, 0.9) !important;
        box-shadow: 0 0 12px rgba(0, 200, 83, 0.3) !important;
        outline: none !important;
        outline-color: transparent !important;
    }}

    /* Kill ALL red/orange Streamlit focus rings on chat input */
    div[data-testid=\"stChatInput\"] *,
    div[data-testid=\"stChatInputContainer\"] * {{
        outline: none !important;
        outline-color: transparent !important;
    }}
    
    div[data-testid=\"stChatInput\"],
    div[data-testid=\"stChatInput\"] > div,
    div[data-testid=\"stChatInputContainer\"],
    div[data-testid=\"stChatInputContainer\"] > div {{
        border-color: rgba(0, 200, 83, 0.6) !important;
        outline: none !important;
    }}
    
    div[data-testid=\"stChatInput\"]:focus-within,
    div[data-testid=\"stChatInputContainer\"]:focus-within {{
        border-color: rgba(0, 200, 83, 0.9) !important;
        box-shadow: 0 0 12px rgba(0, 200, 83, 0.3) !important;
        outline: none !important;
    }}

    /* Override Streamlit's default red/orange bottom border on chat input container */
    .stChatInput > div {{
        border-color: rgba(0, 200, 83, 0.6) !important;
        outline: none !important;
    }}
    
    .stChatInput > div:focus-within {{
        border-color: rgba(0, 200, 83, 0.9) !important;
        box-shadow: 0 0 12px rgba(0, 200, 83, 0.3) !important;
    }}

    /* =========================================
       CHAT MESSAGE STYLING
       ========================================= */
    [data-testid="stChatMessage"] {{
        background-color: rgba(0, 0, 0, 0.7) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 15px !important;
        padding: 1.5rem !important;
        margin-bottom: 1rem !important;
        backdrop-filter: blur(10px) !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3) !important;
    }}
    
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p {{
        font-size: 1.05rem !important;
        line-height: 1.6 !important;
    }}

    /* =========================================
       LOGIN PAGE STYLING (Dark Glassmorphism)
       ========================================= */
    [data-testid="stForm"] {{
        background-color: rgba(0, 0, 0, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 20px !important;
        padding: 3rem 2rem !important;
        box-shadow: 0 15px 35px rgba(0,0,0,0.5) !important;
        backdrop-filter: blur(10px) !important;
    }}
    
    [data-testid="stForm"] input {{
        background-color: rgba(255, 255, 255, 0.05) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }}
    
    [data-testid="stForm"] button {{
        background-color: #ffffff !important;
        color: black !important;
        font-weight: bold !important;
        border: none !important;
        transition: all 0.3s ease !important;
    }}
    
    [data-testid="stForm"] button:hover {{
        transform: scale(1.02) !important;
        box-shadow: 0 0 15px rgba(255, 255, 255, 0.3) !important;
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
                <h1 style="font-size: 4rem; font-weight: 800; background: -webkit-linear-gradient(#00f2fe, #4facfe); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">AI Powered Smart Education System</h1>
                <p style="font-size: 1.2rem; color: #888;">Empowering your learning journey with dynamic articles, flashcards, and interactive quizzes.</p>
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
            <div style="background: linear-gradient(90deg, rgba(0, 242, 254, 0.2) 0%, transparent 100%); border-left: 5px solid #00f2fe; padding: 10px 15px; margin: 20px 0; border-radius: 4px;">
                <h3 style="margin: 0; color: #00f2fe; text-shadow: 0 0 10px rgba(0,242,254,0.5);">📚 Course Material</h3>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(content.get('article', ''))
            
            # 2. Flashcards (Multimodal)
            flashcards = content.get('flashcards')
            if flashcards and 'flashcards' in flashcards:
                st.markdown("""
                <div style="background: linear-gradient(90deg, rgba(168, 85, 247, 0.2) 0%, transparent 100%); border-left: 5px solid #A855F7; padding: 10px 15px; margin: 25px 0 15px 0; border-radius: 4px;">
                    <h3 style="margin: 0; color: #d8b4fe; text-shadow: 0 0 10px rgba(168,85,247,0.5);">🎴 Concept Flashcards</h3>
                </div>
                """, unsafe_allow_html=True)
                # Create a horizontal scroll or grid for flashcards
                cols = st.columns(min(len(flashcards['flashcards']), 3))
                for idx, fc in enumerate(flashcards['flashcards']):
                    with cols[idx % 3]:
                        st.markdown(f"""
                        <div style="border: 1px solid rgba(255,255,255,0.1); border-radius: 15px; padding: 15px; background: rgba(255,255,255,0.05); margin-bottom: 10px;">
                            <h4 style="margin-top:0; color: #A855F7;">{fc['concept']}</h4>
                            <p style="font-size: 0.9rem;">{fc['description']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if fc.get('image_b64'):
                            st.image(f"data:image/png;base64,{fc['image_b64']}", use_container_width=True)
                st.markdown("---")

            # 3. Quiz (Improved UI)
            quiz = content.get('quiz')
            if quiz and 'questions' in quiz:
                st.markdown("""
                <div style="background: linear-gradient(90deg, rgba(236, 72, 153, 0.2) 0%, transparent 100%); border-left: 5px solid #EC4899; padding: 10px 15px; margin: 25px 0 15px 0; border-radius: 4px;">
                    <h3 style="margin: 0; color: #fbcfe8; text-shadow: 0 0 10px rgba(236,72,153,0.5);">🧠 Knowledge Check</h3>
                </div>
                """, unsafe_allow_html=True)
                st.markdown("""
                <style>
                .quiz-card {
                    background: linear-gradient(145deg, rgba(30,40,60,0.5), rgba(15,20,30,0.8));
                    border: 1px solid rgba(0, 255, 204, 0.2);
                    border-left: 4px solid #00f2fe;
                    border-radius: 12px;
                    padding: 20px;
                    margin-bottom: 20px;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
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

