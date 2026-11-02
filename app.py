import streamlit as st
import random
import math

st.set_page_config(page_title="Tic-Tac-Toe AI", page_icon="❌", layout="centered")

# --- MODERN UI CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@700;900&display=swap');
    
    .stApp { background-color: #1a1a2e; color: #ffffff; font-family: 'Nunito', sans-serif; }
    h1, h2, h3 { text-align: center; color: #e94560; text-transform: uppercase; letter-spacing: 2px; }
    
    /* Grid Buttons */
    .stButton>button {
        height: 80px; width: 100%; font-size: 40px; font-weight: 900; border-radius: 10px;
        background-color: #16213e; color: #e94560; border: 2px solid #0f3460; transition: 0.2s;
    }
    .stButton>button:hover { background-color: #0f3460; border-color: #e94560; }
    
    .stButton>button:disabled { background-color: #1a1a2e; color: #0f3460; border: 1px solid #0f3460; }
    
    .status-box { text-align: center; font-size: 24px; font-weight: bold; margin: 20px 0; padding: 15px; border-radius: 10px; background-color: #0f3460; }
    
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>❌ Tic-Tac-Toe AI ⭕</h1>", unsafe_allow_html=True)

# --- THE MINIMAX AI ENGINE ---
def check_winner(board, size):
    # Check rows and columns
    for i in range(size):
        if board[i*size:(i+1)*size].count(board[i*size]) == size and board[i*size] != "":
            return board[i*size]
        if [board[j*size + i] for j in range(size)].count(board[i]) == size and board[i] != "":
            return board[i]
    # Check diagonals
    if [board[i*size + i] for i in range(size)].count(board[0]) == size and board[0] != "":
        return board[0]
    if [board[i*size + (size-1-i)] for i in range(size)].count(board[size-1]) == size and board[size-1] != "":
        return board[size-1]
    return None

def is_full(board):
    return "" not in board

def get_empty_cells(board):
    return [i for i, spot in enumerate(board) if spot == ""]

def minimax(board, depth, is_maximizing, size, ai_player, human_player, alpha, beta):
    winner = check_winner(board, size)
    if winner == ai_player: return 10 - depth
    elif winner == human_player: return depth - 10
    elif is_full(board): return 0
    
    if is_maximizing:
        best_score = -math.inf
        for i in get_empty_cells(board):
            board[i] = ai_player
            score = minimax(board, depth + 1, False, size, ai_player, human_player, alpha, beta)
            board[i] = ""
            best_score = max(score, best_score)
            alpha = max(alpha, score)
            if beta <= alpha: break
        return best_score
    else:
        best_score = math.inf
        for i in get_empty_cells(board):
            board[i] = human_player
            score = minimax(board, depth + 1, True, size, ai_player, human_player, alpha, beta)
            board[i] = ""
            best_score = min(score, best_score)
            beta = min(beta, score)
            if beta <= alpha: break
        return best_score

def get_best_move(board, size, difficulty):
    empty_cells = get_empty_cells(board)
    if not empty_cells: return None
    
    # EASY: 80% chance to pick a random move (can be stupid)
    if difficulty == "Easy" and random.random() < 0.8:
        return random.choice(empty_cells)
    
    # MEDIUM: 30% chance to pick a random move (makes mistakes sometimes)
    if difficulty == "Medium" and random.random() < 0.3:
        return random.choice(empty_cells)
        
    # IMPOSSIBLE (or the 20%/70% chance for Easy/Medium): Use Minimax
    best_score = -math.inf
    best_move = random.choice(empty_cells)
    
    for i in empty_cells:
        board[i] = "O"
        score = minimax(board, 0, False, size, "O", "X", -math.inf, math.inf)
        board[i] = ""
        if score > best_score:
            best_score = score
            best_move = i
            
    return best_move

# --- GAME STATE ---
if "board" not in st.session_state:
    st.session_state.size = 3
    st.session_state.board = [""] * 9
    st.session_state.turn = "X"
    st.session_state.winner = None
    st.session_state.difficulty = "Medium"

# --- SETTINGS ---
if st.session_state.turn == "X" and not st.session_state.winner:
    with st.sidebar:
        st.header("⚙️ Game Settings")
        
        grid_size = st.selectbox("Grid Size", [3, 4, 5], index=0)
        difficulty = st.selectbox("AI Difficulty", ["Easy", "Medium", "Impossible"], index=1)
        
        if st.button("🔄 Restart Game", type="primary", use_container_width=True):
            st.session_state.size = grid_size
            st.session_state.board = [""] * (grid_size * grid_size)
            st.session_state.turn = "X"
            st.session_state.winner = None
            st.session_state.difficulty = difficulty
            st.rerun()

# --- RENDER GRID ---
status_text = ""
if st.session_state.winner:
    if st.session_state.winner == "X":
        status_text = "🎉 YOU WIN! (How did you do that?!)"
    elif st.session_state.winner == "O":
        status_text = "🤖 AI WINS!"
    else:
        status_text = "🤝 IT'S A DRAW!"
else:
    if st.session_state.turn == "X":
        status_text = "🟢 Your Turn (X)"
    else:
        status_text = "🔴 AI is thinking... (O)"

st.markdown(f'<div class="status-box">{status_text}</div>', unsafe_allow_html=True)

# Create the grid
size = st.session_state.size
cols = st.columns(size)

for i in range(size * size):
    with cols[i % size]:
        val = st.session_state.board[i]
        if val == "":
            if st.button(" ", key=f"cell_{i}", disabled=st.session_state.turn == "O" or st.session_state.winner is not None):
                # Human Move
                st.session_state.board[i] = "X"
                
                # Check win
                st.session_state.winner = check_winner(st.session_state.board, size)
                if not st.session_state.winner and not is_full(st.session_state.board):
                    st.session_state.turn = "O"
                elif is_full(st.session_state.board) and not st.session_state.winner:
                    st.session_state.winner = "Draw"
                st.rerun()
        else:
            st.button(val, key=f"cell_{i}", disabled=True)

# --- AI TURN ---
if st.session_state.turn == "O" and not st.session_state.winner:
    with st.spinner("AI is calculating..."):
        time.sleep(0.5) # Tiny delay to make it feel natural
        ai_move = get_best_move(st.session_state.board, size, st.session_state.difficulty)
        
        if ai_move is not None:
            st.session_state.board[ai_move] = "O"
            
            # Check win
            st.session_state.winner = check_winner(st.session_state.board, size)
            if not st.session_state.winner and not is_full(st.session_state.board):
                st.session_state.turn = "X"
            elif is_full(st.session_state.board) and not st.session_state.winner:
                st.session_state.winner = "Draw"
            st.rerun()
