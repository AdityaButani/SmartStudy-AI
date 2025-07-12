import streamlit as st
import os
import time
import re
from dotenv import load_dotenv
import groq
import tempfile
import subprocess
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
import base64
import json
import requests
import graphviz
from markdown import markdown

# Load environment variables
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")
serper_api_key = os.getenv("SERPER_API_KEY")

# Initialize Groq client
client = groq.Client(api_key=groq_api_key)

# Set page config
st.set_page_config(
    page_title="CodeBuddy - Coding Assistant",
    page_icon="🧩",
    layout="wide"
)

# Define supported languages
SUPPORTED_LANGUAGES = {
    "Python": {"ext": "py", "compiler": "python"},
    "JavaScript": {"ext": "js", "compiler": "node"},
    "Java": {"ext": "java", "compiler": "javac"},
    "C++": {"ext": "cpp", "compiler": "g++"},
    "HTML/CSS": {"ext": "html", "compiler": None},
    "SQL": {"ext": "sql", "compiler": None},
}

# DSA topics
DSA_TOPICS = [
    "Arrays", "Linked Lists", "Stacks", "Queues", "Trees", "Graphs", 
    "Sorting Algorithms", "Searching Algorithms", "Dynamic Programming", 
    "Greedy Algorithms", "Backtracking", "Hashing", "Heap", "String Manipulation",
    "Bit Manipulation", "Recursion", "Binary Search", "Sliding Window",
    "Two Pointers", "BFS/DFS", "Trie", "Union Find", "Math"
]

# Difficulty levels
DIFFICULTY_LEVELS = ["Easy", "Medium", "Hard"]

# Top tech companies
TECH_COMPANIES = [
    "Amazon", "Google", "Microsoft", "Meta (Facebook)", "Apple", 
    "Netflix", "Uber", "Airbnb", "Twitter", "LinkedIn", 
    "Bloomberg", "Adobe", "Oracle", "Salesforce", "IBM"
]

# CSS for styling
def local_css():
    st.markdown("""
    <style>
    .code-editor {
        border-radius: 5px;
        border: 1px solid #ccc;
        font-family: monospace;
    }
    .output-area {
        background-color: #f0f0f0;
        padding: 10px;
        border-radius: 5px;
        color: #333;
        font-family: monospace;
        height: 200px;
        overflow-y: auto;
        white-space: pre-wrap;
    }
    .suggestion-area {
        background-color: #f9f9f9;
        padding: 10px;
        border-radius: 5px;
        border-left: 3px solid #4CAF50;
        margin-top: 10px;
    }
    .error-message {
        color: #D32F2F;
        font-weight: bold;
    }
    .stButton>button {
        width: 100%;
    }
    .language-selector {
        padding: 10px;
    }
    .challenge-container {
        background-color: #f0f8ff;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 20px;
        border-left: 4px solid #4169e1;
    }
    .difficulty-easy {
        background-color: #e6ffe6;
        border-left: 4px solid #4CAF50;
    }
    .difficulty-medium {
        background-color: #fff8e6;
        border-left: 4px solid #FFA500;
    }
    .difficulty-hard {
        background-color: #ffe6e6;
        border-left: 4px solid #D32F2F;
    }
    .problem-description {
        font-size: 16px;
        line-height: 1.6;
        background-color: #f9f9f9;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 15px;
    }
    .problem-description h4 {
        color: #2C3E50;
        margin-top: 15px;
        margin-bottom: 10px;
    }
    .problem-description pre {
        background-color: #f1f1f1;
        padding: 10px;
        border-radius: 3px;
        overflow-x: auto;
    }
    .problem-description code {
        font-family: 'Courier New', monospace;
    }
    .problem-examples {
        background-color: #f5f5f5;
        padding: 10px;
        border-left: 3px solid #3498db;
        margin-bottom: 10px;
    }
    .graph-container {
        background-color: white;
        padding: 15px;
        border-radius: 5px;
        margin-top: 15px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
    }
    </style>
    """, unsafe_allow_html=True)

def run_code(code, language):
    """Execute code in the selected language and return the output"""
    if language not in SUPPORTED_LANGUAGES:
        return "Unsupported language", "error"
    
    lang_details = SUPPORTED_LANGUAGES[language]
    
    if lang_details["compiler"] is None:
        return "Preview not available for this language", "info"
    
    with tempfile.NamedTemporaryFile(suffix=f".{lang_details['ext']}", delete=False) as f:
        f.write(code.encode())
        temp_file = f.name
    try:
        if language == "Python":
            result = subprocess.run(["python", temp_file], capture_output=True, text=True, timeout=5)
        elif language == "JavaScript":
            result = subprocess.run(["node", temp_file], capture_output=True, text=True, timeout=5)
        elif language == "Java":
            # Compile first
            compile_result = subprocess.run(["javac", temp_file], capture_output=True, text=True, timeout=5)
            if compile_result.returncode != 0:
                return compile_result.stderr, "error"
            
            # Extract class name
            class_name = os.path.basename(temp_file).replace(".java", "")
            result = subprocess.run(["java", "-cp", os.path.dirname(temp_file), class_name], 
                                    capture_output=True, text=True, timeout=5)
        elif language == "C++":
            output_file = temp_file.replace(f".{lang_details['ext']}", "")
            compile_result = subprocess.run(["g++", temp_file, "-o", output_file], 
                                            capture_output=True, text=True, timeout=5)
            if compile_result.returncode != 0:
                return compile_result.stderr, "error"
            
            result = subprocess.run([output_file], capture_output=True, text=True, timeout=5)
        
        os.unlink(temp_file)
        
        if result.returncode != 0:
            return result.stderr, "error"
        return result.stdout, "success"
    
    except subprocess.TimeoutExpired:
        return "Code execution timed out (limit: 5 seconds)", "timeout"
    except Exception as e:
        return str(e), "error"
    finally:
        # Clean up
        if os.path.exists(temp_file):
            os.unlink(temp_file)

def get_ai_suggestion(code, language, prompt):
    """Get code suggestions from Groq API"""
    try:
        system_message = f"""You are an expert coding assistant specializing in {language} programming. 
        Provide helpful, concise, and technically correct code suggestions or fixes.
        When fixing code, explain the issues and how to resolve them.
        Only show code snippets when necessary."""
        
        # Prepare user message based on the prompt type
        if prompt == "debug":
            user_message = f"Debug this {language} code and explain the issues:\n\n```{language}\n{code}\n```"
        elif prompt == "complete":
            user_message = f"Complete or improve this {language} code:\n\n```{language}\n{code}\n```"
        elif prompt == "explain":
            user_message = f"Explain how this {language} code works:\n\n```{language}\n{code}\n```"
        elif prompt == "flowchart":
            user_message = f"""Generate a Graphviz DOT representation for this {language} code. 
            Create a flowchart that shows the main logic flow of the algorithm:
            
            ```{language}
            {code}
            ```
            
            Return only the DOT code between ```dot and ``` tags, with no other explanation."""
        else:
            user_message = f"Help me with this {language} code:\n\n```{language}\n{code}\n```"
        
        # Make API call
        chat_completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # Use the Mixtral model which is good for code
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            temperature=0.3,
            max_tokens=1024
        )
        
        # Extract the response
        suggestion = chat_completion.choices[0].message.content
        return suggestion
    except Exception as e:
        return f"Error getting suggestion: {str(e)}"

def highlight_code(code, language):
    """Highlight code syntax using Pygments"""
    try:
        if language == "HTML/CSS":
            lexer = get_lexer_by_name("html")
        else:
            lexer = get_lexer_by_name(language.lower())
        formatter = HtmlFormatter(style="friendly")
        highlighted = highlight(code, lexer, formatter)
        
        # Add formatter CSS
        pygments_css = f"<style>{formatter.get_style_defs('.highlight')}</style>"
        return pygments_css + highlighted
    except Exception:
        # Return plain code if highlighting fails
        return f"<pre>{code}</pre>"

def analyze_errors(output, language):
    """Analyze error messages and provide suggestions"""
    if language == "Python":
        # Look for common Python errors
        if "IndentationError" in output:
            return "Check your indentation. Python uses indentation to define code blocks."
        elif "SyntaxError" in output:
            return "There's a syntax error in your code. Check for missing colons, parentheses, or quotes."
        elif "NameError" in output:
            return "A variable or function is being used before it's defined."
        elif "TypeError" in output:
            return "You're using an operation on incompatible data types."
    
    return None

def extract_graphviz_code(text):
    """Extract Graphviz DOT code from text response"""
    dot_code_match = re.search(r'```dot\s*([\s\S]*?)\s*```', text)
    if dot_code_match:
        return dot_code_match.group(1).strip()
    
    # Alternative pattern without explicit dot tag
    code_match = re.search(r'```\s*(digraph\s*[\s\S]*?)\s*```', text)
    if code_match:
        return code_match.group(1).strip()
    
    return None

def generate_code_flowchart(code, language):
    """Generate a flowchart visualization of the code using Graphviz"""
    try:
        # Get the DOT representation from the LLM
        dot_text = get_ai_suggestion(code, language, "flowchart")
        
        # Extract the DOT code
        dot_code = extract_graphviz_code(dot_text)
        
        if not dot_code:
            return None, "Failed to generate flowchart DOT code."
        
        # Create the Graphviz object
        graph = graphviz.Source(dot_code)
        return graph, None
    except Exception as e:
        return None, f"Error generating flowchart: {str(e)}"

def generate_dsa_challenge(topic, difficulty, company, language):
    """Generate a DSA challenge using Groq LLM"""
    try:
        company_prompt = f" that has been asked in {company} interviews" if company != "Any" else ""
        
        system_message = f"""You are an expert DSA (Data Structures and Algorithms) coach creating interview preparation problems.
        Create a challenging but solvable coding problem related to {topic} at {difficulty} difficulty level{company_prompt}.
        
        Structure your response exactly as follows:
        {{
            "title": "Problem title",
            "description": "Detailed problem description with examples. Use markdown formatting for clarity.",
            "constraints": "Input/output constraints",
            "examples": [
                {{"input": "Example input", "output": "Expected output", "explanation": "Why this is the output"}}
            ],
            "starter_code": "Basic starter code in {language}",
            "test_cases": [
                {{"input": "Test input", "expected": "Expected output"}}
            ],
            "hints": ["Hint 1", "Hint 2"],
            "solution_approach": "High-level approach to solve this problem"
        }}
        
        Make sure all string values are properly escaped and the JSON is valid.
        For the description, use rich markdown formatting including:
        - Headers with # and ## for sections
        - Bullet points with * and -
        - Code blocks with ```
        - Bold and italic text
        - Mathematical notation where appropriate
        
        Keep the starter_code concise and use simple string representation.
        """
        
        # Make API call without forcing JSON format to avoid validation errors
        chat_completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"Create a {difficulty} level {topic} problem for {language} programming language{company_prompt}."}
            ],
            temperature=0.5,
            max_tokens=2048
            # Removed response_format to get raw text instead of validated JSON
        )
        
        # Extract the response
        response_text = chat_completion.choices[0].message.content
        
        # Try to extract JSON from the response text
        # Sometimes the model might return additional text before or after the JSON
        import re
        import json
        
        # Find JSON object in the response
        json_match = re.search(r'({[\s\S]*})', response_text)
        if json_match:
            json_str = json_match.group(1)
            try:
                challenge = json.loads(json_str)
                return challenge
            except json.JSONDecodeError:
                # If still can't parse, create a simplified challenge structure
                st.warning("Couldn't parse JSON response from LLM. Creating a simplified challenge.")
        
        # Fallback: create a simplified challenge if JSON parsing fails
        fallback_challenge = {
            "title": f"{topic} Challenge",
            "description": "Solve this algorithm problem",
            "constraints": "Standard constraints apply",
            "examples": [{"input": "Example input", "output": "Example output", "explanation": "Basic explanation"}],
            "starter_code": f"# Write your {language} solution here\n\n",
            "test_cases": [{"input": "Test input", "expected": "Expected output"}],
            "hints": ["Try to solve this step by step"],
            "solution_approach": "Think about the problem carefully"
        }
        
        # Try to extract title and description from text response if JSON parsing failed
        title_match = re.search(r'["\']title["\']:\s*["\']([^"\']+)["\']', response_text)
        if title_match:
            fallback_challenge["title"] = title_match.group(1)
            
        desc_match = re.search(r'["\']description["\']:\s*["\']([^"\']+)["\']', response_text)
        if desc_match:
            fallback_challenge["description"] = desc_match.group(1)
        
        return fallback_challenge
            
    except Exception as e:
        st.error(f"Error generating challenge: {str(e)}")
        # Return a basic challenge structure in case of error
        return {
            "title": f"{topic} Problem",
            "description": "Please try generating another challenge.",
            "constraints": "N/A",
            "examples": [{"input": "Example", "output": "Example", "explanation": "Example"}],
            "starter_code": f"# Write your {language} solution here\n\n",
            "test_cases": [],
            "hints": ["Try again with different parameters"],
            "solution_approach": "N/A"
        }

def search_similar_problems(topic, company):
    """Search for similar problems using Serper API"""
    try:
        if not serper_api_key:
            return "Serper API key not configured. Cannot fetch similar problems."
        
        query = f"{topic} coding interview problem {company if company != 'Any' else 'tech companies'}"
        
        payload = {
            "q": query,
            "gl": "us",
            "hl": "en",
            "num": 5
        }
        
        headers = {
            "X-API-KEY": serper_api_key,
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            "https://google.serper.dev/search",
            json=payload,
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            similar_problems = []
            
            # Extract organic search results
            if "organic" in result:
                for item in result["organic"][:3]:  # Get top 3 results
                    similar_problems.append({
                        "title": item.get("title", ""),
                        "link": item.get("link", ""),
                        "snippet": item.get("snippet", "")
                    })
            
            return similar_problems
        else:
            return f"Error: {response.status_code}"
    except Exception as e:
        return f"Error searching similar problems: {str(e)}"

def main():
    local_css()
    
    st.title("👨‍💻 CodeBuddy - Interactive Coding Assistant")
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Code Editor", "DSA Challenges", "About"])
    
    if page == "Code Editor":
        code_editor_page()
    elif page == "DSA Challenges":
        dsa_challenges_page()
    else:
        about_page()

def code_editor_page():
    st.header("Code Editor")
    
    # Language selection
    col1, col2 = st.columns([1, 3])
    with col1:
        language = st.selectbox("Select Language", list(SUPPORTED_LANGUAGES.keys()), key="lang_select")
    
    with col2:
        st.write("")  # Spacer
    
    # Code input
    if "code" not in st.session_state:
        st.session_state.code = "# Write your code here\n"
    
    code = st.text_area("Code Editor", st.session_state.code, height=300, key="code_editor", 
                       help="Write your code here")
    st.session_state.code = code
    
    # Action buttons
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        run_button = st.button("Run Code", key="run", use_container_width=True)
    with col2:
        debug_button = st.button("Debug", key="debug", use_container_width=True)
    with col3:
        improve_button = st.button("Improve", key="improve", use_container_width=True)
    with col4:
        explain_button = st.button("Explain", key="explain", use_container_width=True)
    with col5:
        flowchart_button = st.button("Visualize Flow", key="flowchart", use_container_width=True)
    
    # Output area
    st.subheader("Output")
    output_placeholder = st.empty()
    
    # Suggestion area
    suggestion_placeholder = st.empty()
    
    # Flowchart area
    flowchart_placeholder = st.empty()
    
    # Run code
    if run_button:
        with st.spinner("Running code..."):
            output, status = run_code(code, language)
            
            if status == "error":
                output_placeholder.markdown(f'<div class="output-area error-message">{output}</div>', unsafe_allow_html=True)
                
                # Automatically analyze errors
                error_suggestion = analyze_errors(output, language)
                if error_suggestion:
                    suggestion_placeholder.markdown(f'<div class="suggestion-area"><strong>💡 Quick Fix:</strong> {error_suggestion}</div>', unsafe_allow_html=True)
            else:
                output_placeholder.markdown(f'<div class="output-area">{output}</div>', unsafe_allow_html=True)
    
    # Get AI help
    if debug_button or improve_button or explain_button:
        prompt_type = "debug" if debug_button else ("complete" if improve_button else "explain")
        
        with st.spinner(f"Getting {'debugging help' if debug_button else ('suggestions' if improve_button else 'explanation')}..."):
            suggestion = get_ai_suggestion(code, language, prompt_type)
            suggestion_placeholder.markdown(f'<div class="suggestion-area">{suggestion}</div>', unsafe_allow_html=True)
    
    # Generate flowchart
    if flowchart_button:
        with st.spinner("Generating code flowchart..."):
            graph, error = generate_code_flowchart(code, language)
            if error:
                flowchart_placeholder.error(error)
            elif graph:
                flowchart_placeholder.markdown('<div class="graph-container">', unsafe_allow_html=True)
                flowchart_placeholder.graphviz_chart(graph)
                flowchart_placeholder.markdown('</div>', unsafe_allow_html=True)

def dsa_challenges_page():
    st.header("🧩 DSA Vault Challenges Generator")
    st.write("Generate custom Data Structures & Algorithms challenges for interview preparation")
    
    # Initialize session state for challenge
    if "current_challenge" not in st.session_state:
        st.session_state.current_challenge = None
    
    if "challenge_code" not in st.session_state:
        st.session_state.challenge_code = ""
    
    # Settings for challenge generation
    st.subheader("Challenge Settings")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        language = st.selectbox("Programming Language", 
                               [lang for lang in SUPPORTED_LANGUAGES.keys() if SUPPORTED_LANGUAGES[lang]["compiler"] is not None],
                               key="dsa_lang")
    
    with col2:
        topic = st.selectbox("DSA Topic", ["Any"] + DSA_TOPICS, key="dsa_topic")
        
    with col3:
        difficulty = st.selectbox("Difficulty Level", DIFFICULTY_LEVELS, key="dsa_difficulty")
    
    col4, col5 = st.columns(2)
    with col4:
        company = st.selectbox("Company", ["Any"] + TECH_COMPANIES, key="dsa_company")
    
    with col5:
        generate_button = st.button("Generate Challenge", key="gen_challenge", use_container_width=True)
    
    # Generate challenge
    if generate_button:
        with st.spinner("Generating your custom DSA challenge..."):
            challenge = generate_dsa_challenge(
                topic if topic != "Any" else "any data structure or algorithm", 
                difficulty, 
                company, 
                language
            )
            
            if challenge:
                st.session_state.current_challenge = challenge
                st.session_state.challenge_code = challenge.get("starter_code", "# Write your solution here")
    
    # Display current challenge
    if st.session_state.current_challenge:
        challenge = st.session_state.current_challenge
        
        # Apply styling based on difficulty
        difficulty_class = f"difficulty-{challenge.get('difficulty', difficulty).lower()}"
        
        # Challenge header with title and metadata
        st.markdown(f"""
        <div class="challenge-container {difficulty_class}">
            <h3>{challenge.get('title', 'DSA Challenge')}</h3>
            <p><strong>Difficulty:</strong> {difficulty}</p>
            <p><strong>Topic:</strong> {topic if topic != "Any" else "Mixed"}</p>
            <p><strong>Company:</strong> {company if company != "Any" else "General"}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Render the description with markdown
        st.markdown("<h4>Problem Description</h4>", unsafe_allow_html=True)
        description = challenge.get('description', '')
        # Convert markdown to HTML for better rendering
        st.markdown(f'<div class="problem-description">{markdown(description)}</div>', unsafe_allow_html=True)
        
        # Constraints
        st.markdown("<h4>Constraints</h4>", unsafe_allow_html=True)
        constraints = challenge.get('constraints', '')
        st.markdown(f'<div class="problem-description">{markdown(constraints)}</div>', unsafe_allow_html=True)
        
        # Display examples
        st.markdown("<h4>Examples</h4>", unsafe_allow_html=True)
        examples = challenge.get('examples', [])
        for i, example in enumerate(examples):
            st.markdown(f"""
            <div class="problem-examples">
                <p><strong>Example {i+1}:</strong></p>
                <p><strong>Input:</strong> <code>{example.get('input', '')}</code></p>
                <p><strong>Output:</strong> <code>{example.get('output', '')}</code></p>
                <p><strong>Explanation:</strong> {example.get('explanation', '')}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Solution code editor
        st.subheader("Your Solution")
        code = st.text_area("Code Editor", st.session_state.challenge_code, 
                           height=300, key="dsa_code_editor")
        st.session_state.challenge_code = code
        
        # Action buttons for the DSA challenge
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            run_button = st.button("Run Code", key="dsa_run", use_container_width=True)
        with col2:
            debug_button = st.button("Debug", key="dsa_debug", use_container_width=True)
        with col3:
            hint_button = st.button("Get Hint", key="dsa_hint", use_container_width=True)
        with col4:
            solution_button = st.button("Show Solution", key="dsa_solution", use_container_width=True)
        with col5:
            similar_button = st.button("Similar Problems", key="dsa_similar", use_container_width=True)
        with col6:
            flowchart_button = st.button("Visualize Flow", key="dsa_flowchart", use_container_width=True)
        
        # Output area
        st.subheader("Output")
        output_placeholder = st.empty()
        
        # Hint/Solution/Similar area
        help_placeholder = st.empty()
        
        # Flowchart area
        flowchart_placeholder = st.empty()
        
        # Run code
        if run_button:
            with st.spinner("Running code..."):
                output, status = run_code(code, language)
                
                if status == "error":
                    output_placeholder.markdown(f'<div class="output-area error-message">{output}</div>', unsafe_allow_html=True)
                else:
                    output_placeholder.markdown(f'<div class="output-area">{output}</div>', unsafe_allow_html=True)
        
        # Debug code
        if debug_button:
            with st.spinner("Debugging your code..."):
                suggestion = get_ai_suggestion(code, language, "debug")
                help_placeholder.markdown(f'<div class="suggestion-area"><strong>🔍 Debug Analysis:</strong> {suggestion}</div>', unsafe_allow_html=True)
        
        # Get hint
        if hint_button:
            with st.spinner("Getting hint..."):
                # First try to use hints from the challenge
                if challenge.get("hints") and len(challenge.get("hints")) > 0:
                    hints = challenge.get("hints")
                    hint_index = st.session_state.get("hint_index", 0) % len(hints)
                    hint = hints[hint_index]
                    st.session_state.hint_index = hint_index + 1
                else:
                    # Generate a hint with LLM
                    hint_prompt = f"Provide a helpful hint for solving this DSA problem without giving away the complete solution:\n\n{challenge.get('description')}"
                    
                    chat_completion = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {"role": "system", "content": "You are a DSA tutor who provides helpful hints without revealing the full solution."},
                            {"role": "user", "content": hint_prompt}
                        ],
                        temperature=0.3,
                        max_tokens=150
                    )
                    
                    hint = chat_completion.choices[0].message.content
                
                help_placeholder.markdown(f'<div class="suggestion-area"><strong>💡 Hint:</strong> {hint}</div>', unsafe_allow_html=True)
        
        # Show solution
        if solution_button:
            with st.spinner("Generating optimal solution..."):
                solution_approach = challenge.get("solution_approach", "")
                
                # If no solution approach is provided, generate one with LLM
                if not solution_approach:
                    solution_prompt = f"Provide a detailed solution in {language} for this DSA problem with explanation:\n\n{challenge.get('description')}"
                    
                    chat_completion = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {"role": "system", "content": "You are an expert DSA coach providing optimal solutions with clear explanations."},
                            {"role": "user", "content": solution_prompt}
                        ],
                        temperature=0.3,
                        max_tokens=1024
                    )
                    
                    solution_approach = chat_completion.choices[0].message.content
                
                help_placeholder.markdown(f'<div class="suggestion-area"><strong>✅ Solution Approach:</strong> {solution_approach}</div>', unsafe_allow_html=True)
        
        # Find similar problems
        if similar_button:
            with st.spinner("Searching for similar problems..."):
                similar_problems = search_similar_problems(topic if topic != "Any" else challenge.get('title'), company)
                
                if isinstance(similar_problems, list):
                    similar_html = "<div class='suggestion-area'><strong>📚 Similar Problems:</strong><ul>"
                    for problem in similar_problems:
                        similar_html += f"<li><a href='{problem['link']}' target='_blank'>{problem['title']}</a> - {problem['snippet']}</li>"
                    similar_html += "</ul></div>"
                    help_placeholder.markdown(similar_html, unsafe_allow_html=True)
                else:
                    help_placeholder.markdown(f"<div class='suggestion-area error-message'>{similar_problems}</div>", unsafe_allow_html=True)
        
        # Generate flowchart
        if flowchart_button:
            with st.spinner("Generating solution flowchart..."):
                graph, error = generate_code_flowchart(code, language)
                if error:
                    flowchart_placeholder.error(error)
                elif graph:
                    flowchart_placeholder.markdown('<div class="graph-container">', unsafe_allow_html=True)
                    flowchart_placeholder.graphviz_chart(graph)
                    flowchart_placeholder.markdown('</div>', unsafe_allow_html=True)

def about_page():
    st.header("About CodeBuddy")
    
    st.markdown("""
    ## 👋 Welcome to CodeBuddy!
    
    **CodeBuddy** is your AI-powered coding companion designed to help you:
    
    - Write, run, and debug code in multiple programming languages
    - Generate custom DSA (Data Structures and Algorithms) challenges for interview preparation
    - Get intelligent code suggestions and improvements
    - Visualize code flow with interactive flowcharts
    - Compare your solutions with optimal approaches
    
    ### 🔧 Features
    
    - **Interactive Code Editor**: Write and run code in Python, JavaScript, Java, and C++
    - **Intelligent Debugging**: Get AI-powered insights on your code errors
    - **DSA Challenge Generator**: Practice with custom-generated challenges tailored to your needs
    - **Code Visualization**: See your algorithms as flowcharts to better understand logic flow
    - **Similar Problem Search**: Find related coding problems across the web
    
    ### 🚀 How to Use
    
    1. Navigate between the **Code Editor** and **DSA Challenges** using the sidebar
    2. Write your code or generate a challenge
    3. Use the action buttons to run, debug, improve, or visualize your code
    4. Get AI-powered help when you're stuck
    
    ### 💻 Supported Languages
    
    - Python
    - JavaScript
    - Java
    - C++
    - HTML/CSS (preview not available)
    - SQL (preview not available)
    
    ### 📊 DSA Topics
    
    Practice with challenges covering a wide range of topics including Arrays, Linked Lists, Trees, 
    Graphs, Dynamic Programming, and many more!
    
    ### 🛠️ Technical Details
    
    CodeBuddy is built with:
    - Streamlit for the web interface
    - Groq LLM API for AI code assistance
    - Pygments for code syntax highlighting
    - Graphviz for code flow visualization
    - Google Serper API for similar problem search
    
    ### 📝 Feedback
    
    We're constantly improving CodeBuddy! If you have suggestions or encounter any issues, 
    please let us know by opening an issue on our GitHub repository.
    
    ---
    
    Happy coding! 👨‍💻
    """)

if __name__ == "__main__":
    main()