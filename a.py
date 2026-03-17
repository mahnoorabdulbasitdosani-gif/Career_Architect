import streamlit as st
import google.generativeai as genai
import json
import os
import time
from datetime import datetime
from dotenv import load_dotenv

# Loading configurations
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# 1. PAGE SETUP
st.set_page_config(page_title="Chef AI_Xora", page_icon="👨‍🍳", layout="wide")

# 2. UI/UX DESIGN (Background & Health Theme)
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), 
        url("https://images.unsplash.com/photo-1498837167922-ddd27525d352?q=80&w=2070");
        background-size: cover;
        background-attachment: fixed;
    }
    [data-testid="stSidebar"] {
        background-color: rgba(15, 15, 15, 0.95) !important;
        border-right: 1px solid #D4AF37;
    }
    .stExpander {
        border: none !important;
        background: transparent !important;
    }
    .stChatMessage {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(10px);
        border-radius: 12px !important;
        border: 1px solid rgba(212, 175, 55, 0.2) !important;
    }
    .inventory-card {
        background: rgba(46, 125, 50, 0.1);
        padding: 10px;
        border-radius: 8px;
        border-left: 4px solid #2e7d32;
        margin-bottom: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

if api_key:
    genai.configure(api_key=api_key)
else:
    st.error("API Key Missing! Please check your .env file.")
    st.stop()

# Assets
CHEF_NAME = "Chef AI_Xora"
INV_FILE = "inventory.json"
CHAT_FILE = "chat_memory.json"
# ICONS (Fixed Chef & Human)
CHEF_ICON = "https://cdn-icons-png.flaticon.com/512/3448/3448099.png"
USER_ICON = "https://cdn-icons-png.flaticon.com/512/3135/3135715.png"

# 3. HEALTH-CONSCIOUS AGENT LOGIC
SYSTEM_PROMPT = f"""
You are {CHEF_NAME}, a Strategic & Health-Conscious AI Kitchen Agent.
Core Directives:
1. Health First: Always prioritize nutritious, low-calorie, and balanced meal plans.
2. Waste Warrior: Use items from inventory expiring soonest.
3. Memory: Strictly avoid ingredients the user dislikes.
4. Budget: Provide shopping lists in PKR within user budget.
5. Outsmart: Suggest healthy alternatives (e.g., honey instead of sugar).
"""

# Helper Functions
def load_data(file):
    if os.path.exists(file) and os.path.getsize(file) > 0:
        with open(file, "r") as f: return json.load(f)
    return {} if "inventory" in file else []

def save_data(file, data):
    with open(file, "w") as f: json.dump(data, f)

# 4. SIDEBAR
with st.sidebar:
    st.image(CHEF_ICON, width=100)
    st.markdown("<h2 style='color:#D4AF37;'>Chief Kitchen</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.subheader("🍏 Health & Inventory")
    with st.expander("Add New Ingredient"):
        item = st.text_input("Item Name")
        expiry = st.date_input("Expiry Date")
        if st.button("Track Item"):
            inv = load_data(INV_FILE)
            inv[item] = str(expiry)
            save_data(INV_FILE, inv)
            st.success(f"{item} is now tracked!")

    st.markdown("### ⚠️ Expiring Soon")
    inventory = load_data(INV_FILE)
    for itm, exp in inventory.items():
        st.markdown(f"""<div class="inventory-card"><b>{itm}</b><br><small>Expiry: {exp}</small></div>""", unsafe_allow_html=True)

    st.markdown("---")
    if st.button("🗑️ Clear Chat"):
        if os.path.exists(CHAT_FILE): os.remove(CHAT_FILE)
        if "chat" in st.session_state: del st.session_state.chat
        st.rerun()

    st.markdown(f"<div style='margin-top:20px;'><p style='color:#888; font-size:0.8rem;'>Developed by</p><p style='font-weight:600; color:white;'>Mahnoor Abdul Basit</p></div>", unsafe_allow_html=True)

# 5. MAIN INTERFACE
st.title(f"👨‍🍳 {CHEF_NAME}")
st.caption("Your Strategic Health-Conscious Meal Planner")

if "chat" not in st.session_state:
    model = genai.GenerativeModel('gemini-2.5-flash-lite', system_instruction=SYSTEM_PROMPT)
    st.session_state.chat = model.start_chat(history=load_data(CHAT_FILE))

# Display Chat History with FIXED Chef Icon
for message in st.session_state.chat.history:
    # Checking role and applying correct avatar
    msg_avatar = USER_ICON if message.role == "user" else CHEF_ICON
    with st.chat_message(message.role, avatar=msg_avatar):
        st.markdown(message.parts[0].text)

# Agent Input & Response
if prompt := st.chat_input("Ask Chef AI_Xora for a healthy meal plan..."):
    # Display user message
    with st.chat_message("user", avatar=USER_ICON):
        st.markdown(prompt)
    
    # Interaction State
    with st.spinner(f"{CHEF_NAME} is thinking and preparing your healthy meal..."):
        try:
            # Building context with Inventory & Health goal
            current_inv = load_data(INV_FILE)
            context = f"Inventory: {current_inv}. User prompt: {prompt}. Focus on health and waste reduction."
            
            response = st.session_state.chat.send_message(context)
            
            # Display assistant response with Chef Icon
            with st.chat_message("assistant", avatar=CHEF_ICON):
                st.markdown(response.text)
            
            # Save history
            history_to_save = [{"role": m.role, "parts": [{"text": m.parts[0].text}]} for m in st.session_state.chat.history]
            save_data(CHAT_FILE, history_to_save)
        except Exception as e:
            st.error(f"Error: {e}")