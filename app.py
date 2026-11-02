import streamlit as st
import requests
import random
import time
import json
import os

st.set_page_config(page_title="Game Dev Copilot", page_icon="👾", layout="wide")

# --- FILE STORAGE LOGIC ---
SAVE_FILE = "saved_games.json"

def load_games():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_games(games_dict):
    with open(SAVE_FILE, "w") as f:
        json.dump(games_dict, f)

# --- CYBERPUNK CHAT UI ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;700&display=swap');
    
    .stApp { background-color: #0d1117; color: #c9d1d9; font-family: 'Fira Code', monospace; }
    h1, h2, h3 { color: #58a6ff; text-transform: uppercase; }
    
    .user-msg { background-color: #1f6feb; color: white; padding: 15px; border-radius: 10px 10px 0px 10px; margin-bottom: 10px; text-align: right; margin-left: 20%;}
    .ai-msg { background-color: #161b22; border: 1px solid #30363d; color: #c9d1d9; padding: 15px; border-radius: 10px 10px 10px 0px; margin-bottom: 10px; margin-right: 20%; font-family: monospace; white-space: pre-wrap;}
    
    .run-btn>button {
        background-color: #ff0040 !important; color: white !important; border: none !important; 
        font-family: 'Fira Code', monospace; font-weight: bold; font-size: 18px !important; 
        width: 100%; border-radius: 5px; padding: 15px !important;
        box-shadow: 0 0 15px rgba(255, 0, 64, 0.5); animation: pulse 2s infinite;
    }
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.7; } 100% { opacity: 1; } }
    
    .stButton>button {
        background-color: #238636; color: white; border: none; font-family: 'Fira Code', monospace; font-weight: bold; width: 100%; border-radius: 5px; padding: 10px;
    }
    .stButton>button:hover { background-color: #2ea043; color: white; }
    
    .stTextInput>div>div>input {
        background-color: #010409; color: #c9d1d9; border: 1px solid #30363d; font-family: 'Fira Code', monospace;
    }
    
    section[data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; }
    
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- STATE INITIALIZATION ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "I am your game dev AI. Tell me what game to build, and I'll write the Python code for you. You can then save it to your library!"}
    ]
if "code_to_run" not in st.session_state:
    st.session_state.code_to_run = ""

# Load from file on startup
if "saved_games" not in st.session_state:
    st.session_state.saved_games = load_games()

# --- SIDEBAR: SAVED GAMES LIBRARY ---
with st.sidebar:
    st.markdown("### 📂 My Saved Games")
    if not st.session_state.saved_games:
        st.write("No games saved yet.")
    else:
        for game_name in list(st.session_state.saved_games.keys()):
            col1, col2 = st.columns([4, 1])
            if col1.button(f"▶️ {game_name}", key=f"load_{game_name}"):
                st.session_state.code_to_run = st.session_state.saved_games[game_name]
                st.rerun()
            if col2.button("🗑️", key=f"del_{game_name}"):
                del st.session_state.saved_games[game_name]
                save_games(st.session_state.saved_games) # Update file
                st.rerun()

# --- MAIN UI ---
st.markdown("<h1>👾 Game Dev Copilot</h1>", unsafe_allow_html=True)

# --- LIVE VISUALS PANEL ---
st.write("### 🎨 Live Visual Effects")
col1, col2, col3, col4 = st.columns(4)
if col1.button("🎈 Balloons"): st.balloons()
if col2.button("❄️ Snow"): st.snow()
if col3.button("🎉 Confetti"):
    st.markdown("""
    <style>
        .confetti { position: fixed; top: -10px; width: 10px; height: 10px; background: red; animation: fall 3s linear infinite; z-index: 9999;}
        @keyframes fall { 100% { transform: translateY(100vh); } }
    </style>
    <div class="confetti" style="left: 10%; background: #f00; animation-delay: 0s;"></div>
    <div class="confetti" style="left: 30%; background: #0f0; animation-delay: 0.5s;"></div>
    <div class="confetti" style="left: 50%; background: #00f; animation-delay: 1s;"></div>
    <div class="confetti" style="left: 70%; background: #ff0; animation-delay: 1.5s;"></div>
    <div class="confetti" style="left: 90%; background: #0ff; animation-delay: 2s;"></div>
    """, unsafe_allow_html=True)
if col4.button("🔊 Coin Sound"):
    st.markdown("""<audio autoplay><source src="https://assets.mixkit.co/active_storage/sfx/2000/2000-preview.mp3" type="audio/mpeg"></audio>""", unsafe_allow_html=True)

st.divider()

# --- SPLIT SCREEN: CHAT AND GAMEPLAY ---
chat_col, game_col = st.columns([1, 1])

with chat_col:
    st.markdown("### 💬 AI Chat")
    
    # Display chat messages
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="user-msg">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="ai-msg">{msg["content"]}</div>', unsafe_allow_html=True)

    # Input
    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_input("Describe your game...", placeholder="e.g., Code a guessing game.")
        submit = st.form_submit_button("Send to AI")

    if submit and user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        with st.spinner("AI is coding..."):
            prompt = f"""
            You are an expert Streamlit game developer. 
            The user wants to build this: "{user_input}"
            
            Write the exact Python code needed to make this happen. 
            Use `st.balloons()`, `st.snow()`, or `st.toast()` to add visual flair.
            Only output the Python code block. Keep it under 30 lines.
            """
            try:
                response = requests.get(f"https://text.pollinations.ai/{requests.utils.quote(prompt)}", timeout=15)
                if response.status_code == 200:
                    ai_code = response.text.strip()
                    if ai_code.startswith("```python"): ai_code = ai_code[9:]
                    if ai_code.endswith("```"): ai_code = ai_code[:-3]
                    st.session_state.messages.append({"role": "assistant", "content": ai_code.strip()})
                else:
                    st.error("AI server busy.")
            except:
                st.error("Connection failed.")
        st.rerun()

    # Code Execution & Save Buttons
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "assistant":
        last_code = st.session_state.messages[-1]["content"]
        
        if "st." in last_code:
            st.markdown('<div class="run-btn">', unsafe_allow_html=True)
            if st.button("▶️ EXECUTE AI CODE"):
                st.session_state.code_to_run = last_code
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            
            # SAVE GAME (Now writes to physical file)
            with st.expander("💾 Save this Game"):
                game_name = st.text_input("Name your game:", placeholder="e.g., Space Clicker")
                if st.button("Save to Library"):
                    if game_name:
                        st.session_state.saved_games[game_name] = last_code
                        save_games(st.session_state.saved_games) # Save to JSON file
                        st.success(f"Saved '{game_name}' successfully to disk!")
                        time.sleep(1)
                        st.rerun()

with game_col:
    st.markdown("### 🎮 Gameplay Area")
    
    if st.session_state.code_to_run:
        game_container = st.container()
        
        with game_container:
            try:
                exec(st.session_state.code_to_run)
            except Exception as e:
                st.error(f"⚠️ The AI wrote code with an error:\n\n{e}")
                
        st.write("---")
        if st.button("🛑 Stop Game / Clear Screen"):
            st.session_state.code_to_run = ""
            st.rerun()
    else:
        st.info("No game running. Ask the AI to build one, or load a saved game from the sidebar!")
