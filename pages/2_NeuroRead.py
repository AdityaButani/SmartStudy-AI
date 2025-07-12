import streamlit as st
from groq import Groq
import os
from dotenv import load_dotenv
from pdfminer.high_level import extract_text
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Page configuration
st.set_page_config(
    page_title="AI Document Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern, clean CSS
st.markdown("""
    <style>
    /* Reset default padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* Clean message styling */
    .chat-message {
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 0.5rem;
        background: white;
        border: 1px solid #e5e7eb;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
    }

    .user-message {
        border-left: 4px solid #2563eb;
    }

    .assistant-message {
        border-left: 4px solid #059669;
    }

    /* Message headers */
    .message-header {
        font-size: 0.875rem;
        font-weight: 500;
        margin-bottom: 0.5rem;
        color: #4b5563;
    }

    /* Input field styling */
    .stTextInput > div > div > input {
        background: white;
        border: 1px solid #e5e7eb;
        padding: 0.75rem 1rem;
        font-size: 1rem;
        border-radius: 0.5rem;
    }

    /* Button styling */
    .stButton > button {
        background: #2563eb;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        font-weight: 500;
    }

    .stButton > button:hover {
        background: #1d4ed8;
    }

    /* File uploader */
    .uploadedFile {
        border: 1px solid #e5e7eb;
        padding: 0.5rem;
        border-radius: 0.375rem;
        margin: 0.5rem 0;
        background: white;
    }

    /* Status messages */
    .success-message {
        color: #059669;
        font-size: 0.875rem;
        padding: 0.5rem;
        background: #ecfdf5;
        border-radius: 0.375rem;
        margin: 0.5rem 0;
    }

    .info-message {
        color: #2563eb;
        font-size: 0.875rem;
        padding: 0.5rem;
        background: #eff6ff;
        border-radius: 0.375rem;
        margin: 0.5rem 0;
    }

    /* Headers */
    h1, h2, h3 {
        color: #111827;
        font-weight: 600;
    }

    /* Card-like containers */
    .content-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 0.5rem;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize Groq client
load_dotenv()
groq_api_key = os.environ.get("GROQ_API_KEY")

if not groq_api_key:
    st.error("❌ GROQ_API_KEY environment variable not set.")
    st.stop()

client = Groq(api_key=groq_api_key)

# Model configuration
MODELS = {
    'Llama3 8b': 'llama3-8b-8192',
    'Llama3 70b': 'llama3-70b-8192',
}

# Helper functions (keeping the same implementation)
def get_pdf_text(pdf_docs):
    text_content = []
    for uploaded_file in pdf_docs:
        if uploaded_file.type == "application/pdf":
            try:
                text = extract_text(uploaded_file)
                text_content.append({
                    'filename': uploaded_file.name,
                    'content': text
                })
            except Exception as e:
                st.error(f"Error processing {uploaded_file.name}: {str(e)}")
    return text_content

@st.cache_resource
def create_tfidf_vectorizer():
    return TfidfVectorizer()

def get_relevant_chunks(text, user_question, vectorizer, top_n=2):
    chunk_size = 10000
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

    if not chunks:
        return []

    chunk_vectors = vectorizer.fit_transform(chunks)
    question_vector = vectorizer.transform([user_question])
    similarities = cosine_similarity(question_vector, chunk_vectors).flatten()

    if np.all(similarities == 0):
        return []

    top_indices = np.argsort(similarities)[::-1][:top_n]
    return [chunks[i] for i in top_indices]

def truncate_text(text, max_tokens=6000):
    tokens = text.split()
    return ' '.join(tokens[:max_tokens]) if len(tokens) > max_tokens else text

def get_answer(user_question, context, file_names):
    context = truncate_text(context)
    prompt = f"""
    Based on the following documents: {', '.join(file_names)}

    Context: {context}

    Question: {user_question}

    Please provide a clear and concise answer based on the context provided.
    If the answer cannot be found in the context, please say so.
    """

    try:
        completion = client.chat.completions.create(
            model=MODELS['Llama3 8b'],
            messages=[
                {"role": "system", "content": "You are a helpful document analysis assistant. Provide accurate answers based on the given context."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1024,
            top_p=1,
            stream=False,
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating answer: {str(e)}"


def main():
    # Improved header with a more prominent title
    st.title("📚 NeuroRead - AI Powered Document Assistant")
    st.subheader("Ask questions and get insights from your documents")

    # Expandable section for instructions
    with st.expander("ℹ️ How to use this app"):
        st.markdown("""
            1.  **Upload Documents:** Use the sidebar to upload one or more PDF documents.
            2.  **Wait for Processing:**  The documents will be processed automatically. Please wait for the confirmation message.
            3.  **Ask Questions:** Type your question in the input box below and click the "Ask" button.
            4.  **Get Answers:**  The AI will analyze your documents and provide an answer.

            **Supported file types:** PDF
            """)

    # Initialize session state
    if "doc_reader_messages" not in st.session_state:
        st.session_state.doc_reader_messages = []
    if "processed_docs" not in st.session_state:
        st.session_state.processed_docs = None

    # Sidebar for file upload
    with st.sidebar:
        st.subheader("📁 Upload Documents")
        uploaded_files = st.file_uploader(
            "Choose PDF files",
            accept_multiple_files=True,
            type=['pdf']
        )

        if uploaded_files:
            st.markdown(f'<div class="success-message">📄 {len(uploaded_files)} files uploaded</div>', unsafe_allow_html=True)
            for file in uploaded_files:
                st.markdown(f'<div class="uploadedFile">📎 {file.name}</div>', unsafe_allow_html=True)

    # Main content area
    if uploaded_files:
        if not st.session_state.processed_docs:
            with st.status("Processing documents...", expanded=True) as status:
                try:
                    st.session_state.processed_docs = get_pdf_text(uploaded_files)
                    if st.session_state.processed_docs:
                        status.update(label="✅ Documents processed", state="complete")
                    else:
                        status.update(label="❌ Processing failed", state="error")
                        st.stop()
                except Exception as e:
                    status.update(label=f"❌ Processing failed: {e}", state="error")
                    st.stop()

        # Question input in a styled container
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        user_question = st.text_input("Ask a question about your documents:", key="question_input", placeholder="Type your question here...")
        col1, col2 = st.columns([4, 1])
        with col2:
            ask_button = st.button("Ask", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if user_question and ask_button:
            with st.spinner("Analyzing..."):
                all_text = " ".join([doc['content'] for doc in st.session_state.processed_docs])
                vectorizer = create_tfidf_vectorizer()
                relevant_chunks = get_relevant_chunks(all_text, user_question, vectorizer)
                context = "\n".join(relevant_chunks)

                file_names = [doc['filename'] for doc in st.session_state.processed_docs]
                answer = get_answer(user_question, context, file_names)

                # Add new messages to the beginning of the list to reverse the order
                st.session_state.doc_reader_messages.insert(0, {"role": "user", "content": user_question})
                st.session_state.doc_reader_messages.insert(0, {"role": "assistant", "content": answer})

        # Conversation display
        if st.session_state.doc_reader_messages:
            st.markdown("### Conversation")
            for message in st.session_state.doc_reader_messages:
                if message["role"] == "user":
                    st.markdown(f"""
                        <div class="chat-message user-message">
                            <div class="message-header">You</div>
                            {message['content']}
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                        <div class="chat-message assistant-message">
                            <div class="message-header">Assistant</div>
                            {message['content']}
                        </div>
                    """, unsafe_allow_html=True)

            # Clear chat button
            col1, col2, col3 = st.columns([3, 1, 3])
            with col2:
                if st.button("Clear Chat", use_container_width=True):
                    st.session_state.doc_reader_messages = []
                    st.experimental_rerun()
    else:
        # Welcome message with more emphasis
        st.markdown("""
            <div class="content-card" style="text-align: center;">
                <h2>👋 Welcome!</h2>
                <p style="color: #6b7280; margin: 1rem 0;">
                    Upload PDF documents using the sidebar to unlock AI-powered document analysis.
                </p>
            </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

