import streamlit as st
from google.generativeai import GenerativeModel
import google.generativeai as genai
import os
from dotenv import load_dotenv
from datetime import datetime
import uuid
import requests
import json
import hashlib
import pickle
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="DSA Learning Assistant",
    page_icon="🧠",
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
google_api_key = os.environ.get("GEMINI_API_KEY")
groq_api_key = os.environ.get("GROQ_API_KEY")
serper_api_key = os.environ.get("SERPER_API_KEY")  # Add your Serper API key to .env file

if not google_api_key:
    st.error("❌ GEMINI_API_KEY environment variable not set. Please set it.")
    st.stop()

if not groq_api_key:
    st.error("❌ GROQ_API_KEY environment variable not set. Please set it.")
    st.stop()

if not serper_api_key:
    st.warning("⚠️ SERPER_API_KEY not set. Web search functionality will be limited.")

# Configure Google Generative AI with your API key
if google_api_key:
    genai.configure(api_key=google_api_key)

# Define your model configurations
MODELS = {
    'DSA Sage-01':'tunedmodel',
    'Gemini 1.5 Pro': 'gemini-1.5-pro',
    'Gemini 1.5 Flash': 'gemini-1.5-flash',
    'Llama 3 70B': 'llama3-70b-8192',
    'Llama 3 8B': 'llama3-8b-8192',
    'Mixtral 8x7B': 'mixtral-8x7b-32768',
    'Gemma 7b': 'gemma-7b-it',
    'Claude 3 Haiku': 'claude-3-haiku-20240307',
    'Claude 3 Sonnet': 'claude-3-sonnet-20240229',
    'Claude 3 Opus': 'claude-3-opus-20240229',
}

# Model provider mapping
MODEL_PROVIDERS = {
    'DSA Sage-01': 'gemini',
    'Gemini 1.5 Pro': 'gemini',
    'Gemini 1.5 Flash': 'gemini',
    'Llama 3 70B': 'groq',
    'Llama 3 8B': 'groq',
    'Mixtral 8x7B': 'groq',
    'Gemma 7b': 'groq',
    'Claude 3 Haiku': 'groq',
    'Claude 3 Sonnet': 'groq',
    'Claude 3 Opus': 'groq',
}

# Model-specific configurations for better performance
MODEL_CONFIGS = {
    'DSA Sage-01': {
        'temperature': 0.2,
        'max_output_tokens': 4096,  # Increased token size
        'top_p': 0.95,
        'top_k': 40,
        'system_prompt': 'You are an expert DSA (Data Structures and Algorithms) tutor. Your primary goal is to provide clear, detailed, and comprehensive explanations about DSA concepts. Include code examples, time and space complexity analysis, visual explanations, and multiple approaches to solving problems. You are proficient in multiple programming languages including Python, Java, C++, and JavaScript. Always include detailed implementations with well-commented code'
    },
    'gemini-1.5-pro': {
        'temperature': 0.7,
        'max_output_tokens': 2048,
        'top_p': 1.0,
    },
    'gemini-1.5-flash': {
        'temperature': 0.7,
        'max_output_tokens': 2048,
        'top_p': 1.0,
    },
    'llama3-70b-8192': {
        'temperature': 0.7,
        'max_tokens': 2048,
        'top_p': 1.0,
    },
    'llama3-8b-8192': {
        'temperature': 0.7,
        'max_tokens': 2048,
        'top_p': 1.0,
    },
    'mixtral-8x7b-32768': {
        'temperature': 0.7,
        'max_tokens': 2048,
        'top_p': 1.0,
    },
    'gemma-7b-it': {
        'temperature': 0.7,
        'max_tokens': 2048,
        'top_p': 1.0,
    },
    'claude-3-haiku-20240307': {
        'temperature': 0.7,
        'max_tokens': 2048,
        'top_p': 1.0,
    },
    'claude-3-sonnet-20240229': {
        'temperature': 0.7,
        'max_tokens': 2048,
        'top_p': 1.0,
    },
    'claude-3-opus-20240229': {
        'temperature': 0.7,
        'max_tokens': 2048,
        'top_p': 1.0,
    }
}

# Maximum number of messages to include in context window
MAX_CONTEXT_MESSAGES = 10

# Set up cache directory
CACHE_DIR = Path("./dsa_response_cache")
CACHE_DIR.mkdir(exist_ok=True)

# Cache implementation with improved path handling
class ResponseCache:
    def __init__(self, cache_dir=CACHE_DIR):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(exist_ok=True)

    def _generate_key(self, prompt, model):
        """Generate a unique key for the cache based on prompt and model with safe path handling"""
        # Create a hash of the prompt to use as filename
        prompt_str = json.dumps(prompt) if isinstance(prompt, list) else str(prompt)
        hash_obj = hashlib.md5(prompt_str.encode('utf-8'))
        hash_key = hash_obj.hexdigest()

        # Sanitize model name to be file-system safe
        safe_model = model.replace('/', '_').replace('\\', '_').replace(':', '_').replace('-', '_')
        return f"{safe_model}_{hash_key}.pkl"

    def get(self, prompt, model):
        """Get cached response if it exists"""
        key = self._generate_key(prompt, model)
        cache_file = self.cache_dir / key

        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                st.error(f"Error reading from cache: {e}")
                return None

        return None

    def set(self, prompt, model, response):
        """Cache a response with improved error handling"""
        key = self._generate_key(prompt, model)
        cache_file = self.cache_dir / key

        # Ensure the directory exists before writing
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(response, f)
            return True
        except Exception as e:
            st.error(f"Error writing to cache: {e}")
            return False

# Initialize response cache
response_cache = ResponseCache()

# Initialize session state
if "chats" not in st.session_state:
    st.session_state.chats = {}
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None
if "model" not in st.session_state:
    st.session_state.model = 'DSA Sage-01'  # Default to your fine-tuned model
if "context_window" not in st.session_state:
    st.session_state.context_window = MAX_CONTEXT_MESSAGES
if "use_cache" not in st.session_state:
    st.session_state.use_cache = True
if "search_enabled" not in st.session_state:
    st.session_state.search_enabled = True

def create_new_chat():
    """Create a new chat and return its ID"""
    chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    st.session_state.chats[chat_id] = {
        "title": f"New DSA Chat {len(st.session_state.chats) + 1}",
        "messages": [],
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "summary": ""  # To store the conversation summary for context management
    }
    return chat_id

def delete_chat(chat_id):
    """Delete a chat from session state"""
    if chat_id in st.session_state.chats:
        del st.session_state.chats[chat_id]
        if chat_id == st.session_state.current_chat_id:
            st.session_state.current_chat_id = None

def get_chat_title(messages):
    """Generate a chat title based on the first message"""
    if messages:
        first_msg = messages[0]["content"]
        return first_msg[:30] + "..." if len(first_msg) > 30 else first_msg
    return "New DSA Chat"

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
        model_name = MODELS[st.session_state["model"]]
        provider = MODEL_PROVIDERS[st.session_state["model"]]

        if provider == 'gemini':
            model = GenerativeModel(model_name)
            follow_up_response = model.generate_content(
                [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Original query: {query}\n\nAI response: {response_text[:1000]}..."}
                ],
                generation_config={
                    'temperature': 0.7,
                    'max_output_tokens': 150,
                    'top_p': 1.0
                }
            )
            response_text = follow_up_response.text.strip() if hasattr(follow_up_response, 'text') else ""
        else:
            client = Groq(api_key=groq_api_key)
            follow_up_response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Original query: {query}\n\nAI response: {response_text[:1000]}..."}
                ],
                temperature=0.7,
                max_tokens=150,
                top_p=1.0,
                response_format={"type": "json_object"}
            )
            response_text = follow_up_response.choices[0].message.content.strip()

        # Debugging: Print the response text to understand its structure
        print("Response Text:", response_text)

        # Attempt to parse the JSON response
        try:
            questions_data = json.loads(response_text)
        except json.JSONDecodeError as e:
            print(f"JSON Decode Error: {e}")
            return ["Tell me more about this topic",
                    "What are the most recent developments?",
                    "How does this compare to alternatives?"]

        # Check if the response has the expected format
        if isinstance(questions_data, list):
            return questions_data[:3]
        else:
            # Fallback if the format is unexpected but still a list
            return ["Tell me more about this topic",
                    "What are the most recent developments?",
                    "How does this compare to alternatives?"]

    except Exception as e:
        print(f"Error generating follow-up questions: {e}")
        return ["Tell me more about this topic",
               "What are the most recent developments?",
               "How does this compare to alternatives?"]

def get_dsa_system_prompt():
    """Generate an enhanced system prompt for DSA assistant with examples"""
    return """You are a specialized Data Structures and Algorithms (DSA) tutor designed to help students master computer science concepts.

Your capabilities include:
1. Explaining DSA concepts clearly with detailed examples and visualizations
2. Providing optimized code implementations in multiple languages (Python, Java, C++, JavaScript)
3. Analyzing time and space complexity of algorithms with mathematical precision
4. Breaking down problem-solving approaches step-by-step for coding challenges
5. Suggesting practice problems based on skill level with targeted learning goals
6. Explaining solutions with detailed reasoning and edge case handling

Always include:
- Well-commented code examples when explaining implementations
- Precise Big O analysis for time and space complexity with explanations of derivation
- Visual explanations using text-based diagrams or ASCII art when appropriate
- Multiple approaches to solving problems with trade-offs analysis
- Common pitfalls and optimization techniques

Example format for algorithm explanations:
---
## Binary Search
Binary search is an efficient algorithm for finding a target value in a sorted array.

### Concept:
The algorithm works by repeatedly dividing the search interval in half. If the target value is less than the middle element, continue searching in the lower half; otherwise, search in the upper half.

### Visual Explanation:
[ 1, 3, 5, 7, 9, 11, 13, 15 ]
L           M            R    // compare 7 with target=11
L     M      R    // compare 11 with target=11
M           // found!

### Implementation (Python):
```python
def binary_search(arr, target):
    left, right = 0, len(arr) - 1

    while left <= right:
        mid = left + (right - left) // 2  # Prevents integer overflow

        if arr[mid] == target:
            return mid  # Target found
        elif arr[mid] < target:
            left = mid + 1  # Search in right half
        else:
            right = mid - 1  # Search in left half

    return -1  # Target not found
Time Complexity:
O(log n) - Each step eliminates half of the remaining elements
This is because the search space is halved in each iteration: n → n/2 → n/4 → ... → 1
Space Complexity:
O(1) - Only using a constant amount of extra space regardless of input size
Tailor your responses to the student's level of understanding and provide practical, industry-relevant insights when appropriate.
"""

def format_messages_for_google_ai(messages, system_prompt):
    """Format messages for Google AI's expected structure"""
    formatted_messages = []

    # Add system prompt as first message from the model
    if system_prompt:
        formatted_messages.append({"role": "model", "parts": [system_prompt]})

    # Add conversation messages
    for msg in messages:
        role = "user" if msg["role"] == "user" else "model"
        formatted_messages.append({"role": role, "parts": [msg["content"]]})

    return formatted_messages

def format_messages_for_groq(messages, system_prompt):
    """Format messages for Groq API"""
    formatted_messages = []

    # Add system message if provided
    if system_prompt:
        formatted_messages.append({"role": "system", "content": system_prompt})

    # Add conversation messages
    for msg in messages:
        role = "user" if msg["role"] == "user" else "assistant"
        formatted_messages.append({"role": role, "content": msg["content"]})

    return formatted_messages

def call_groq_api(messages, model_name, config):
    """Call the Groq API directly"""
    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {groq_api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": model_name,
        "messages": messages,
        "temperature": config.get('temperature', 0.7),
        "max_tokens": config.get('max_tokens', 2048),
        "top_p": config.get('top_p', 1.0)
    }

    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200:
        response_data = response.json()
        if "choices" in response_data and len(response_data["choices"]) > 0:
            return response_data["choices"][0]["message"]["content"]
        else:
            return "Error: No content in response"
    else:
        error_info = response.json() if response.text else {"error": f"HTTP {response.status_code}"}
        raise Exception(f"Groq API error: {error_info}")

def get_optimized_message_history(chat_id):
    """Get optimized message history, with a summary of older messages to save tokens."""
    if chat_id not in st.session_state.chats:
        return []

    chat = st.session_state.chats[chat_id]
    messages = chat["messages"]

    # If under the MAX_CONTEXT_MESSAGES limit, just return all messages
    if len(messages) <= MAX_CONTEXT_MESSAGES:
        return [{"role": msg["role"], "content": msg["content"]} for msg in messages]

    # Otherwise, use a summary + recent messages approach
    result = []

    # Get or generate a summary of older messages
    summary = chat.get("summary", "")
    if not summary:
        summary = generate_conversation_summary(messages, chat_id)

    # Add the summary as system message if it exists
    if summary:
        result.append({
            "role": "system",
            "content": f"Here's a summary of the earlier conversation: {summary}\n\nNow continue helping with the latest messages."
        })

    # Add the most recent MAX_CONTEXT_MESSAGES messages
    recent_messages = messages[-MAX_CONTEXT_MESSAGES:]
    for msg in recent_messages:
        result.append({"role": msg["role"], "content": msg["content"]})

    return result

def generate_conversation_summary(messages, chat_id=None):
    """Generate a summary of the conversation to maintain context while reducing tokens."""
    if not messages or len(messages) <= 1:
        return ""

    # Only summarize if we have more than MAX_CONTEXT_MESSAGES
    if len(messages) <= MAX_CONTEXT_MESSAGES:
        return ""

    # Get earlier messages to summarize (except the most recent MAX_CONTEXT_MESSAGES)
    messages_to_summarize = messages[:-MAX_CONTEXT_MESSAGES]

    try:
        # Create a prompt to summarize the conversation
        summary_prompt = "Summarize the following conversation about Data Structures and Algorithms in a concise way that preserves the key technical details, questions asked, and knowledge shared. Here's the conversation:\n\n"

        for msg in messages_to_summarize:
            summary_prompt += f"{msg['role'].upper()}: {msg['content']}\n\n"

        # Check cache first
        cached_response = None
        if st.session_state.use_cache:
            cached_response = response_cache.get(summary_prompt, MODELS[st.session_state.model])

        if cached_response:
            summary = cached_response
        else:
            # Get the summary from the selected model
            model_name = MODELS[st.session_state.model]
            provider = MODEL_PROVIDERS[st.session_state.model]

            # Get the system prompt
            system_prompt = get_dsa_system_prompt()

            if provider == 'gemini':
                # Use Google AI
                model = GenerativeModel(model_name)

                # Create formatted prompt for Google AI
                formatted_prompt = [
                    {"role": "user", "parts": [summary_prompt]}
                ]

                # Use the model-specific configurations
                config = MODEL_CONFIGS.get(model_name, {
                    'temperature': 0.3,
                    'max_output_tokens': 500,
                    'top_p': 1.0
                })

                response = model.generate_content(
                    formatted_prompt,
                    generation_config=config
                )

                summary = response.text if hasattr(response, 'text') else ""
            else:
                # Use Groq API
                # Format messages for Groq
                formatted_messages = [
                    {"role": "system", "content": "You are a DSA assistant tasked with summarizing conversations."},
                    {"role": "user", "content": summary_prompt}
                ]

                config = MODEL_CONFIGS.get(model_name, {
                    'temperature': 0.3,
                    'max_tokens': 500,
                    'top_p': 1.0
                })

                summary = call_groq_api(formatted_messages, model_name, config)

        # Cache the response
        if st.session_state.use_cache:
            response_cache.set(summary_prompt, model_name, summary)

        # Save the summary if we have a chat_id
        if chat_id and chat_id in st.session_state.chats:
            st.session_state.chats[chat_id]["summary"] = summary

        return summary

    except Exception as e:
        # If summarization fails, just return a basic summary
        return f"This conversation covers DSA topics including {', '.join(set([msg.get('topic', 'various DSA concepts') for msg in messages_to_summarize if 'topic' in msg]))}."

def get_response_with_cag(messages, system_prompt):
    """Get response from the model with cache-augmented generation and improved error handling"""
    selected_model = st.session_state.model
    model_name = MODELS[selected_model]
    provider = MODEL_PROVIDERS[selected_model]

    # Special handling for DSA Sage-01 model
    if selected_model == 'DSA Sage-01':
        # Use the DSA Sage-specific system prompt
        dsa_sage_config = MODEL_CONFIGS['DSA Sage-01']
        system_prompt = dsa_sage_config.get('system_prompt', system_prompt)

    # Format messages based on provider
    if provider == 'gemini':
        formatted_messages = format_messages_for_google_ai(messages, system_prompt)
    else:  # 'groq'
        formatted_messages = format_messages_for_groq(messages, system_prompt)

    # Check cache first if enabled
    cached_response = None
    if st.session_state.use_cache:
        cached_response = response_cache.get(formatted_messages, model_name)

    if cached_response:
        return cached_response, True  # Return cached response and flag that it was from cache

    # If not in cache, generate new response
    try:
        if provider == 'gemini':
            # Use Google AI
            model = GenerativeModel(model_name)

            # Get model-specific configuration
            config = MODEL_CONFIGS.get(model_name, {
                'temperature': 0.7,
                'max_output_tokens': 2048,
                'top_p': 1.0
            })

            # Generate response with model-specific configurations
            response = model.generate_content(
                formatted_messages,
                generation_config=config
            )

            bot_response = response.text if hasattr(response, 'text') else "Error: No response received."

        else:  # 'groq'
            # Use Groq API
            config = MODEL_CONFIGS.get(model_name, {
                'temperature': 0.7,
                'max_tokens': 2048,
                'top_p': 1.0
            })

            bot_response = call_groq_api(formatted_messages, model_name, config)

        # Perform web search to enhance the response
        search_query = messages[-1]["content"]  # Use the last user message as the search query
        search_results = {}
        sources = []

        if st.session_state.search_enabled:
            search_results = search_web(search_query)
            sources = extract_relevant_info(search_results, search_query)

        if sources:
            # Append search results to the response
            bot_response += "\n\n### Data Sources:\n"
            for source in sources:
                bot_response += f"- [{source['title']}]({source['url']})\n"

        # Cache the response
        if st.session_state.use_cache:
            response_cache.set(formatted_messages, model_name, bot_response)

        return bot_response, False  # Return new response and flag that it was not from cache

    except Exception as e:
        error_msg = str(e)
        # Add more detailed error handling
        if "not found" in error_msg.lower() and "model" in error_msg.lower():
            return f"Error: The model '{model_name}' could not be found. Please check your model configuration.", False
        elif "permission" in error_msg.lower() or "access" in error_msg.lower():
            return f"Error: Permission issue with the API. Please verify your API key has access to '{model_name}'.", False
        elif "api key" in error_msg.lower():
            return "Error: API key issue. Please check that your key is valid and properly configured.", False
        else:
            return f"Error generating response: {error_msg}", False

# Sidebar
with st.sidebar:
    st.title("🧠 DSA Learning")

    # Study Mode Selection
    st.session_state.study_mode = st.radio(
        "Study Mode:",
        options=["Chat"],
        index=0
    )

    # New chat button
    if st.button("🆕 New Chat", key="new_chat"):
        st.session_state.current_chat_id = create_new_chat()
        st.rerun()

    st.divider()

    # API provider selection
    api_provider = st.radio(
        "API Provider:",
        options=["Gemini", "Groq"],
        horizontal=True,
        disabled=(not google_api_key or not groq_api_key)
    )

    # Filter models based on selected provider
    if api_provider == "Gemini" and google_api_key:
        available_models = [model for model, provider in MODEL_PROVIDERS.items() if provider == 'gemini']
    elif api_provider == "Groq" and groq_api_key:
        available_models = [model for model, provider in MODEL_PROVIDERS.items() if provider == 'groq']
    else:
        # If API key is missing, show all models but disable selection
        available_models = list(MODELS.keys())

    # Model selection
    st.session_state.model = st.selectbox(
        "Select Model:",
        options=available_models,
        index=0 if 'DSA Sage-01' in available_models else 0
    )

    # Display model settings for the selected model
    selected_model_name = MODELS[st.session_state.model]
    with st.expander("Model Settings"):
        config = MODEL_CONFIGS.get(selected_model_name, {})

        # Display configuration based on provider
        if MODEL_PROVIDERS[st.session_state.model] == 'gemini':
            st.write(f"Temperature: {config.get('temperature', 0.7)}")
            st.write(f"Max tokens: {config.get('max_output_tokens', 2048)}")
            st.write(f"Top-p: {config.get('top_p', 1.0)}")
            if 'top_k' in config:
                st.write(f"Top-k: {config['top_k']}")
        else:  # groq
            st.write(f"Temperature: {config.get('temperature', 0.7)}")
            st.write(f"Max tokens: {config.get('max_tokens', 2048)}")
            st.write(f"Top-p: {config.get('top_p', 1.0)}")

        # Show special handling for DSA Sage-01
        if st.session_state.model == 'DSA Sage-01':
            st.write("🌟 Using specialized DSA expert system prompt")

    # Context window settings
    st.session_state.context_window = st.slider(
        "Context Window Size:",
        min_value=2,
        max_value=20,
        value=MAX_CONTEXT_MESSAGES,
        help="Number of recent messages to include in the context. Smaller values save tokens but may reduce context awareness."
    )

    # CAG settings
    st.session_state.use_cache = st.checkbox("Use Cache-Augmented Generation (CAG)", value=True,
                                           help="Use cached responses when available to improve response time")

    if st.session_state.use_cache:
        if st.button("Clear Cache"):
            try:
                # Delete all files in cache directory
                for file in CACHE_DIR.glob("*.pkl"):
                    file.unlink()
                st.success("Cache cleared successfully!")
            except Exception as e:
                st.error(f"Error clearing cache: {e}")

    # Search toggle
    st.session_state.search_enabled = st.toggle("Enable Web Search", value=True)

    # Display chat history in the sidebar
    st.subheader("Chat History")
    if st.session_state.chats:
        for chat_id, chat_data in sorted(st.session_state.chats.items(),
                                       key=lambda x: x[1]["created_at"],
                                       reverse=True):
            col1, col2 = st.columns([0.8, 0.2])
            with col1:
                if st.button(
                    f"📝 {chat_data['title']}",
                    key=f"chat_{chat_id}",
                    help=chat_data["created_at"]
                ):
                    st.session_state.current_chat_id = chat_id
                    st.rerun()
            with col2:
                if st.button("🗑️", key=f"delete_{chat_id}"):
                    delete_chat(chat_id)
                    st.rerun()
    else:
        st.info("No chats yet. Start a new chat!")

# Main interface
if not st.session_state.current_chat_id:
    st.session_state.current_chat_id = create_new_chat()

current_chat = st.session_state.chats[st.session_state.current_chat_id]

if st.session_state.study_mode == "Chat":
    # Chat header
    st.title("🧠DSA Sage - DSA Learning Assistant")
    st.caption(f"Current Model: {st.session_state.model} ({MODEL_PROVIDERS[st.session_state.model].capitalize()}) | CAG: {'Enabled' if st.session_state.use_cache else 'Disabled'} | Web Search: {'Enabled' if st.session_state.search_enabled else 'Disabled'}")

    # Display chat messages
    for msg in current_chat["messages"]:
        with st.chat_message(msg["role"], avatar=msg.get("avatar", "👤" if msg["role"] == "user" else "🧠")):
            st.markdown(msg["content"])
            if msg.get("from_cache", False):
                st.caption("Retrieved from cache ⚡")

    # Display context information
    message_count = len(current_chat["messages"])
    if message_count > MAX_CONTEXT_MESSAGES:
        with st.expander("Context Management Info"):
            st.info(f"This conversation has {message_count} messages. Using most recent {MAX_CONTEXT_MESSAGES} messages plus a summary for context.")
            if current_chat.get("summary"):
                st.caption("Conversation Summary:")
                st.text(current_chat["summary"])

    # Chat input
    user_input = st.chat_input("Ask about any DSA concept or problem...")

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

        # Update context if needed (if we've crossed the threshold)
        if len(current_chat["messages"]) > MAX_CONTEXT_MESSAGES and len(current_chat["messages"]) % 5 == 0:
            # Regenerate summary every 5 messages after hitting the limit
            _ = generate_conversation_summary(current_chat["messages"], st.session_state.current_chat_id)

        # Get optimized message history (summary + recent messages)
        optimized_messages = get_optimized_message_history(st.session_state.current_chat_id)

        # Get response with CAG
        with st.spinner("Generating response..."):
            bot_response, from_cache = get_response_with_cag(
                optimized_messages,
                get_dsa_system_prompt()
            )

            # Add and display bot response
            current_chat["messages"].append({
                "role": "assistant",
                "content": bot_response,
                "avatar": "🧠",
                "from_cache": from_cache
            })

            with st.chat_message("assistant", avatar="🧠"):
                st.markdown(bot_response)
                if from_cache:
                    st.caption("Retrieved from cache ⚡")

# Add a footer
st.markdown("---")
