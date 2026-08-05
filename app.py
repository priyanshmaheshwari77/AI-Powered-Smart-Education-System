import sys
import traceback

try:
    import app_core
except Exception:
    import streamlit as st
    st.error("FATAL ERROR ON BOOT:")
    st.error(traceback.format_exc())
