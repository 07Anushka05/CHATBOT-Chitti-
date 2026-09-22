import streamlit as st
from ollama import chat
from datetime import datetime
import json
import os
import re
from pathlib import Path
from streamlit_mic_recorder import speech_to_text
from database import (
    register_user, login_user, get_user_info, create_chat_session,
    save_message, get_user_sessions, get_session_messages, delete_session,
    update_session_title
)

# Page configuration
st.set_page_config(
    page_title="Chitti - Your Personal AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================= SESSION STATE =================
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True 
if "live_wallpaper" not in st.session_state:
    st.session_state.live_wallpaper = True # NEW: Live wallpaper state
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "username" not in st.session_state:
    st.session_state.username = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "model" not in st.session_state:
    st.session_state.model = "gemma3:4b"
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None
if "guest_message_count" not in st.session_state:
    st.session_state.guest_message_count = 0
if "suggestion_clicked" not in st.session_state:
    st.session_state.suggestion_clicked = None

# ================= CUSTOM CSS (PREMIUM AI UI) =================
dm = st.session_state.get("dark_mode", True)
bg_color = "#0f172a" if dm else "#f8fafc" 
user_msg_bg = "linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)" if dm else "linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)"
bot_msg_bg = "rgba(30, 41, 59, 0.7)" if dm else "rgba(255, 255, 255, 0.7)"
text_color = "#f8fafc" if dm else "#0f172a"
border_color = "rgba(255, 255, 255, 0.1)" if dm else "rgba(0, 0, 0, 0.1)"
orb_opacity = "0.15" if dm else "0.3"
pill_bg = "rgba(255, 255, 255, 0.2)"

# --- NEW: Live Wallpaper CSS Logic ---
live_wallpaper_css = ""
if st.session_state.live_wallpaper:
    orb_opacity = "0.15" if dm else "0.3"
    live_wallpaper_css = f"""
        /* Ambient Floating Orbs */
        .bg-orb1 {{ position: fixed; top: -10%; left: -10%; width: 50vw; height: 50vw; border-radius: 50%; background: radial-gradient(circle, rgba(99,102,241,{orb_opacity}) 0%, rgba(0,0,0,0) 70%); filter: blur(60px); animation: float1 20s infinite alternate; z-index: -1; pointer-events: none; }}
        .bg-orb2 {{ position: fixed; bottom: -10%; right: -10%; width: 60vw; height: 60vw; border-radius: 50%; background: radial-gradient(circle, rgba(236,72,153,{orb_opacity}) 0%, rgba(0,0,0,0) 70%); filter: blur(60px); animation: float2 25s infinite alternate; z-index: -1; pointer-events: none; }}
        @keyframes float1 {{ 0% {{ transform: translate(0, 0) scale(1); }} 100% {{ transform: translate(100px, 50px) scale(1.2); }} }}
        @keyframes float2 {{ 0% {{ transform: translate(0, 0) scale(1); }} 100% {{ transform: translate(-100px, -50px) scale(1.1); }} }}
    """

st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;900&display=swap');
        
        /* Global Background */
        body {{ background-color: {bg_color}; color: {text_color}; font-family: 'Inter', sans-serif; transition: background-color 0.5s ease; }}
        .stApp {{ background: transparent !important; }} /* Makes the container transparent */
        
        /* Ambient Floating Orbs */
        .bg-orb1 {{ position: fixed; top: -10%; left: -10%; width: 50vw; height: 50vw; border-radius: 50%; background: radial-gradient(circle, rgba(99,102,241,{orb_opacity}) 0%, rgba(0,0,0,0) 70%); filter: blur(60px); animation: float1 20s infinite alternate; z-index: 0; pointer-events: none; }}
        .bg-orb2 {{ position: fixed; bottom: -10%; right: -10%; width: 60vw; height: 60vw; border-radius: 50%; background: radial-gradient(circle, rgba(236,72,153,{orb_opacity}) 0%, rgba(0,0,0,0) 70%); filter: blur(60px); animation: float2 25s infinite alternate; z-index: 0; pointer-events: none; }}
        .block-container {{ z-index: 1; position: relative; }} /* Keeps your chat text above the orbs */
        
        @keyframes float1 {{ 0% {{ transform: translate(0, 0) scale(1); }} 100% {{ transform: translate(100px, 50px) scale(1.2); }} }}
        @keyframes float2 {{ 0% {{ transform: translate(0, 0) scale(1); }} 100% {{ transform: translate(-100px, -50px) scale(1.1); }} }}
        /* Glassmorphism Message Bubbles & Strict Text Color Overrides */
        .user-message {{ background: {user_msg_bg}; color: #ffffff !important; padding: 16px 22px; border-radius: 20px 20px 4px 20px; margin: 10px 0; max-width: 75%; word-wrap: break-word; box-shadow: 0 8px 20px rgba(99, 102, 241, 0.2); font-size: 16px; line-height: 1.6; letter-spacing: 0.2px; }}
        .user-message p, .user-message span, .user-message li, .user-message a {{ color: #ffffff !important; }}
        
        .assistant-message {{ background: {bot_msg_bg}; backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); color: {text_color} !important; padding: 16px 22px; border-radius: 20px 20px 20px 4px; margin: 10px 0; max-width: 75%; word-wrap: break-word; box-shadow: 0 8px 32px rgba(0,0,0,0.08); border: 1px solid {border_color}; font-size: 16px; line-height: 1.6; letter-spacing: 0.2px; }}
        .assistant-message p, .assistant-message span, .assistant-message li, .assistant-message a {{ color: {text_color} !important; }}
        
        /* File Pill Styling */
        .file-pill {{ background: {pill_bg}; padding: 6px 14px; border-radius: 12px; font-size: 13px; display: inline-flex; align-items: center; margin-bottom: 10px; border: 1px solid rgba(255,255,255,0.3); backdrop-filter: blur(5px); font-weight: 500; color: {text_color} !important; }}
        
        /* Avatars */
        .avatar {{ width: 36px; height: 36px; border-radius: 50%; margin: 0 14px; flex-shrink: 0; box-shadow: 0 4px 10px rgba(0,0,0,0.1); border: 2px solid {border_color}; }}
        .user-avatar {{ background: url('https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f600.png') no-repeat center; background-size: cover; background-color: white; }}
        .bot-avatar {{ background: url('https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f916.png') no-repeat center; background-size: cover; background-color: #f1f5f9; }}
        
        /* Typing Animation */
        .typing-indicator {{ display: flex; align-items: center; justify-content: flex-start; margin: 15px 0 15px 65px; }}
        .typing-indicator span {{ display: inline-block; width: 8px; height: 8px; background-color: #8b5cf6; border-radius: 50%; margin: 0 3px; animation: bounce 1.4s infinite ease-in-out both; }}
        .typing-indicator span:nth-child(1) {{ animation-delay: -0.32s; }}
        .typing-indicator span:nth-child(2) {{ animation-delay: -0.16s; }}
        @keyframes bounce {{ 0%, 80%, 100% {{ transform: scale(0); }} 40% {{ transform: scale(1); }} }}
        
        /* Auto scroll container */
        #scroll-target {{ overflow-y: auto; max-height: 60vh; padding-bottom: 30px; padding-right: 15px; scrollbar-width: thin; z-index: 10; position: relative; }}
        
        /* Premium Chitti Header */
        .chitti-title {{ text-align: center; font-size: 5rem; font-weight: 900; letter-spacing: 4px; margin-top: 5vh; margin-bottom: 0px; background: linear-gradient(to right, #4f46e5, #ec4899, #f59e0b); -webkit-background-clip: text; -webkit-text-fill-color: transparent; animation: gradient-shift 8s ease infinite; background-size: 200% 200%; }}
        @keyframes gradient-shift {{ 0% {{ background-position: 0% 50%; }} 50% {{ background-position: 100% 50%; }} 100% {{ background-position: 0% 50%; }} }}
        .welcome-subtext {{ text-align: center; color: {'#94a3b8' if dm else '#64748b'}; font-size: 1.2rem; font-weight: 400; margin-bottom: 40px; }}
        
        /* Floating Circular Mic Button */
        .floating-mic {{
            position: fixed;
            bottom: 90px;
            right: 40px;
            z-index: 9999;
        }}
        .floating-mic button {{
            background: linear-gradient(135deg, #ec4899 0%, #8b5cf6 100%) !important;
            border: none !important;
            color: white !important;
            border-radius: 50% !important;
            width: 55px !important;
            height: 55px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            font-size: 24px !important;
            padding: 0 !important;
            box-shadow: 0 8px 20px rgba(236, 72, 153, 0.4) !important;
            transition: all 0.3s ease !important;
        }}
        .floating-mic button:hover {{
            transform: translateY(-3px) scale(1.05) !important;
            box-shadow: 0 12px 25px rgba(236, 72, 153, 0.6) !important;
        }}
    </style>
""", unsafe_allow_html=True)

# --- NEW: Inject Live Wallpaper HTML Elements ---
if st.session_state.live_wallpaper:
    st.markdown('<div class="bg-orb1"></div><div class="bg-orb2"></div>', unsafe_allow_html=True)


def generate_chat_id():
    return f"chat_{int(datetime.now().timestamp() * 1000)}"

# ================= SIDEBAR =================
with st.sidebar:
    st.markdown("### 🤖 CHITTI")
    st.markdown("---")

    if st.session_state.user_id is None:
        st.markdown("#### 👤 Authentication")
        tab1, tab2 = st.tabs(["Login", "Register"])
        with tab1:
            login_username = st.text_input("Username", key="login_user")
            login_password = st.text_input("Password", type="password", key="login_pass")
            if st.button("Login", use_container_width=True):
                success, result = login_user(login_username, login_password)
                if success:
                    st.session_state.user_id = result
                    st.session_state.username = get_user_info(result)[0]
                    st.session_state.messages = []
                    st.session_state.current_chat_id = None
                    st.session_state.guest_message_count = 0
                    st.rerun()
                else:
                    st.error(result)
        with tab2:
            reg_username = st.text_input("Username", key="reg_user")
            reg_email = st.text_input("Email", key="reg_email")
            reg_password = st.text_input("Password", type="password", key="reg_pass")
            reg_password_confirm = st.text_input("Confirm Password", type="password", key="reg_pass_confi")
            if st.button("Register", use_container_width=True):
                if reg_password != reg_password_confirm:
                    st.error("Passwords do not match!")
                elif len(reg_password) < 6:
                    st.error("Password must be at least 6 characters!")
                else:
                    success, message = register_user(reg_username, reg_email, reg_password)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
    else:
        st.markdown(f"**Welcome back, {st.session_state.username}!** 👋")
        
        if st.button("➕ New Chat", use_container_width=True, type="primary"):
            st.session_state.messages = []
            st.session_state.current_chat_id = None
            st.rerun()
            
        st.markdown("---")
        st.markdown("**📋 Recent Conversations**")
        sessions = get_user_sessions(st.session_state.user_id)
        if sessions:
            for session_id, title, created_at, updated_at in sessions:
                col1, col2 = st.columns([5, 1])
                with col1:
                    if st.button(f"💬 {title}", key=f"chat_{session_id}", use_container_width=True):
                        st.session_state.messages = get_session_messages(session_id)
                        st.session_state.current_chat_id = session_id
                        st.rerun()
                with col2:
                    if st.button("🗑", key=f"del_{session_id}", help="Delete chat"):
                        delete_session(session_id)
                        if st.session_state.current_chat_id == session_id:
                            st.session_state.messages = []
                            st.session_state.current_chat_id = None
                        st.rerun()
        else:
            st.info("No chat history yet. Start a new conversation!")
        
        st.markdown("---")
        
        with st.expander("⚙️ Settings & Preferences"):
            st.caption(f"**Model:** {st.session_state.model}")
            st.checkbox("🌓 Dark mode", value=st.session_state.dark_mode, key="dark_mode")
            # --- NEW: Live Wallpaper Toggle added here ---
            st.checkbox("✨ Background", value=st.session_state.live_wallpaper, key="live_wallpaper")
            
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.user_id = None
                st.session_state.username = None
                st.session_state.messages = []
                st.session_state.current_chat_id = None
                st.rerun()
                
        if len(st.session_state.messages) > 0:
            with st.expander("📥 Export Conversation"):
                json_str = json.dumps(st.session_state.messages, ensure_ascii=False, indent=2)
                st.download_button("📄 Export as JSON", data=json_str, file_name=f"chitti_chat_{datetime.now().strftime('%Y%m%d')}.json", mime="application/json", use_container_width=True)
                
                text_output = "".join([f"{'You' if m['role']=='user' else 'Chitti'}: {m['content']}\n\n" for m in st.session_state.messages])
                st.download_button("📝 Export as Text", data=text_output, file_name=f"chitti_chat_{datetime.now().strftime('%Y%m%d')}.txt", mime="text/plain", use_container_width=True)

# ================= MAIN CHAT AREA =================
if st.session_state.user_id is None:
    st.session_state.username = "Guest"

chat_placeholder = st.container()

with chat_placeholder:
    st.markdown('<div id="scroll-target">', unsafe_allow_html=True)

    # --- THE NEW PREMIUM WELCOME SCREEN ---
    if len(st.session_state.messages) == 0 and st.session_state.current_chat_id is None:
        display_name = st.session_state.username if st.session_state.username != "Guest" else "There"
        st.markdown(f"""
            <h1 class="chitti-title">CHITTI</h1>
            <div class="welcome-subtext">Hello {display_name}, I am Chitti. How can I assist you today?</div>
        """, unsafe_allow_html=True)
        
        st.write("") # Spacer
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("💡 Brainstorm project ideas", use_container_width=True):
                st.session_state.suggestion_clicked = "Can you help me brainstorm some creative coding project ideas?"
        with col2:
            if st.button("💻 Explain a coding concept", use_container_width=True):
                st.session_state.suggestion_clicked = "Explain the concept of Object-Oriented Programming like I am 5 years old."
        with col3:
            if st.button("📝 Summarize text", use_container_width=True):
                st.session_state.suggestion_clicked = "I have a document I need help summarizing. Can you help me distill the main points?"
                
        st.markdown("<br><br>", unsafe_allow_html=True)
    # ---------------------------------------

    # Render Messages
    for msg in st.session_state.messages:
        content = msg["content"]
        
        if msg["role"] == "user":
            formatted_content = re.sub(
                r'\[ATTACHED_FILE: (.*?)\]', 
                r'<div class="file-pill">📎 \1</div><br>', 
                content
            )
            formatted_content = re.sub(r'--- FILE CONTENTS ---.*', '', formatted_content, flags=re.DOTALL)
            
            st.markdown(f"""
                <div style="display: flex; justify-content: flex-end; margin: 15px 0;">
                    <div class="user-message">{formatted_content}</div>
                    <div class="user-avatar avatar"></div>
                </div>
            """, unsafe_allow_html=True)
            
        else:
            st.markdown(f"""
                <div style="display: flex; justify-content: flex-start; margin: 15px 0;">
                    <div class="bot-avatar avatar"></div>
                    <div class="assistant-message">{content}</div>
                </div>
            """, unsafe_allow_html=True)
            
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("""<script>var objDiv = document.getElementById("scroll-target"); if(objDiv){ objDiv.scrollTop = objDiv.scrollHeight; }</script>""", unsafe_allow_html=True)

# ================= INPUT & PROCESSING =================

# 1. The Voice Recorder floating above the chat input
st.markdown('<div class="floating-mic">', unsafe_allow_html=True)
voice_text = speech_to_text(
    language='en',
    start_prompt="🎙️",
    stop_prompt="🛑",
    just_once=True,
    use_container_width=False,
    key='STT'
)
st.markdown('</div>', unsafe_allow_html=True)

# 2. The standard Chat Input
prompt = st.chat_input(
    "Ask Chitti anything...",
    accept_file="multiple",
    file_type=["txt", "pdf", "csv", "py", "docx", "xlsx", "pptx", "json", "md", "html", "xml", "zip", "rar", "java", "c", "cpp", "js", "ts", "go", "rb", "php", "swift", "kt", "rs", "dart", "m", "scala", "lua", "hs", "erl", "ex", "exs","png", "jpg", "jpeg", "gif", "bmp", "svg", "webp"]
)

user_text = ""
uploaded_files = []

# Check where the input came from (Text box, Mic, or Suggestion Card)
if prompt:
    user_text = prompt.text if hasattr(prompt, "text") and prompt.text else (prompt if isinstance(prompt, str) else "")
    uploaded_files = prompt.files if hasattr(prompt, "files") else []
elif voice_text:
    user_text = voice_text
elif st.session_state.suggestion_clicked:
    user_text = st.session_state.suggestion_clicked
    st.session_state.suggestion_clicked = None

if user_text or uploaded_files:
    if st.session_state.user_id is None:
        if st.session_state.guest_message_count >= 5:
            st.warning("Please login to continue chatting with Chitti.")
            st.stop()
        else:
            st.session_state.guest_message_count += 1

    combined_input = user_text
    file_display_tags = ""
    file_raw_contents = ""

    # Process Files
    if uploaded_files:
        for attached_file in uploaded_files:
            file_display_tags += f"[ATTACHED_FILE: {attached_file.name}]\n"
            try:
                file_ext = Path(attached_file.name).suffix.lower()
                if file_ext == '.pdf':
                    import PyPDF2
                    pdf_reader = PyPDF2.PdfReader(attached_file)
                    text = "".join(page.extract_text() or "" for page in pdf_reader.pages)
                    file_raw_contents += f"\nFile '{attached_file.name}':\n{text}\n"
                elif file_ext in ['.docx', '.xlsx', '.pptx', '.zip', '.rar']:
                    file_raw_contents += f"\n[User attached binary file: {attached_file.name}]\n"
                else:
                    file_raw_contents += f"\nFile '{attached_file.name}':\n{attached_file.getvalue().decode('utf-8')}\n"
            except Exception as e:
                st.error(f"Error reading {attached_file.name}: {e}")

    if file_display_tags:
        combined_input = file_display_tags + combined_input + "\n\n--- FILE CONTENTS ---\n" + file_raw_contents

    if combined_input.strip() == "":
        st.stop()

    if st.session_state.current_chat_id is None:
        st.session_state.current_chat_id = generate_chat_id()
        if st.session_state.user_id is not None:
            create_chat_session(st.session_state.user_id, st.session_state.current_chat_id)
            title_source = user_text if user_text else "File Analysis"
            short_title = title_source[:30] + "..." if len(title_source) > 30 else title_source
            update_session_title(st.session_state.current_chat_id, short_title)

    st.session_state.messages.append({"role": "user", "content": combined_input})
    if st.session_state.user_id is not None:
        save_message(st.session_state.current_chat_id, "user", combined_input)
        
    st.rerun()

# ================= GENERATING RESPONSE =================
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    
    thinking_placeholder = st.empty()
    # Fixed the HTML typo here
    thinking_placeholder.markdown("""
        <div class="typing-indicator">
            <span></span><span></span><span></span>
        </div>
    """, unsafe_allow_html=True)

    current_time = datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")
    
    # Restructured System Prompt: Hides the time as "System Data" 
    # and simplifies the rules so small models actually follow them.
    system_message = {
        "role": "system",
        "content": (
            f"You are Chitti, a highly intelligent premium AI assistant talking to {st.session_state.username}. "
            f"[HIDDEN SYSTEM DATA: The exact current time is {current_time}. DO NOT mention this time unless the user specifically asks for it.]\n\n"
            # "STRICT RULES:\n"
            # "1. NEVER start your response with time-based greetings like 'Good morning', 'Good afternoon', or 'Good evening' unless asked .\n"
            # "2. Answer based ONLY on the user's prompt. Do not invent imaginary documents or previous conversations.\n"
            # "3. Use Markdown (bolding, bullet points, headers) to make responses beautiful and readable.\n"
            # "4. If the user attaches a file, use the content provided below the '--- FILE CONTENTS ---' marker."
            "Conversation Guidelines: "
            "1. Tone: Be friendly, empathetic, and highly helpful. Maintain a natural conversation flow without repetitive greetings (don't say 'Hello' every time). "
            "2. Accuracy: Answer directly based ONLY on the user's input and the provided chat history. DO NOT invent imaginary context, previous conversations, or documents. "
            "3. Honesty: If you do not know the answer or lack sufficient context, politely admit it rather than guessing or hallucinating information. "
            "4. Formatting: Always use Markdown formatting (bolding, bullet points, headers, and tables) to make your responses highly readable and scannable. "
            "5. Coding & Tech: If the user asks for code, provide clean, efficient, and well-commented code blocks. Explain the logic briefly after the code. "
            "6. Context: You know the current time, but only mention it if the user specifically asks about dates or times. "
            "7. File Analysis: If the user attaches a file, carefully use the content provided below the '--- FILE CONTENTS ---' marker to answer their query accurately."
            "8. Greetings: DO NOT initiate time-based greetings like 'Good morning' or 'Good evening' unless the user explicitly greets you that way first. "
        )
    }

    messages_for_model = [system_message] + st.session_state.messages
    

    messages_for_model = [system_message] + st.session_state.messages

    response = chat(
        model=st.session_state.model,
        messages=messages_for_model,
        stream=False
    )
    
    assistant_msg = response["message"]["content"]
    
    thinking_placeholder.empty()

    st.session_state.messages.append({"role": "assistant", "content": assistant_msg})
    if st.session_state.user_id is not None:
        save_message(st.session_state.current_chat_id, "assistant", assistant_msg)

    st.rerun()