import streamlit as st
import os
import json
import requests
import time
from dotenv import load_dotenv
import graphviz

# Load environment variables
load_dotenv()

# Get API keys from environment variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

# Constants
DSA_TOPICS = [
    "Arrays", "Strings", "Linked Lists", "Stacks", "Queues", "Hash Tables",
    "Trees", "Heaps", "Graphs", "Sorting", "Searching",
    "Dynamic Programming", "Greedy Algorithms", "Backtracking",
    "Divide and Conquer", "Recursion", "Bit Manipulation"
]

DIFFICULTY_LEVELS = ["Easy", "Medium", "Hard"]

TOP_TECH_COMPANIES = [
    "Google", "Amazon", "Microsoft", "Meta", "Apple",
    "Netflix", "Uber", "Airbnb", "Twitter", "LinkedIn",
    "Salesforce", "Adobe", "Oracle", "IBM", "Tesla"
]

# Set up page configuration
st.set_page_config(
    page_title="CodeBuddy - Interactive Coding Assistant",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem !important;
        color: #4527A0;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    .section-header {
        font-size: 1.5rem;
        color: #5E35B1;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    .code-editor {
        border-radius: 10px;
        margin-top: 1rem;
    }
    .stButton>button {
        background-color: #5E35B1;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        margin-top: 1rem;
    }
    .stButton>button:hover {
        background-color: #4527A0;
    }
    .challenge-card {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #5E35B1;
        margin-bottom: 20px;
    }
    .difficulty-easy {
        color: #2E7D32;
        font-weight: bold;
    }
    .difficulty-medium {
        color: #FF8F00;
        font-weight: bold;
    }
    .difficulty-hard {
        color: #C62828;
        font-weight: bold;
    }
    .similar-question-card {
        background-color: #f1f3f9;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
        border-left: 3px solid #3f51b5;
    }
    .input-section {
        background-color: #f9f9fd;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        border: 1px solid #e0e0f0;
    }
</style>
""", unsafe_allow_html=True)

# Title and introduction
st.markdown("<h1 class='main-title'>💻 CodeBuddy - Interactive Coding Assistant</h1>", unsafe_allow_html=True)
st.markdown("""
Enhance your Data Structures and Algorithms skills with AI-generated coding challenges tailored 
to your preferred topics, difficulty level, and target companies. Practice, debug, and visualize 
your solutions all in one place!
""")

# Initialize session state variables
if 'challenge' not in st.session_state:
    st.session_state.challenge = None
    
if 'user_code' not in st.session_state:
    st.session_state.user_code = ""
    
if 'explanation' not in st.session_state:
    st.session_state.explanation = None
    
if 'improved_solution' not in st.session_state:
    st.session_state.improved_solution = None
    
if 'flowchart' not in st.session_state:
    st.session_state.flowchart = None
    
if 'similar_questions' not in st.session_state:
    st.session_state.similar_questions = None

# Sidebar for additional tools and information
with st.sidebar:
    st.markdown("### About CodeBuddy")
    st.info("""
    CodeBuddy is your interactive coding companion designed to help you practice 
    and improve your DSA skills with personalized challenges, visualization, 
    code improvement suggestions, and similar questions from top tech companies.
    """)
    
    st.markdown("### Tips for Practice")
    st.markdown("""
    - Start with easier problems and gradually increase difficulty
    - Focus on understanding the algorithm, not just the solution
    - Review and optimize your solutions after solving
    - Practice regularly with a variety of topics
    - Study similar questions to recognize patterns
    """)
    
    st.markdown("### Resources")
    st.markdown("""
    - [LeetCode](https://leetcode.com/)
    - [HackerRank](https://www.hackerrank.com/)
    - [GeeksforGeeks](https://www.geeksforgeeks.org/)
    - [AlgoExpert](https://www.algoexpert.io/)
    - [Cracking the Coding Interview](https://www.crackingthecodinginterview.com/)
    """)

# Main page input form
st.markdown("<div class='input-section'>", unsafe_allow_html=True)
st.markdown("### 🔍 Challenge Configuration")

col1, col2 = st.columns(2)
with col1:
    # Topic selection (multi-select)
    selected_topics = st.multiselect(
        "Select DSA Topics",
        options=DSA_TOPICS,
        default=["Arrays", "Strings"]
    )
    
    # Difficulty selection (single-select)
    difficulty = st.select_slider(
        "Select Difficulty Level",
        options=DIFFICULTY_LEVELS,
        value="Medium"
    )

with col2:
    # Company selection (multi-select with a default)
    target_companies = st.multiselect(
        "Target Companies",
        options=TOP_TECH_COMPANIES,
        default=["Google", "Amazon"]
    )
    
    # Generate button
    generate_button = st.button("Generate Challenge", type="primary", use_container_width=True)
    
st.markdown("</div>", unsafe_allow_html=True)

# Function to search for relevant information using Serper API
def search_relevant_info(query):
    url = "https://google.serper.dev/search"
    payload = json.dumps({
        "q": query,
        "num": 5
    })
    headers = {
        'X-API-KEY': SERPER_API_KEY,
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.request("POST", url, headers=headers, data=payload)
        return response.json()
    except Exception as e:
        st.error(f"Error fetching information: {e}")
        return None

# Function to search for similar questions
def find_similar_questions(problem_title, topics):
    topics_str = ", ".join(topics)
    query = f"similar coding interview questions to {problem_title} {topics_str} leetcode hackerrank"
    
    try:
        search_results = search_relevant_info(query)
        similar_questions = []
        
        if search_results and 'organic' in search_results:
            for i, result in enumerate(search_results['organic'][:5]):
                if 'title' in result and 'link' in result and 'snippet' in result:
                    similar_questions.append({
                        'title': result['title'],
                        'link': result['link'],
                        'snippet': result['snippet']
                    })
        
        return similar_questions
    except Exception as e:
        st.error(f"Error finding similar questions: {e}")
        return []

# Function to generate challenge using Groq API with Mistral Saba 24B model
def generate_dsa_challenge(topics, difficulty, companies):
    # Create prompt for the AI model
    topics_str = ", ".join(topics)
    companies_str = ", ".join(companies)
    
    # Search for relevant information about the companies and DSA topics
    search_results = search_relevant_info(f"{topics_str} coding interview questions at {companies_str}")
    
    context = ""
    if search_results and 'organic' in search_results:
        for i, result in enumerate(search_results['organic'][:3]):
            if 'snippet' in result:
                context += f"{result['snippet']}\n"
    
    prompt = f"""
    You are an expert DSA (Data Structures and Algorithms) interview coach.

    Create a challenging but fair coding interview problem that:
    - Focuses on these DSA topics: {topics_str}
    - Has a {difficulty} difficulty level
    - Is similar to problems asked at these companies: {companies_str}
    
    Additional context from real interview questions:
    {context}
    
    Please format your response with the following sections:
    
    1. PROBLEM TITLE: A concise, descriptive title for the problem.
    
    2. PROBLEM STATEMENT: Clearly describe the problem, including any constraints and examples.
    
    3. EXAMPLE INPUT/OUTPUT: Provide at least 2 examples with explanations.
    
    4. CONSTRAINTS: List all constraints (e.g., time/space complexity requirements, input size limits).
    
    5. EXPECTED SOLUTION APPROACH: A brief hint about the expected solution approach without giving away the full solution.
    
    Format the response as a clean, readable markdown document that would be appropriate for a technical interview setting.
    """
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "llama3-70b-8192",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 1500,
    }
    
    try:
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                               headers=headers, 
                               json=payload)
        
        if response.status_code == 200:
            result = response.json()
            challenge = result['choices'][0]['message']['content']
            return challenge
        else:
            st.error(f"Error from Groq API: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error generating challenge: {e}")
        return None

# Function to generate flowchart visualization of code
def generate_flowchart(code):
    # Create prompt for the AI model to convert code to flowchart description
    prompt = f"""
    Convert the following code to a detailed flowchart description in DOT language (graphviz) format:
    
    ```
    {code}
    ```
    
    Please provide only the dot language code without any explanations or markdown formatting.
    The flowchart should visualize the main algorithm logic, decisions, and flow.
    """
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "llama3-70b-8192",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
        "max_tokens": 1000,
    }
    
    try:
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                               headers=headers, 
                               json=payload)
        
        if response.status_code == 200:
            result = response.json()
            dot_code = result['choices'][0]['message']['content']
            
            # Clean up the dot code (remove markdown formatting if present)
            if "```dot" in dot_code:
                dot_code = dot_code.split("```dot")[1].split("```")[0].strip()
            elif "```" in dot_code:
                dot_code = dot_code.split("```")[1].split("```")[0].strip()
            
            return dot_code
        else:
            st.error(f"Error generating flowchart: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error in flowchart generation: {e}")
        return None

# Function to explain code
def explain_code(code):
    prompt = f"""
    Explain the following code in detail, including:
    1. A high-level overview of the algorithm
    2. Time and space complexity analysis
    3. Key implementation details for each section
    4. Potential edge cases and how they're handled
    
    ```
    {code}
    ```
    
    Make your explanation clear and educational, suitable for someone learning DSA concepts.
    """
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "llama3-70b-8192",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
        "max_tokens": 1500,
    }
    
    try:
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                               headers=headers, 
                               json=payload)
        
        if response.status_code == 200:
            result = response.json()
            explanation = result['choices'][0]['message']['content']
            return explanation
        else:
            st.error(f"Error generating explanation: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error in code explanation: {e}")
        return None

# Function to improve code
def improve_solution(code, problem_statement):
    prompt = f"""
    Given this problem:
    
    {problem_statement}
    
    And this code solution:
    
    ```
    {code}
    ```
    
    Please improve this solution by:
    1. Optimizing for better time and/or space complexity if possible
    2. Making the code more readable and maintainable
    3. Adding appropriate comments
    4. Handling edge cases better
    5. Applying best coding practices
    
    Provide the improved code with explanations of the key improvements made.
    """
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "llama3-70b-8192",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
        "max_tokens": 1500,
    }
    
    try:
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                               headers=headers, 
                               json=payload)
        
        if response.status_code == 200:
            result = response.json()
            improved_solution = result['choices'][0]['message']['content']
            return improved_solution
        else:
            st.error(f"Error improving solution: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error in solution improvement: {e}")
        return None

# Generate challenge when button is clicked
if generate_button:
    if not selected_topics:
        st.warning("Please select at least one DSA topic")
    else:
        with st.spinner("Generating your personalized DSA challenge..."):
            st.session_state.challenge = generate_dsa_challenge(selected_topics, difficulty, target_companies)
            # Reset other state variables
            st.session_state.user_code = ""
            st.session_state.explanation = None
            st.session_state.improved_solution = None
            st.session_state.flowchart = None
            st.session_state.similar_questions = None

# Main content area
if st.session_state.challenge:
    # Display the challenge
    st.markdown("<div class='challenge-card'>", unsafe_allow_html=True)
    st.markdown(st.session_state.challenge)
    
    # Add difficulty tag with appropriate color
    difficulty_class = f"difficulty-{difficulty.lower()}"
    st.markdown(f"<p>Difficulty: <span class='{difficulty_class}'>{difficulty}</span></p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Code editor
    st.markdown("<h3 class='section-header'>💻 Code Editor</h3>", unsafe_allow_html=True)
    st.session_state.user_code = st.text_area(
        "Write your solution here:",
        value=st.session_state.user_code,
        height=300,
        key="code_editor"
    )
    
    # Action buttons
    st.markdown("<h3 class='section-header'>🛠️ Code Tools</h3>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("Run Code", use_container_width=True):
            st.info("Code execution feature is coming soon. For now, please use the visualization and explanation tools.")
    
    with col2:
        if st.button("Debug", use_container_width=True):
            st.info("Debugging feature is coming soon. For now, please use the explanation and improvement tools.")
    
    with col3:
        visualize_button = st.button("Visualize", use_container_width=True)
    
    with col4:
        explain_button = st.button("Explain Code", use_container_width=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        improve_button = st.button("Improve Solution", use_container_width=True)
    
    with col2:
        similar_button = st.button("Find Similar Questions", use_container_width=True)
    
    with col3:
        if st.button("Submit Solution", use_container_width=True):
            st.success("Solution submitted successfully!")
    
    # Process visualization request
    if visualize_button and st.session_state.user_code:
        with st.spinner("Generating visualization..."):
            dot_code = generate_flowchart(st.session_state.user_code)
            if dot_code:
                try:
                    # Create and render the graph
                    graph = graphviz.Source(dot_code)
                    st.session_state.flowchart = graph
                except Exception as e:
                    st.error(f"Error rendering flowchart: {e}")
                    st.code(dot_code, language="dot")
    
    # Process explanation request
    if explain_button and st.session_state.user_code:
        with st.spinner("Generating explanation..."):
            st.session_state.explanation = explain_code(st.session_state.user_code)
    
    # Process improvement request
    if improve_button and st.session_state.user_code:
        with st.spinner("Improving your solution..."):
            st.session_state.improved_solution = improve_solution(st.session_state.user_code, st.session_state.challenge)
    
    # Process similar questions request
    if similar_button and st.session_state.challenge:
        with st.spinner("Finding similar questions..."):
            # Extract problem title from the challenge
            challenge_lines = st.session_state.challenge.split('\n')
            problem_title = ""
            for line in challenge_lines:
                if "PROBLEM TITLE:" in line:
                    problem_title = line.replace("PROBLEM TITLE:", "").strip()
                    break
            
            if problem_title:
                st.session_state.similar_questions = find_similar_questions(problem_title, selected_topics)
            else:
                st.warning("Could not extract problem title from the challenge")
    
    # Display flowchart if available
    if st.session_state.flowchart:
        st.markdown("<h3 class='section-header'>📊 Solution Visualization</h3>", unsafe_allow_html=True)
        st.graphviz_chart(st.session_state.flowchart)
    
    # Display explanation if available
    if st.session_state.explanation:
        st.markdown("<h3 class='section-header'>📝 Code Explanation</h3>", unsafe_allow_html=True)
        st.markdown(st.session_state.explanation)
    
    # Display improved solution if available
    if st.session_state.improved_solution:
        st.markdown("<h3 class='section-header'>⚡ Improved Solution</h3>", unsafe_allow_html=True)
        st.markdown(st.session_state.improved_solution)
    
    # Display similar questions if available
    if st.session_state.similar_questions and len(st.session_state.similar_questions) > 0:
        st.markdown("<h3 class='section-header'>🔍 Similar Questions</h3>", unsafe_allow_html=True)
        for i, question in enumerate(st.session_state.similar_questions):
            st.markdown(f"<div class='similar-question-card'>", unsafe_allow_html=True)
            st.markdown(f"**{i+1}. [{question['title']}]({question['link']})**")
            st.markdown(f"{question['snippet']}")
            st.markdown("</div>", unsafe_allow_html=True)
    
else:
    # When no challenge is generated yet
    st.markdown("""
    ### 👆 Configure your challenge parameters above and click "Generate Challenge"
    
    Select your preferred:
    - DSA topics you want to practice
    - Difficulty level
    - Target companies whose interview questions you want to simulate
    
    Then click "Generate Challenge" to create a personalized DSA problem!
    """)
    
    # Display sample challenge card
    st.markdown("<h3 class='section-header'>Sample Challenge Preview</h3>", unsafe_allow_html=True)
    st.markdown("<div class='challenge-card'>", unsafe_allow_html=True)
    st.markdown("""
    ## PROBLEM TITLE: Balanced Binary Tree Validator
    
    ### PROBLEM STATEMENT
    Given the root of a binary tree, determine if it is height-balanced. A height-balanced binary tree is a tree where the depth of the two subtrees of every node never differs by more than one.
    
    ### EXAMPLE INPUT/OUTPUT
    **Example 1:**
    ```
    Input: root = [3,9,20,null,null,15,7]
    Output: true
    ```
    
    **Example 2:**
    ```
    Input: root = [1,2,2,3,3,null,null,4,4]
    Output: false
    ```
    
    ### CONSTRAINTS
    - The number of nodes in the tree is in the range [0, 5000]
    - -10^4 <= Node.val <= 10^4
    
    ### EXPECTED SOLUTION APPROACH
    Consider using a recursive approach to calculate the height of each subtree and check for balance condition at each node.
    """)
    st.markdown(f"<p>Difficulty: <span class='difficulty-medium'>Medium</span></p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center">
    <p>💻 CodeBuddy - Your Interactive Coding Assistant</p>
    <p>Practice makes perfect! Generate new challenges regularly to improve your problem-solving abilities.</p>
</div>
""", unsafe_allow_html=True)