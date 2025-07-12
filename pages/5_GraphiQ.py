import streamlit as st
import os
import json
import re
import requests
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import time
from datetime import datetime
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr
import streamlit.components.v1 as components
from groq import Groq
import random

# Initialize Groq client
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Initialize Serper API
SERPER_API_KEY = os.environ.get("SERPER_API_KEY")

# Page configuration
st.set_page_config(
    page_title="Math Learning Assistant",
    page_icon="🧮",
    layout="wide",
)

# Custom CSS for better UI
st.markdown("""
<style>
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.8rem;
        margin-bottom: 1rem;
        display: flex;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .chat-message.user {
        background-color: #e6f3ff;
        border-left: 5px solid #2970ff;
    }
    .chat-message.assistant {
        background-color: #f0f0f0;
        border-left: 5px solid #6c757d;
    }
    .chat-message .avatar {
        width: 50px;
        height: 50px;
        border-radius: 50%;
        object-fit: cover;
        margin-right: 1rem;
    }
    .chat-message .content {
        width: 90%;
    }
    .desmos-calculator {
        width: 100%;
        height: 500px;
        border: 1px solid #ddd;
        border-radius: 8px;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
    .reference-card {
        background-color: #f9f9f9;
        border-left: 3px solid #28a745;
        padding: 10px;
        margin: 10px 0;
        border-radius: 5px;
    }
    .visualization-options {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 15px;
    }
    /* Modern chat UI styles */
    .chat-container {
        display: flex;
        flex-direction: column;
        height: 70vh;
        overflow-y: auto;
        padding: 10px;
        background-color: #f9f9f9;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .chat-input-area {
        display: flex;
        margin-top: 10px;
    }
    .chat-input {
        flex-grow: 1;
        padding: 10px;
        border-radius: 20px;
        border: 1px solid #ddd;
        margin-right: 10px;
    }
    .send-button {
        background-color: #4CAF50;
        color: white;
        border: none;
        border-radius: 20px;
        padding: 10px 20px;
        cursor: pointer;
    }
    .user-message {
        align-self: flex-end;
        background-color: #DCF8C6;
        color: black;
        padding: 10px 15px;
        border-radius: 18px;
        margin: 5px 0;
        max-width: 70%;
    }
    .bot-message {
        align-self: flex-start;
        background-color: white;
        color: black;
        padding: 10px 15px;
        border-radius: 18px;
        margin: 5px 0;
        max-width: 70%;
    }
    .sidebar-content {
        padding: 15px;
    }
    .chat-options {
        background-color: #f0f0f0;
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for chat management
if 'chats' not in st.session_state:
    st.session_state.chats = {
        "New Chat": []
    }

if 'current_chat' not in st.session_state:
    st.session_state.current_chat = "New Chat"

if 'chat_counter' not in st.session_state:
    st.session_state.chat_counter = 1

if 'current_expression' not in st.session_state:
    st.session_state.current_expression = ""

if 'web_search_enabled' not in st.session_state:
    st.session_state.web_search_enabled = True

if 'search_results' not in st.session_state:
    st.session_state.search_results = []

if 'visualization_type' not in st.session_state:
    st.session_state.visualization_type = "Desmos"

# Function to perform web search using Serper API
def search_web(query):
    if not st.session_state.web_search_enabled:
        return {"organic": []}
    
    try:
        url = "https://google.serper.dev/search"
        payload = json.dumps({
            "q": query,
            "num": 3
        })
        headers = {
            'X-API-KEY': SERPER_API_KEY,
            'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        return response.json()
    except Exception as e:
        st.error(f"Error searching the web: {e}")
        return {"organic": []}

# Function to extract mathematical expressions from text
def extract_math_expressions(text):
    # Match expressions between $ signs for inline math
    inline_pattern = r'\$(.*?)\$'
    # Match expressions between $$ signs for block math
    block_pattern = r'\$\$(.*?)\$\$'
    
    inline_matches = re.findall(inline_pattern, text)
    block_matches = re.findall(block_pattern, text)
    
    # Combine all matches
    all_matches = inline_matches + block_matches
    
    # Try to find functions with y= or f(x)= patterns
    function_pattern = r'(?:y|f\(x\))\s*=\s*(.*?)(?:\n|$)'
    function_matches = re.findall(function_pattern, text)
    
    all_matches.extend(function_matches)
    
    return all_matches

# Function to generate a Desmos graph from an expression
def get_desmos_calculator(expression=""):
    desmos_html = f"""
    <div class="desmos-calculator">
        <script src="https://www.desmos.com/api/v1.7/calculator.js?apiKey=dcb31709b452b1cf9dc26972add0fda6"></script>
        <div id="calculator" style="width: 100%; height: 500px;"></div>
        <script>
            var elt = document.getElementById('calculator');
            var calculator = Desmos.GraphingCalculator(elt);
            calculator.setExpression({{ id: 'graph1', latex: '{expression}' }});
        </script>
    </div>
    """
    return desmos_html

# Function to create a plotly visualization
def create_visualization(expression, x_range=(-10, 10), points=1000, viz_type="2D"):
    try:
        # Parse the expression with sympy
        x = sp.Symbol('x')
        parsed_expr = parse_expr(expression.replace("^", "**"))
        
        # Create x values
        x_vals = np.linspace(x_range[0], x_range[1], points)
        
        # Calculate y values
        f = sp.lambdify(x, parsed_expr, "numpy")
        y_vals = [f(x_val) for x_val in x_vals]
        
        # Create the plot
        if viz_type == "2D":
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=x_vals, y=y_vals, mode='lines', name=expression))
            fig.update_layout(
                title=f"Graph of {expression}",
                xaxis_title="x",
                yaxis_title="y",
                height=500,
            )
            return fig
        elif viz_type == "3D":
            # Create a meshgrid for 3D visualization
            y = sp.Symbol('y')
            try:
                # For 3D, we need to convert the expression to use both x and y
                # This is a simplistic approach - replace x with sqrt(x^2+y^2) to create a surface of revolution
                expr_3d = parsed_expr.subs(x, sp.sqrt(x**2 + y**2))
                f_3d = sp.lambdify((x, y), expr_3d, "numpy")
                
                X, Y = np.meshgrid(x_vals, x_vals)
                Z = np.zeros_like(X)
                
                for i in range(len(x_vals)):
                    for j in range(len(x_vals)):
                        try:
                            Z[i, j] = f_3d(X[i, j], Y[i, j])
                        except:
                            Z[i, j] = np.nan
                
                fig = go.Figure(data=[go.Surface(z=Z, x=X, y=Y)])
                fig.update_layout(
                    title=f'3D Surface from {expression}',
                    scene=dict(
                        xaxis_title='X',
                        yaxis_title='Y',
                        zaxis_title='Z'
                    ),
                    height=700
                )
                return fig
            except Exception as e:
                st.warning(f"Could not create 3D visualization: {e}")
                return None
        elif viz_type == "Contour":
            # Create a contour plot
            y = sp.Symbol('y')
            try:
                # Try to adapt the expression for contour plotting
                expr_contour = parsed_expr.subs(x, sp.sqrt(x**2 + y**2))
                f_contour = sp.lambdify((x, y), expr_contour, "numpy")
                
                X, Y = np.meshgrid(x_vals, x_vals)
                Z = np.zeros_like(X)
                
                for i in range(len(x_vals)):
                    for j in range(len(x_vals)):
                        try:
                            Z[i, j] = f_contour(X[i, j], Y[i, j])
                        except:
                            Z[i, j] = np.nan
                
                fig = go.Figure(data=[go.Contour(z=Z, x=x_vals, y=x_vals)])
                fig.update_layout(
                    title=f'Contour Plot of {expression}',
                    xaxis_title='X',
                    yaxis_title='Y',
                    height=500
                )
                return fig
            except Exception as e:
                st.warning(f"Could not create contour visualization: {e}")
                return None
        else:
            return None
    except Exception as e:
        st.warning(f"Error creating visualization: {e}")
        return None

# Function to evaluate mathematical expressions
def evaluate_expression(expr_str):
    try:
        x = sp.Symbol('x')
        expr = parse_expr(expr_str.replace("^", "**"))
        return expr
    except:
        return None

# Function to get a response from Groq API
def get_groq_response(messages):
    try:
        response = groq_client.chat.completions.create(
            messages=messages,
            model="llama3-70b-8192",
            temperature=0.5,
            max_tokens=1024
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error getting response from Groq: {e}")
        return f"I'm having trouble connecting to my knowledge source. Please try again. Error: {str(e)}"

# Function to process the user message
def process_message(user_message):
    # Add user message to history
    if st.session_state.current_chat not in st.session_state.chats:
        st.session_state.chats[st.session_state.current_chat] = []
    
    st.session_state.chats[st.session_state.current_chat].append({"role": "user", "content": user_message})
    
    # Search the web for relevant information
    search_results = search_web(f"math {user_message}")
    st.session_state.search_results = search_results.get("organic", [])[:3]
    
    # Prepare messages for LLM
    context_messages = [
        {"role": "system", "content": """You are a helpful and knowledgeable math learning assistant. 
        Your goal is to help students understand mathematical concepts through clear explanations, examples, and visualizations.
        Include LaTeX formulas where appropriate using $ for inline math and $$ for block equations.
        Make sure to explain step by step and provide intuitive explanations.
        If suitable, suggest graphs or visualizations that could help understand the concept better.
        Always be encouraging and supportive."""}
    ]
    
    # Add web search context
    web_context = ""
    if st.session_state.search_results and st.session_state.web_search_enabled:
        web_context = "Here's some information I found that might help:\n\n"
        for idx, result in enumerate(st.session_state.search_results):
            web_context += f"Source {idx+1}: {result.get('title', 'Unknown')}\n"
            web_context += f"Summary: {result.get('snippet', 'No snippet available')}\n\n"
    
    if web_context:
        context_messages.append({"role": "user", "content": f"Please use this context to help answer the question: {web_context}"})
    
    # Add past messages for context (limiting to last 10 exchanges)
    current_chat_messages = st.session_state.chats[st.session_state.current_chat]
    for msg in current_chat_messages[-10:]:
        context_messages.append(msg)
    
    # Get response from LLM
    assistant_response = get_groq_response(context_messages)
    
    # Extract mathematical expressions
    expressions = extract_math_expressions(assistant_response)
    if expressions:
        st.session_state.current_expression = expressions[0]
    
    # Add assistant response to history
    st.session_state.chats[st.session_state.current_chat].append({"role": "assistant", "content": assistant_response})
    
    return assistant_response, expressions

# Function to create a new chat
def create_new_chat():
    chat_name = f"Chat {st.session_state.chat_counter}"
    st.session_state.chats[chat_name] = []
    st.session_state.current_chat = chat_name
    st.session_state.chat_counter += 1

# Function to delete the current chat
def delete_current_chat():
    if st.session_state.current_chat != "New Chat":
        del st.session_state.chats[st.session_state.current_chat]
        st.session_state.current_chat = "New Chat"

# Sidebar
with st.sidebar:
    st.image("https://api.dicebear.com/7.x/bottts/svg?seed=math-bot", width=100)
    st.title("GraphiQ - Math Learning Assistant")
    
    # Chat management options
    st.subheader("Chat Options")
    if st.button("➕ New Chat"):
        create_new_chat()
    
    # Display available chats
    st.subheader("Your Chats")
    for chat_name in st.session_state.chats.keys():
        if st.sidebar.button(chat_name, key=f"chat_{chat_name}"):
            st.session_state.current_chat = chat_name
    
    # Delete current chat
    if st.session_state.current_chat != "New Chat" and st.button("🗑️ Delete Current Chat"):
        delete_current_chat()
    
    # Web search toggle
    st.subheader("Settings")
    st.session_state.web_search_enabled = st.toggle("Enable Web Search", value=st.session_state.web_search_enabled)
    
    # Visualization options
    st.subheader("Visualization Options")
    st.session_state.visualization_type = st.selectbox(
        "Default Visualization", 
        ["Desmos", "Plotly 2D", "Plotly 3D", "Contour Plot"],
        index=0
    )
    
    # Help section
    with st.expander("How to Use"):
        st.markdown("""
        1. **Ask Questions**: Type any math question in the chat box
        2. **Visualize**: The system will automatically detect and visualize equations
        3. **Chat Management**: Create new chats for different topics
        4. **Web Search**: Toggle on/off web search for additional context
        5. **Multiple Visualizations**: Choose different visualization types
        """)
    
    # Clear chat button
    if st.button("Clear Current Chat"):
        st.session_state.chats[st.session_state.current_chat] = []
        st.session_state.current_expression = ""
        st.session_state.search_results = []
        st.rerun()

# Main area - Combined chat and visualization
st.header(f"Math Learning Assistant - {st.session_state.current_chat}")

# Display chat messages
if st.session_state.current_chat in st.session_state.chats:
    for message in st.session_state.chats[st.session_state.current_chat]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # If this is a bot message, check for expressions and add visualization button
            if message["role"] == "assistant":
                expressions = extract_math_expressions(message["content"])
                if expressions:
                    with st.expander("Visualize Expressions", expanded=False):
                        selected_expr = st.selectbox(
                            "Select expression to visualize:", 
                            options=expressions,
                            key=f"expr_select_{hash(message['content'])}"
                        )
                        
                        if st.button("Visualize", key=f"viz_{hash(message['content'])}"):
                            st.session_state.current_expression = selected_expr
                            st.rerun()

# Web search results display
if st.session_state.search_results and st.session_state.web_search_enabled:
    with st.expander("View Related Resources", expanded=False):
        for idx, result in enumerate(st.session_state.search_results):
            st.markdown(f"""
            <div class="reference-card">
                <strong>{result.get('title', 'Unknown')}</strong><br>
                {result.get('snippet', 'No information available')}<br>
                <a href="{result.get('link', '#')}" target="_blank">Read more</a>
            </div>
            """, unsafe_allow_html=True)

# Visualization section
if st.session_state.current_expression:
    st.subheader("Mathematical Visualization")
    
    # Options for visualization
    with st.expander("Visualization Settings", expanded=True):
        col1, col2, col3 = st.columns([3, 2, 1])
        
        with col1:
            manual_expression = st.text_input(
                "Mathematical expression:", 
                value=st.session_state.current_expression
            )
        
        with col2:
            x_range = st.slider(
                "X Range", 
                min_value=-20, 
                max_value=20, 
                value=(-10, 10),
                step=1
            )
        
        with col3:
            if st.button("Update Plot"):
                st.session_state.current_expression = manual_expression
    
    # Visualization tabs
    viz_tab1, viz_tab2, viz_tab3, viz_tab4 = st.tabs(["Desmos", "2D Plot", "3D Plot", "Contour Plot"])
    
    with viz_tab1:
        # Desmos calculator
        st.subheader("Interactive Desmos Graph")
        components.html(
            get_desmos_calculator(st.session_state.current_expression),
            height=550
        )
    
    with viz_tab2:
        # Plotly 2D visualization
        try:
            fig_2d = create_visualization(st.session_state.current_expression, x_range=x_range, viz_type="2D")
            if fig_2d:
                st.plotly_chart(fig_2d, use_container_width=True)
            else:
                st.warning("Unable to create 2D visualization for this expression.")
        except Exception as e:
            st.error(f"Error creating 2D visualization: {e}")
    
    with viz_tab3:
        # 3D visualization
        try:
            fig_3d = create_visualization(st.session_state.current_expression, x_range=x_range, viz_type="3D")
            if fig_3d:
                st.plotly_chart(fig_3d, use_container_width=True)
            else:
                st.warning("Unable to create 3D visualization for this expression.")
        except Exception as e:
            st.error(f"Error creating 3D visualization: {e}")
    
    with viz_tab4:
        # Contour plot
        try:
            fig_contour = create_visualization(st.session_state.current_expression, x_range=x_range, viz_type="Contour")
            if fig_contour:
                st.plotly_chart(fig_contour, use_container_width=True)
            else:
                st.warning("Unable to create contour visualization for this expression.")
        except Exception as e:
            st.error(f"Error creating contour visualization: {e}")
    
    # Expression analysis
    with st.expander("Expression Analysis", expanded=False):
        try:
            # Evaluate the expression
            expr = evaluate_expression(st.session_state.current_expression)
            if expr:
                st.write("Simplified form:", sp.simplify(expr))
                
                # Derivative
                x = sp.Symbol('x')
                derivative = sp.diff(expr, x)
                st.write("Derivative:", derivative)
                
                # Find critical points
                critical_points = sp.solve(derivative, x)
                if critical_points:
                    st.write("Critical points:", critical_points)
                else:
                    st.write("No critical points found.")
                
                # Integral
                integral = sp.integrate(expr, x)
                st.write("Indefinite integral:", integral)
        except Exception as e:
            st.error(f"Error analyzing expression: {e}")

# Chat input
prompt = st.chat_input("Ask me any math question...")
if prompt:
    response, expressions = process_message(prompt)
    
    # Handle the current expression for visualization
    if expressions and not st.session_state.current_expression:
        st.session_state.current_expression = expressions[0]
    
    st.rerun()