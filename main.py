import streamlit as st
import hmac
import hashlib

# Function to create a secure password hash
def make_hash(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# Function to check password
def check_password(stored_password, user_password):
    return stored_password == make_hash(user_password)

# Function to verify user credentials
def verify_user(username, password):
    # Hardcoded user credentials - You can modify these
    users = {
        "adityabutani@gmail.com": make_hash("adi123"),
        "jayganatra@gmail.com": make_hash("jay123"),
        "niharnarsana@gmail.com": make_hash("nihar123"),
        "student1@example.com": make_hash("password123")  # Added the sample credential
    }
    
    if username in users:
        return check_password(users[username], password)
    return False

# Page configuration
st.set_page_config(
    page_title="SMARTSTUDY AI",
    page_icon="🎓",
    layout="wide"
)

# Enhanced CSS with more colors and modern design elements
st.markdown("""
    <style>
    /* Main container styling */
    .stApp {
        background: linear-gradient(135deg, #f6f9fc 0%, #eef2f7 100%);
    }

    /* Custom container */
    .custom-container {
        background: rgba(255, 255, 255, 0.95);
        padding: 2.5rem;
        border-radius: 1.5rem;
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.08);
        margin-bottom: 2.5rem;
        border: 1px solid rgba(78, 140, 255, 0.1);
        backdrop-filter: blur(10px);
    }

    /* Feature card */
    .feature-card {
        background: white;
        padding: 1.8rem;
        border-radius: 1rem;
        border-left: none;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
        margin-bottom: 1.5rem;
        transition: transform 0.2s, box-shadow 0.2s;
        border: 1px solid rgba(78, 140, 255, 0.1);
        position: relative;
        overflow: hidden;
    }

    .feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(180deg, #4e8cff 0%, #3a7be0 100%);
    }

    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
    }

    /* Headers */
    .main-header {
        background: linear-gradient(135deg, #2d3436 0%, #1e1e1e 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.5rem;
        font-weight: 800;
        margin-bottom: 1rem;
        text-align: center;
        padding: 1rem 0;
    }

    .sub-header {
        color: #666;
        font-size: 1.6rem;
        margin-bottom: 2.5rem;
        text-align: center;
        font-weight: 300;
    }

    /* Feature title */
    .feature-title {
        color: #2c3e50;
        font-size: 1.4rem;
        font-weight: 700;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .feature-title i {
        font-size: 1.8rem;
        background: linear-gradient(135deg, #4e8cff 0%, #3a7be0 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* Feature description */
    .feature-description {
        color: #666;
        font-size: 1.1rem;
        line-height: 1.6;
    }

    /* Stats container */
    .stats-container {
        display: flex;
        justify-content: space-around;
        text-align: center;
        margin: 3rem 0;
        gap: 2rem;
        flex-wrap: wrap;
    }

    .stat-item {
        background: white;
        padding: 2rem;
        border-radius: 1rem;
        min-width: 200px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s;
        border: 1px solid rgba(78, 140, 255, 0.1);
    }

    .stat-item:hover {
        transform: translateY(-5px);
    }

    .stat-number {
        background: linear-gradient(135deg, #4e8cff 0%, #3a7be0 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }

    .stat-label {
        color: #666;
        font-size: 1.1rem;
        font-weight: 500;
    }

    /* Section headers */
    h3 {
        color: #2c3e50;
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 2rem;
        position: relative;
        padding-bottom: 1rem;
    }

    h3::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        width: 60px;
        height: 4px;
        background: linear-gradient(135deg, #4e8cff 0%, #3a7be0 100%);
        border-radius: 2px;
    }

    /* Get Started steps */
    .steps-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1.5rem;
        margin-top: 2rem;
    }

    .step-card {
        background: white;
        padding: 1.5rem;
        border-radius: 1rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
        border: 1px solid rgba(78, 140, 255, 0.1);
    }

    .step-number {
        background: linear-gradient(135deg, #4e8cff 0%, #3a7be0 100%);
        color: white;
        width: 30px;
        height: 30px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        margin-bottom: 1rem;
    }

    /* Sidebar styling */
    .css-1d391kg {
        background: white;
        border-right: 1px solid rgba(78, 140, 255, 0.1);
    }

    .sidebar-link {
        color: #2c3e50;
        text-decoration: none;
        display: block;
        padding: 0.5rem 0;
        transition: color 0.2s;
    }

    .sidebar-link:hover {
        color: #4e8cff;
    }

    /* Login form styling */
    .login-container {
        max-width: 450px;
        margin: 5rem auto;
        padding: 2.5rem;
        background: white;
        border-radius: 1.5rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(78, 140, 255, 0.1);
    }

    .login-header {
        font-size: 2rem;
        font-weight: 700;
        color: #2c3e50;
        margin-bottom: 2rem;
        text-align: center;
    }

    .login-subheader {
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
        font-size: 1.1rem;
    }

    .login-button {
        background: linear-gradient(135deg, #4e8cff 0%, #3a7be0 100%);
        color: white;
        border: none;
        border-radius: 0.5rem;
        padding: 0.75rem 1.5rem;
        font-size: 1.1rem;
        font-weight: 600;
        cursor: pointer;
        width: 100%;
        transition: transform 0.2s, box-shadow 0.2s;
        margin-top: 1rem;
    }

    .login-button:hover {
        transform: translateY(-3px);
        box-shadow: 0 5px 15px rgba(78, 140, 255, 0.3);
    }

    .login-form {
        display: flex;
        flex-direction: column;
        gap: 1.5rem;
    }

    .form-input {
        padding: 0.75rem;
        border-radius: 0.5rem;
        border: 1px solid #ddd;
        font-size: 1rem;
        transition: border-color 0.2s;
    }

    .form-input:focus {
        border-color: #4e8cff;
        outline: none;
    }

    .password-container {
        position: relative;
    }

    .password-toggle {
        position: absolute;
        right: 10px;
        top: 50%;
        transform: translateY(-50%);
        cursor: pointer;
        color: #666;
    }

    .forgot-password {
        text-align: right;
        font-size: 0.9rem;
        color: #4e8cff;
        text-decoration: none;
    }

    .login-divider {
        display: flex;
        align-items: center;
        margin: 1.5rem 0;
    }

    .login-divider::before,
    .login-divider::after {
        content: '';
        flex: 1;
        border-bottom: 1px solid #ddd;
    }

    .login-divider-text {
        padding: 0 10px;
        color: #666;
        font-size: 0.9rem;
    }

    .error-message {
        color: #e74c3c;
        background-color: #fde9e7;
        padding: 0.75rem;
        border-radius: 0.5rem;
        font-size: 0.9rem;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .success-message {
        color: #27ae60;
        background-color: #e6f9ee;
        padding: 0.75rem;
        border-radius: 0.5rem;
        font-size: 0.9rem;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state for login
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = None
if 'show_password' not in st.session_state:
    st.session_state['show_password'] = False

# Function for logout - This is used outside forms so it's fine
def logout():
    st.session_state['logged_in'] = False
    st.session_state['username'] = None
    st.experimental_rerun()

# Sidebar - Only show content when logged in
with st.sidebar:
    st.write("👤 Welcome to SMARTSTUDY AI")
    st.markdown("### 🧠 Learning Tools")
    st.markdown("""
        <a href="#" class="sidebar-link">🤖 AI Chatbot</a>
        <a href="#" class="sidebar-link">📚 Document Reader</a>
        <a href="#" class="sidebar-link">🧠 Mindmapper</a>
        <a href="#" class="sidebar-link">🎥 YouTube Learning</a>
        <a href="#" class="sidebar-link">📝 AI Quizzer</a>
        <a href="#" class="sidebar-link">🧮 Math Assistant</a>
        <a href="#" class="sidebar-link">🔍 DSA Learning</a>
        <a href="#" class="sidebar-link">📅 Study Planner</a>
        <a href="#" class="sidebar-link">💻 Code Assistant</a>
        <a href="#" class="sidebar-link">🔬 ScholarLens</a>
        <a href="#" class="sidebar-link">📊 CodeVault</a>
        <a href="#" class="sidebar-link">✍️ WriteWise</a>
    """, unsafe_allow_html=True)
    st.markdown("### 📊 My Progress")
    st.markdown("""
        <a href="#" class="sidebar-link">📈 Learning Analytics</a>
        <a href="#" class="sidebar-link">🏆 Achievements</a>
        <a href="#" class="sidebar-link">📋 Study History</a>
    """, unsafe_allow_html=True)

# Main content
st.markdown('<h1 class="main-header">🎓 SMARTSTUDY AI</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Empower Your Learning Journey with AI-Powered Tools</p>', unsafe_allow_html=True)

# Stats section with enhanced design
st.markdown("""
    <div class="stats-container">
        <div class="stat-item">
            <div class="stat-number">12+</div>
            <div class="stat-label">Powerful AI Tools</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">24/7</div>
            <div class="stat-label">Learning Support</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">100%</div>
            <div class="stat-label">Free Access</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Features section with enhanced cards
st.markdown('<div class="custom-container">', unsafe_allow_html=True)
st.markdown("### 🚀 Our Tools")

# Create four columns for better layout
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
        <div class="feature-card">
            <div class="feature-title">🤖 NetSeek</div>
            <div class="feature-description">
                Engage with state-of-the-art AI models including Llama, Gemma, and Mixtral. Experience intelligent conversations that adapt to your learning style and provide personalized assistance for deeper understanding.
            </div>
        </div>

        <div class="feature-card">
            <div class="feature-title">📚 NeuroRead</div>
            <div class="feature-description">
                Transform your documents into interactive learning materials. Our AI analyzes your uploads, generates comprehensive summaries, and creates smart study guides tailored to your needs.
            </div>
        </div>
        
        <div class="feature-card">
            <div class="feature-title">🧠 Mindmapper</div>
            <div class="feature-description">
                Visualize complex concepts with AI-generated mind maps. Convert your notes or any learning material into organized, interconnected diagrams that enhance comprehension and retention.
            </div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div class="feature-card">
            <div class="feature-title">🎥 EduTube</div>
            <div class="feature-description">
                Extract valuable insights from educational videos instantly. Our AI creates structured summaries, key takeaways, and learning points from any YouTube video, making online learning more efficient.
            </div>
        </div>

        <div class="feature-card">
            <div class="feature-title">📝 QuizVerser</div>
            <div class="feature-description">
                Reinforce your learning with adaptive quizzes. Our AI generates personalized questions based on your progress, providing instant feedback and detailed explanations to enhance your understanding.
            </div>
        </div>
        
        <div class="feature-card">
            <div class="feature-title">🧮 GraphiQ</div>
            <div class="feature-description">
                Master mathematical concepts with step-by-step explanations, interactive problem-solving, and visualization of complex equations. Perfect for students of all levels from basic arithmetic to advanced calculus.
            </div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
        <div class="feature-card">
            <div class="feature-title">🔍 DSA Sage</div>
            <div class="feature-description">
                Learn data structures and algorithms interactively with visualizations, code examples, and practice problems. Our AI guides you through efficient solutions and explains complex algorithmic concepts in simple terms.
            </div>
        </div>
        
        <div class="feature-card">
            <div class="feature-title">📅 PrepMaster</div>
            <div class="feature-description">
                Create personalized learning schedules based on your goals, available time, and learning style. Our AI optimizes your study plan for maximum retention and progress while maintaining a healthy work-life balance.
            </div>
        </div>
        
        <div class="feature-card">
            <div class="feature-title">💻 CodeBuddy</div>
            <div class="feature-description">
                Get instant help with coding challenges, bug fixes, and code optimization. Our AI analyzes your code, identifies errors, suggests improvements, and explains programming concepts in an easy-to-understand manner.
            </div>
        </div>
    """, unsafe_allow_html=True)
    
with col4:
    st.markdown("""
        <div class="feature-card">
            <div class="feature-title">🔬 ScholarLens</div>
            <div class="feature-description">
                Find, analyze, and understand academic papers effortlessly. Our AI searches through research repositories, extracts key findings, generates comprehensive summaries, and helps you integrate scholarly insights into your learning.
            </div>
        </div>
        
        <div class="feature-card">
            <div class="feature-title">📊 CodeVault</div>
            <div class="feature-description">
                Practice DSA with a customizable question bank. Generate coding challenges based on topic, difficulty level, and company preferences. Solve them directly in our AI-integrated IDE with real-time feedback and hints.
            </div>
        </div>
        
        <div class="feature-card">
            <div class="feature-title">✍️ WriteWise</div>
            <div class="feature-description">
                Enhance your writing skills with AI-powered assistance. Generate creative content, improve grammar and style, and develop compelling narratives for essays, stories, or professional documents with personalized guidance.
            </div>
        </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# How to Get Started section with enhanced design
st.markdown('<div class="custom-container">', unsafe_allow_html=True)
st.markdown("### 🎯 How to Get Started")

st.markdown("""
    <div class="steps-container">
        <div class="step-card">
            <div class="step-number">1</div>
            <strong>Select a Tool</strong>
            <p>Choose from our suite of AI-powered learning tools in the sidebar</p>
        </div>
        <div class="step-card">
            <div class="step-number">2</div>
            <strong>Start Learning</strong>
            <p>Interact with the AI tools to enhance your learning experience</p>
        </div>
        <div class="step-card">
            <div class="step-number">3</div>
            <strong>Track Progress</strong>
            <p>Monitor your understanding with the AI Quizzer</p>
        </div>
        <div class="step-card">
            <div class="step-number">4</div>
            <strong>Get Help</strong>
            <p>Use the AI Chatbot for additional support and clarification</p>
        </div>
    </div>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)