import streamlit as st
import requests
import time
import json
import os
import random

st.set_page_config(page_title="Game Dev Copilot", page_icon="👾", layout="wide")

# --- PASTE YOUR *NEW* TOGETHER AI KEY HERE ---
TOGETHER_API_KEY = "key_CgeBE2peok5kXgojctPRo"

# --- FILE STORAGE LOGIC ---
SAVE_FILE = "saved_games.json"
def load_games():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r") as f: return json.load(f)
        except: return {}
    return {}
def save_games(games_dict):
    with open(SAVE_FILE, "w") as f: json.dump(games_dict, f)

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
    
    section[data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; }
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- THE AI ENGINE (TOGETHER AI) ---
def generate_code_with_ai(user_prompt):
    url = "https://api.together.xyz/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    system_prompt = """
    You are an expert Streamlit Python developer. 
    The user will describe a mini-game or visual effect they want.
    You must write the Python code to make it happen.
    
    RULES:
    1. Use `st.button()`, `st.write()`, and `st.balloons()` or `st.snow()` for visuals.
    2. Only output the Python code. Do not write any conversational text or markdown formatting like ```python.
    3. Keep the code under 30 lines so it runs fast.
    4. Assume `import streamlit as st` and `import random` are already imported.
    """
    
    payload = {
        "model": "meta-llama/Llama-3-70b-chat-hf",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 500
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        if response.status_code == 200:
            code = response.json()['choices'][0]['message']['content'].strip()
            if code.startswith("```python"): code = code[9:]
            if code.startswith("```"): code = code[3:]
            if code.endswith("```"): code = code[:-3]
            return code.strip()
        else:
            return f"Error: API returned {response.status_code}. Check your key."
    except Exception as e:
        return f"Error: {str(e)}"

# --- STATE INITIALIZATION ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "I am your AI Game Dev. Tell me any game to build (e.g., 'Make a snake game', 'A text adventure', 'A clicker game'). I will write the code instantly!"}
    ]
if "code_to_run" not in st.session_state:
    st.session_state.code_to_run = ""
if "saved_games" not in st.session_state:
    st.session_state.saved_games = load_games()

# --- SIDEBAR: SAVED GAMES ---
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
                save_games(st.session_state.saved_games)
                st.rerun()

# --- MAIN UI ---
st.markdown("<h1>👾 Game Dev Copilot</h1>", unsafe_allow_html=True)

if TOGETHER_API_KEY == "PASTE_YOUR_NEW_KEY_HERE":
    st.error("⚠️ Please paste your NEW Together AI Key on line 12 of the code to enable the AI.")
    st.stop()

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
    
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="user-msg">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="ai-msg">{msg["content"]}</div>', unsafe_allow_html=True)

    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_input("Describe your game...", placeholder="e.g., Make a snake game")
        submit = st.form_submit_button("Send to AI")

    if submit and user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        with st.spinner("AI is coding your game..."):
            ai_code = generate_code_with_ai(user_input)
            st.session_state.messages.append({"role": "assistant", "content": ai_code})
            
        st.rerun()

    if st.session_state.messages and st.session_state.messages[-1]["role"] == "assistant":
        last_code = st.session_state.messages[-1]["content"]
        
        if "st." in last_code and "Error" not in last_code:
            st.markdown('<div class="run-btn">', unsafe_allow_html=True)
            if st.button("▶️ EXECUTE AI CODE"):
                st.session_state.code_to_run = last_code
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            
            with st.expander("💾 Save this Game"):
                game_name = st.text_input("Name your game:", placeholder="e.g., Snake Game")
                if st.button("Save to Library"):
                    if game_name:
                        st.session_state.saved_games[game_name] = last_code
                        save_games(st.session_state.saved_games)
                        st.success(f"Saved '{game_name}' successfully!")
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
        st.info("No game running. Ask the AI to build one!")
