import streamlit as st
from groq import Groq
import os
from dotenv import load_dotenv
from datetime import datetime
import uuid
import requests
import json

# Page configuration
st.set_page_config(
    page_title="AI Research Assistant",
    page_icon="🔍",
    layout="wide"
)

# Custom CSS - Enhanced for Perplexity-like UI
st.markdown("""
    <style>
    /* Global styles */
    body {
        font-family: 'Inter', sans-serif;
    }
    /* Minimalist Premium Chatbot UI - Inspired by modern AI interfaces */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

    /* Core resets and base styles */
    * {
        box-sizing: border-box;
    }

    body {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background-color: #fafafa;
        color: #111827;
        line-height: 1.5;
        -webkit-font-smoothing: antialiased;
        margin: 0;
        padding: 0;
    }

    /* Main container */
    .main .block-container {
        max-width: 800px;
        margin: 0 auto;
        padding: 16px 8px;
    }

    /* Header styling - ultra minimal */
    h1 {
        font-weight: 600;
        font-size: 1.5rem;
        color: #111827;
        letter-spacing: -0.02em;
        margin-bottom: 8px;
    }

    /* Caption styling */
    .caption {
        font-size: 0.875rem;
        color: #6b7280;
        margin-bottom: 24px;
        font-weight: 400;
    }

    /* Chat container */
    .stChatContainer {
        border-radius: 8px;
        background-color: #ffffff;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }

    /* Message container */
    .stChatMessageContainer {
        padding: 0;
    }

    /* Message styles - general */
    .stChatMessage {
        padding: 12px 16px;
        margin: 0;
        border-bottom: 1px solid #f3f4f6;
        transition: background-color 0.15s ease;
    }

    .stChatMessage:last-child {
        border-bottom: none;
    }

    .stChatMessage:hover {
        background-color: #fafafa;
    }

    /* Message avatar */
    .stChatMessage .stAvatar {
        width: 28px;
        height: 28px;
        border-radius: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 12px;
    }

    /* User message styling */
    .stChatMessage.user .stAvatar {
        background-color: #f0f9ff;
        border: 1px solid #e0f2fe;
    }

    .stChatMessage.user [data-testid="stChatMessageContent"] {
        background-color: transparent;
        padding: 0;
    }

    .stChatMessage.user [data-testid="stMarkdownContainer"] p {
        color: #111827;
        margin: 0;
        padding: 0;
    }

    /* Assistant message styling */
    .stChatMessage.assistant .stAvatar {
        background-color: #f0fdf4;
        border: 1px solid #dcfce7;
    }

    .stChatMessage.assistant [data-testid="stChatMessageContent"] {
        background-color: transparent;
        padding: 0;
    }

    .stChatMessage.assistant [data-testid="stMarkdownContainer"] p {
        color: #111827;
        margin: 0;
        padding: 0;
    }

    /* Code block styling - minimal and clean */
    .stMarkdown pre {
        background-color: #f8fafc;
        border-radius: 6px;
        padding: 12px;
        border: 1px solid #e2e8f0;
        overflow-x: auto;
        font-family: 'SF Mono', 'Menlo', 'Monaco', 'Courier New', monospace;
        font-size: 0.8125rem;
        margin: 12px 0;
        line-height: 1.5;
    }

    .stMarkdown code {
        font-family: 'SF Mono', 'Menlo', 'Monaco', 'Courier New', monospace;
        font-size: 0.8125rem;
        padding: 2px 5px;
        background-color: #f1f5f9;
        border-radius: 4px;
        color: #0f172a;
    }

    /* Input area styling - clean and minimal */
    .stChatInputContainer {
        padding: 12px 16px;
        background-color: #ffffff;
        border-top: 1px solid #f3f4f6;
        border-radius: 0 0 8px 8px;
    }

    .stChatInputContainer textarea {
        padding: 10px 14px;
        border-radius: 6px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
        font-size: 0.9375rem;
        resize: none;
        width: 100%;
        transition: all 0.2s ease;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .stChatInputContainer textarea:focus {
        border-color: #3b82f6;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
        outline: none;
    }

    /* Submit button - minimal */
    .stChatInputContainer button {
        width: 32px;
        height: 32px;
        border-radius: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
        background-color: #3b82f6;
        color: #ffffff;
        border: none;
        cursor: pointer;
        transition: all 0.2s ease;
    }

    .stChatInputContainer button:hover {
        background-color: #2563eb;
    }

    .stChatInputContainer button:focus {
        outline: none;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
    }

    /* Scrollbar styling - ultra minimal */
    ::-webkit-scrollbar {
        width: 4px;
        height: 4px;
    }

    ::-webkit-scrollbar-track {
        background-color: transparent;
    }

    ::-webkit-scrollbar-thumb {
        background-color: #d1d5db;
        border-radius: 2px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background-color: #9ca3af;
    }

    /* Helper elements - sources section */
    .sources-section {
        margin-top: 16px;
        padding: 12px 16px;
        background-color: #f9fafb;
        border-radius: 6px;
        border: 1px solid #e5e7eb;
    }

    .sources-title {
        font-size: 0.75rem;
        font-weight: 600;
        color: #4b5563;
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .reference-card {
        padding: 12px;
        background-color: #ffffff;
        border-radius: 6px;
        border: 1px solid #e5e7eb;
        margin-bottom: 8px;
        transition: all 0.15s ease;
    }

    .reference-card:hover {
        transform: translateY(-1px);
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }

    .reference-title {
        font-weight: 500;
        font-size: 0.875rem;
        color: #2563eb;
        margin-bottom: 4px;
    }

    .reference-url {
        font-size: 0.75rem;
        color: #6b7280;
        margin-bottom: 8px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .reference-snippet {
        font-size: 0.8125rem;
        color: #4b5563;
        line-height: 1.4;
    }

    /* Follow-up questions - minimal buttons */
    .followup-container {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 12px;
    }

    .followup-container button {
        background-color: #f3f4f6;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 6px 12px;
        font-size: 0.75rem;
        color: #4b5563;
        cursor: pointer;
        transition: all 0.15s ease;
    }

    .followup-container button:hover {
        background-color: #e5e7eb;
        color: #1f2937;
    }

    /* Thinking animation - subtle dots */
    .thinking-animation {
        display: flex;
        align-items: center;
        justify-content: flex-start;
        padding: 12px;
    }

    .thinking-dot {
        width: 6px;
        height: 6px;
        margin: 0 2px;
        background-color: #d1d5db;
        border-radius: 50%;
        animation: thinking 1.4s infinite ease-in-out both;
    }

    .thinking-dot:nth-child(1) {
        animation-delay: -0.32s;
    }

    .thinking-dot:nth-child(2) {
        animation-delay: -0.16s;
    }

    @keyframes thinking {
        0%, 80%, 100% { transform: scale(0); opacity: 0.5; }
        40% { transform: scale(1); opacity: 1; }
    }

    /* Lists styling - clean and minimal */
    .stMarkdown ul, .stMarkdown ol {
        padding-left: 24px;
        margin: 12px 0;
    }

    .stMarkdown li {
        margin-bottom: 4px;
        padding-left: 4px;
    }

    /* Table styling - minimal */
    .stMarkdown table {
        border-collapse: collapse;
        width: 100%;
        margin: 16px 0;
        font-size: 0.875rem;
    }

    .stMarkdown th, .stMarkdown td {
        border: 1px solid #e5e7eb;
        padding: 8px 12px;
        text-align: left;
    }

    .stMarkdown th {
        background-color: #f9fafb;
        font-weight: 500;
    }

    .stMarkdown tr:nth-child(even) {
        background-color: #f9fafb;
    }

    /* Mobile responsive adjustments */
    @media (max-width: 640px) {
        .main .block-container {
            padding: 8px 4px;
        }

        .stChatMessage {
            padding: 12px;
        }

        .stChatInputContainer {
            padding: 8px 12px;
        }

        .stChatInputContainer textarea {
            padding: 8px 12px;
        }
    }

    /* Hide default streamlit elements */
    .stDeployButton, .stToolbar, footer, header {
        display: none !important;
    }

    /* Make chat container width consistent */
    .st-emotion-cache-oczf7j.e1ewe7hr3,
    .st-emotion-cache-1gulkj5.e1akgbir11 {
        max-width: 800px !important;
        margin: 0 auto !important;
    }

    /* Message alignment and spacing */
    .stChatMessage [data-testid="stChatMessageContent"] {
        margin-left: 40px !important;
    }

    /* Additional refinements */
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {
        margin-top: 20px;
        margin-bottom: 12px;
        font-weight: 600;
        letter-spacing: -0.01em;
    }

    .stMarkdown p {
        margin: 8px 0;
    }

    /* Subtle hover effect on links */
    a {
        color: #2563eb;
        text-decoration: none;
        transition: color 0.15s ease;
    }

    a:hover {
        color: #1d4ed8;
    }

    </style>
""", unsafe_allow_html=True)

# Load environment variables
load_dotenv()
groq_api_key = os.environ.get("GROQ_API_KEY")
serper_api_key = os.environ.get("SERPER_API_KEY")  # Add your Serper API key to .env file

if not groq_api_key:
    st.error("❌ GROQ_API_KEY environment variable not set. Please set it.")
    st.stop()

if not serper_api_key:
    st.warning("⚠️ SERPER_API_KEY not set. Web search functionality will be limited.")

client = Groq(api_key=groq_api_key)

# Expanded model selection with more Groq models
MODELS = {
    'Llama3 8b': 'llama3-8b-8192',
    'Llama3 70b': 'llama3-70b-8192',
    'Mixtral 8x7b': 'mixtral-8x7b-32768',
    'Gemma2 9b': 'gemma2-9b-it',
    'Claude 3 Haiku': 'claude-3-haiku-20240307',
    'Claude 3 Sonnet': 'claude-3-sonnet-20240229',
    'Claude 3 Opus': 'claude-3-opus-20240229',
}

# Generate a unique app key for this specific chatbot instance
APP_KEY = "perplexity_style_chatbot"

# Initialize session state with app-specific keys
if f"{APP_KEY}_chats" not in st.session_state:
    st.session_state[f"{APP_KEY}_chats"] = {}
if f"{APP_KEY}_current_chat_id" not in st.session_state:
    st.session_state[f"{APP_KEY}_current_chat_id"] = None
if f"{APP_KEY}_model" not in st.session_state:
    st.session_state[f"{APP_KEY}_model"] = 'Claude 3 Sonnet'
if "search_enabled" not in st.session_state:
    st.session_state["search_enabled"] = True

def create_new_chat():
    """Create a new chat and return its ID"""
    chat_id = f"{APP_KEY}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
    st.session_state[f"{APP_KEY}_chats"][chat_id] = {
        "title": f"New Research",
        "messages": [],
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    return chat_id

def delete_chat(chat_id):
    """Delete a chat from session state"""
    if chat_id in st.session_state[f"{APP_KEY}_chats"]:
        del st.session_state[f"{APP_KEY}_chats"][chat_id]
        if chat_id == st.session_state[f"{APP_KEY}_current_chat_id"]:
            st.session_state[f"{APP_KEY}_current_chat_id"] = None

def get_chat_title(messages):
    """Generate a chat title based on the first message"""
    if messages:
        first_msg = messages[0]["content"]
        return first_msg[:30] + "..." if len(first_msg) > 30 else first_msg
    return "New Research"

def search_web(query, num_results=5):
    """Search the web using Serper API"""
    if not serper_api_key:
        return {
            "organic": [
                {
                    "title": "Sample result (Serper API key not configured)",
                    "link": "https://example.com",
                    "snippet": "This is a sample search result. To enable real web search, add your Serper API key to the .env file."
                }
            ]
        }

    headers = {
        'X-API-KEY': serper_api_key,
        'Content-Type': 'application/json'
    }

    payload = {
        "q": query,
        "num": num_results
    }

    try:
        response = requests.post(
            'https://google.serper.dev/search',
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Search error: {e}")
        return {"organic": []}

def extract_relevant_info(search_results, query):
    """Extract relevant information from search results"""
    relevant_info = []

    if "organic" in search_results:
        for result in search_results["organic"]:
            relevant_info.append({
                "title": result.get("title", ""),
                "url": result.get("link", ""),
                "snippet": result.get("snippet", "")
            })

    return relevant_info

def generate_follow_up_questions(response_text, query):
    """Generate follow-up questions based on AI response and query"""
    system_prompt = """
    Given the original query and the AI's response, generate 3 natural follow-up questions that the user might want to ask next.
    Make these questions specific, diverse, and naturally flowing from the current conversation.
    Return only the questions as a JSON array of strings with no additional text.
    """

    try:
        model_name = MODELS[st.session_state[f"{APP_KEY}_model"]]

        follow_up_response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Original query: {query}\n\nAI response: {response_text[:1000]}..."}
            ],
            temperature=0.7,
            max_tokens=150,
            response_format={"type": "json_object"}
        )

        response_text = follow_up_response.choices[0].message.content.strip()
        questions_data = json.loads(response_text)

        # Check if the response has the expected format
        if "questions" in questions_data and isinstance(questions_data["questions"], list):
            return questions_data["questions"][:3]
        else:
            # Fallback if the format is unexpected but still a list
            for key, value in questions_data.items():
                if isinstance(value, list) and len(value) > 0:
                    return value[:3]

            # Final fallback
            return ["Tell me more about this topic",
                   "What are the most recent developments?",
                   "How does this compare to alternatives?"]

    except Exception as e:
        print(f"Error generating follow-up questions: {e}")
        return ["Tell me more about this topic",
               "What are the most recent developments?",
               "How does this compare to alternatives?"]

# Sidebar
with st.sidebar:
    st.title("🔍 Research History")

    # New chat button
    if st.button("🆕 New Research", key=f"{APP_KEY}_new_chat"):
        st.session_state[f"{APP_KEY}_current_chat_id"] = create_new_chat()
        st.rerun()

    st.divider()

    # Model selection
    st.session_state[f"{APP_KEY}_model"] = st.selectbox(
        "Select Research Assistant:",
        options=list(MODELS.keys()),
        index=list(MODELS.keys()).index('Claude 3 Sonnet') if 'Claude 3 Sonnet' in MODELS else 0,
        key=f"{APP_KEY}_model_select"
    )

    # Search toggle
    st.session_state["search_enabled"] = st.toggle("Enable Web Search", value=True)

    st.divider()

    # Display chat history
    if st.session_state[f"{APP_KEY}_chats"]:
        for chat_id, chat_data in sorted(
            st.session_state[f"{APP_KEY}_chats"].items(),
            key=lambda x: x[1]["created_at"],
            reverse=True
        ):
            col1, col2 = st.columns([0.8, 0.2])
            with col1:
                is_selected = chat_id == st.session_state[f"{APP_KEY}_current_chat_id"]
                button_class = "selected-chat" if is_selected else "chat-history"

                if st.button(
                    f"📝 {chat_data['title']}",
                    key=f"{APP_KEY}_chat_{chat_id}",
                    help=chat_data["created_at"],
                    use_container_width=True
                ):
                    st.session_state[f"{APP_KEY}_current_chat_id"] = chat_id
                    st.rerun()
            with col2:
                if st.button("🗑️", key=f"{APP_KEY}_delete_{chat_id}"):
                    delete_chat(chat_id)
                    st.rerun()
    else:
        st.info("No research history yet. Start a new search!")

# Main chat interface
if not st.session_state[f"{APP_KEY}_current_chat_id"]:
    st.session_state[f"{APP_KEY}_current_chat_id"] = create_new_chat()

current_chat = st.session_state[f"{APP_KEY}_chats"][st.session_state[f"{APP_KEY}_current_chat_id"]]

# Chat header
st.title("🔍 NetSeek")
st.caption(f"Powered by {st.session_state[f'{APP_KEY}_model']} | Web Search: {'Enabled' if st.session_state['search_enabled'] else 'Disabled'}")

# Display chat messages
for msg in current_chat["messages"]:
    if msg["role"] == "user":
        with st.chat_message("user", avatar="👤"):
            st.markdown(msg["content"])
    else:
        with st.chat_message("assistant", avatar="🔍"):
            if "is_thinking" in msg and msg["is_thinking"]:
                st.markdown("Searching and thinking...")
                continue

            # Display main response
            st.markdown(msg["content"])

            # Display sources if available
            if "sources" in msg and msg["sources"]:
                st.markdown("---")
                st.markdown("<div class='sources-section'><div class='sources-title'>SOURCES</div></div>", unsafe_allow_html=True)

                for source in msg["sources"]:
                    st.markdown(
                        f"""
                        <div class='reference-card'>
                            <div class='reference-content'>
                                <div class='reference-title'><a href="{source['url']}" target="_blank">{source['title']}</a></div>
                                <div class='reference-url'>{source['url']}</div>
                                <div class='reference-snippet'>{source['snippet']}</div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

            # Display follow-up questions if available
            if "follow_up_questions" in msg and msg["follow_up_questions"]:
                st.markdown("---")
                st.markdown("<div class='followup-container'>", unsafe_allow_html=True)

                for question in msg["follow_up_questions"]:
                    if st.button(f"🔍 {question}", key=f"followup_{hash(question)}"):
                        # When clicked, ask this follow-up question
                        st.session_state["follow_up_question"] = question
                        st.rerun()  # Rerun to handle the follow-up question as a new input

                st.markdown("</div>", unsafe_allow_html=True)

# Ensure the chat input is always rendered
user_input = st.chat_input("Ask research question...")

if user_input:
    # Update chat title if this is the first message
    if not current_chat["messages"]:
        current_chat["title"] = get_chat_title([{"content": user_input}])

    # Add user message
    current_chat["messages"].append({
        "role": "user",
        "content": user_input,
        "avatar": "👤"
    })

    # Display user message
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)

    # Add a "thinking" message
    thinking_msg = {
        "role": "assistant",
        "content": "Searching and thinking...",
        "is_thinking": True,
        "avatar": "🔍"
    }
    current_chat["messages"].append(thinking_msg)

    # Display the thinking message
    with st.chat_message("assistant", avatar="🔍"):
        thinking_placeholder = st.empty()
        thinking_placeholder.markdown("Searching and thinking...")

    try:
        # Perform web search if enabled
        search_results = {}
        sources = []

        if st.session_state["search_enabled"]:
            search_results = search_web(user_input)
            sources = extract_relevant_info(search_results, user_input)

        # Prepare context from search results
        search_context = ""
        if sources:
            search_context = "Here is information from web search results:\n\n"
            for i, source in enumerate(sources):
                search_context += f"Source {i+1}: {source['title']}\nURL: {source['url']}\nSnippet: {source['snippet']}\n\n"

        # Format messages for API request
        model_name = MODELS[st.session_state[f"{APP_KEY}_model"]]

        # Create a system prompt that includes search results
        system_prompt = """You are a helpful research assistant that provides comprehensive, accurate, and up-to-date information.

Your response should:
1. Be detailed, factual, and educational
2. Include relevant statistics, examples, and context
3. Structure information with clear headings and organized paragraphs
4. Maintain a balanced perspective when topics are controversial
5. Cite your sources clearly throughout your response

When search results are provided, use them to inform your response. Explicitly reference these sources when using their information."""

        if search_context:
            system_prompt += f"\n\nHere is information from the web to help answer the query: {user_input}\n\n{search_context}"

        # Prepare conversation context
        formatted_messages = [{"role": "system", "content": system_prompt}]

        # Add previous conversation context (but limit to last 4 exchanges to save tokens)
        conversation_history = []
        for msg in current_chat["messages"]:
            if not msg.get("is_thinking", False):  # Skip thinking messages
                if msg["role"] == "user":
                    conversation_history.append({"role": "user", "content": msg["content"]})
                elif msg["role"] == "assistant":
                    conversation_history.append({"role": "assistant", "content": msg["content"]})

        # Only include the most recent exchanges (up to last 4)
        formatted_messages.extend(conversation_history[-8:])

        # Generate the response
        response = client.chat.completions.create(
            model=model_name,
            messages=formatted_messages,
            temperature=0.7,
            max_tokens=1024,
            top_p=1,
            stream=False,
        )

        bot_response = response.choices[0].message.content.strip() if response.choices else "Error: No response received."

        # Generate follow-up questions
        follow_up_questions = generate_follow_up_questions(bot_response, user_input)

        # Replace the thinking message with the actual response
        current_chat["messages"].pop()  # Remove the thinking message

        current_chat["messages"].append({
            "role": "assistant",
            "content": bot_response,
            "sources": sources,
            "follow_up_questions": follow_up_questions,
            "avatar": "🔍"
        })

        # Update the display
        thinking_placeholder.empty()
        with st.chat_message("assistant", avatar="🔍"):
            # Display main response
            st.markdown(bot_response)

            # Display sources if available
            if sources:
                st.markdown("---")
                st.markdown("<div class='sources-section'><div class='sources-title'>SOURCES</div></div>", unsafe_allow_html=True)

                for source in sources:
                    st.markdown(
                        f"""
                        <div class='reference-card'>
                            <div class='reference-content'>
                                <div class='reference-title'><a href="{source['url']}" target="_blank">{source['title']}</a></div>
                                <div class='reference-url'>{source['url']}</div>
                                <div class='reference-snippet'>{source['snippet']}</div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

            # Display follow-up questions
            if follow_up_questions:
                st.markdown("---")
                st.markdown("<div class='followup-container'>", unsafe_allow_html=True)

                for question in follow_up_questions:
                    if st.button(f"🔍 {question}", key=f"followup_{hash(question)}"):
                        # When clicked, ask this follow-up question
                        st.session_state["follow_up_question"] = question
                        st.rerun()  # Rerun to handle the follow-up question as a new input

                st.markdown("</div>", unsafe_allow_html=True)

    except Exception as e:
        error_message = f"Error generating response: {e}"

        # Replace the thinking message with the error
        current_chat["messages"].pop()  # Remove the thinking message
        current_chat["messages"].append({
            "role": "assistant",
            "content": error_message,
            "avatar": "🔍"
        })

        # Update the display
        thinking_placeholder.empty()
        with st.chat_message("assistant", avatar="🔍"):
            st.error(error_message)