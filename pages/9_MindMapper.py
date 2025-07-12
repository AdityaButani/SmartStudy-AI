import os
import streamlit as st
import google.generativeai as genai
import pytube
import fitz  # PyMuPDF
import requests
import re
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network
import tempfile
import base64
from streamlit_extras.switch_page_button import switch_page
import json
from PIL import Image
from io import BytesIO
import time
import random

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Set page configuration
st.set_page_config(
    page_title="MindMap Generator",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom CSS for modern, clean UI
st.markdown("""
<style>
    /* Main background and text colors */
    .main {
        background-color: #f0f4f8;
        color: #1e293b;
    }
    
    /* Header styling */
    h1 {
        color: #2563eb;
        font-family: 'Poppins', 'Segoe UI', Tahoma, Geneva, sans-serif;
        font-weight: 700;
        margin-top: 0.5rem;
        margin-bottom: 1.2rem;
        padding-bottom: 0.7rem;
        border-bottom: 3px solid #2563eb;
    }
    
    h2, h3 {
        color: #1e40af;
        font-family: 'Poppins', 'Segoe UI', Tahoma, Geneva, sans-serif;
        font-weight: 600;
        margin-top: 1.2rem;
    }
    
    /* Button styling */
    .stButton button {
        background-color: #2563eb;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.7rem 1.5rem;
        font-weight: 600;
        box-shadow: 0 4px 6px rgba(37, 99, 235, 0.25);
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        background-color: #1d4ed8;
        box-shadow: 0 6px 10px rgba(37, 99, 235, 0.3);
        transform: translateY(-2px);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #e2e8f0;
        border-radius: 8px 8px 0 0;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #2563eb !important;
        color: white !important;
    }
    
    /* Cards for different sections */
    .card {
        background-color: white;
        border-radius: 12px;
        padding: 1.8rem;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        margin-bottom: 1.5rem;
        border-top: 5px solid #2563eb;
    }
    
    /* Input fields */
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 1px solid #cbd5e1;
        padding: 0.8rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }
    
    .stTextArea > div > div > textarea {
        border-radius: 8px;
        border: 1px solid #cbd5e1;
        padding: 0.8rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }
    
    /* File uploader */
    .stFileUploader > div > button {
        background-color: #f1f5f9;
        border: 2px dashed #2563eb;
        border-radius: 8px;
        color: #2563eb;
        transition: all 0.3s ease;
    }
    
    .stFileUploader > div > button:hover {
        background-color: #e2e8f0;
    }
    
    /* Tips section */
    .tip-box {
        background-color: #f8fafc;
        border-left: 5px solid #2563eb;
        padding: 1.2rem;
        border-radius: 0 8px 8px 0;
        margin-bottom: 0.8rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }
    
    /* Download button */
    .download-btn {
        display: inline-block;
        background-color: #2563eb;
        color: white;
        text-decoration: none;
        padding: 0.7rem 1.5rem;
        border-radius: 8px;
        font-weight: 600;
        margin-top: 1.2rem;
        box-shadow: 0 4px 6px rgba(37, 99, 235, 0.25);
        transition: all 0.3s ease;
    }
    
    .download-btn:hover {
        background-color: #1d4ed8;
        box-shadow: 0 6px 10px rgba(37, 99, 235, 0.3);
        transform: translateY(-2px);
    }
    
    /* Success message */
    .success-msg {
        background-color: #dcfce7;
        color: #166534;
        padding: 1.2rem;
        border-radius: 8px;
        border-left: 5px solid #22c55e;
        margin: 1.2rem 0;
        display: flex;
        align-items: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    }
    
    .success-msg::before {
        content: "✓";
        background-color: #22c55e;
        color: white;
        width: 24px;
        height: 24px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        margin-right: 10px;
        font-weight: bold;
    }
    
    /* Progress bar */
    .stProgress > div > div > div {
        background-color: #2563eb;
    }
    
    /* Footer */
    .footer {
        margin-top: 2.5rem;
        padding-top: 1.5rem;
        border-top: 1px solid #cbd5e1;
        text-align: center;
        font-size: 0.9rem;
        color: #64748b;
    }
    
    /* Animation */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .animate-fade-in {
        animation: fadeIn 0.5s ease-out forwards;
    }
    
    /* Color schemes for nodes */
    .color-scheme-info {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin: 15px 0;
    }
    
    .color-item {
        display: flex;
        align-items: center;
        margin-right: 15px;
    }
    
    .color-dot {
        width: 15px;
        height: 15px;
        border-radius: 50%;
        margin-right: 5px;
    }
</style>
""", unsafe_allow_html=True)

# App Header with Logo
col1, col2 = st.columns([1, 5])
with col1:
    # Create a brain logo with animation
    st.markdown("""
    <div style="font-size: 4rem; color: #2563eb; text-align: center; animation: pulse 2s infinite alternate;">
        🧠
    </div>
    <style>
    @keyframes pulse {
        0% { transform: scale(1); }
        100% { transform: scale(1.1); }
    }
    </style>
    """, unsafe_allow_html=True)
with col2:
    st.title("Intelligent Mind Map Generator")
    st.markdown("""
    <p style="font-size: 1.2rem; color: #475569; margin-top: -0.5rem;">
        Transform complex content into beautiful, interactive knowledge visualizations
    </p>
    """, unsafe_allow_html=True)

# Initialize the Gemini model
@st.cache_resource
def get_model():
    return genai.GenerativeModel('gemini-1.5-pro')

model = get_model()

def extract_text_from_youtube(youtube_url):
    """Extract transcript from a YouTube video"""
    try:
        with st.spinner("Extracting YouTube transcript..."):
            # Get YouTube video
            video = pytube.YouTube(youtube_url)
            video_id = video.video_id
            
            # Get transcript using YouTube transcript API
            from youtube_transcript_api import YouTubeTranscriptApi
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            transcript = " ".join([t["text"] for t in transcript_list])
            
            # Get video title and basic info
            title = video.title
            author = video.author
            length = video.length
            views = video.views
            
            # Format video metadata
            metadata = f"Title: {title}\nAuthor: {author}\nLength: {length} seconds\nViews: {views}\n\n"
            
            return f"{metadata}\nTranscript:\n{transcript}"
    except Exception as e:
        st.error(f"Error extracting YouTube transcript: {str(e)}")
        return None

def extract_text_from_pdf(pdf_file):
    """Extract text from a PDF file"""
    try:
        with st.spinner("Extracting text from PDF..."):
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(pdf_file.getvalue())
                tmp_file_path = tmp_file.name
            
            # Extract text from PDF
            doc = fitz.open(tmp_file_path)
            
            # Get PDF metadata
            metadata = f"Title: {doc.metadata.get('title', 'Unknown')}\n"
            metadata += f"Author: {doc.metadata.get('author', 'Unknown')}\n"
            metadata += f"Subject: {doc.metadata.get('subject', 'Unknown')}\n"
            metadata += f"Total Pages: {len(doc)}\n\n"
            
            text = metadata
            
            # Extract text with page numbers
            for i, page in enumerate(doc):
                page_text = page.get_text()
                if page_text.strip():  # Only add non-empty pages
                    text += f"Page {i+1}:\n{page_text}\n\n"
            
            # Clean up temporary file
            os.unlink(tmp_file_path)
            
            return text
    except Exception as e:
        st.error(f"Error extracting PDF text: {str(e)}")
        return None

def extract_text_from_url(url):
    """Extract text from a webpage"""
    try:
        with st.spinner("Extracting content from URL..."):
            response = requests.get(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract title and metadata
            title = soup.title.string if soup.title else "Webpage Content"
            
            # Try to get meta description
            description = ""
            desc_tag = soup.find("meta", {"name": "description"}) or soup.find("meta", {"property": "og:description"})
            if desc_tag and desc_tag.get("content"):
                description = desc_tag["content"]
                
            # Extract author if available
            author = ""
            author_tag = soup.find("meta", {"name": "author"}) or soup.find("meta", {"property": "article:author"})
            if author_tag and author_tag.get("content"):
                author = author_tag["content"]
                
            metadata = f"Title: {title}\n"
            if description:
                metadata += f"Description: {description}\n"
            if author:
                metadata += f"Author: {author}\n"
            metadata += f"URL: {url}\n\n"
            
            # Remove script, style elements and navigation elements
            for element in soup(["script", "style", "nav", "footer", "header", "aside", "noscript", 
                                "iframe", "svg", "form", "input", "button", "meta", "link"]):
                element.extract()
            
            # Try to extract main content
            main_content = None
            for tag in ["main", "article", "div.content", "div.main", "div.article"]:
                main_content = soup.select_one(tag)
                if main_content:
                    break
            
            # If no main content found, use body
            if not main_content:
                main_content = soup.body
            
            # Get text from main content
            text = main_content.get_text() if main_content else soup.get_text()
            
            # Break into lines and remove leading and trailing space on each
            lines = (line.strip() for line in text.splitlines())
            
            # Break multi-headlines into a line each
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            
            # Drop blank lines and join
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            return f"{metadata}{text}"
    except Exception as e:
        st.error(f"Error extracting URL text: {str(e)}")
        return None

def generate_mindmap_json(text, theme_option="standard", complexity="standard"):
    """Generate a mindmap from text using Gemini API"""
    if not text:
        return None
    
    # Adjust complexity settings
    complexity_settings = {
        "simple": {
            "max_levels": 3,
            "max_subtopics": 5,
            "max_details": 3
        },
        "standard": {
            "max_levels": 4,
            "max_subtopics": 7,
            "max_details": 5
        },
        "detailed": {
            "max_levels": 5,
            "max_subtopics": 8,
            "max_details": 6
        }
    }
    
    settings = complexity_settings[complexity]
    
    prompt = f"""
    Analyze the following content and create a detailed hierarchical mind map structure in JSON format.
    
    The JSON should have the following structure:
    {{
        "central_topic": "Main Topic",
        "theme": "{theme_option}",
        "metadata": {{
            "source_type": "article/video/pdf/webpage",
            "estimated_reading_time": "X minutes",
            "key_takeaway": "Brief summary of main idea"
        }},
        "children": [
            {{
                "name": "Subtopic 1",
                "importance": "high/medium/low",
                "children": [
                    {{ 
                        "name": "Detail 1",
                        "importance": "high/medium/low",
                        "children": [
                            {{ 
                                "name": "Sub-detail 1",
                                "importance": "high/medium/low"
                            }},
                            {{ 
                                "name": "Sub-detail 2",
                                "importance": "high/medium/low" 
                            }}
                        ]
                    }},
                    {{ 
                        "name": "Detail 2",
                        "importance": "high/medium/low" 
                    }}
                ]
            }},
            {{
                "name": "Subtopic 2",
                "importance": "high/medium/low",
                "children": []
            }}
        ]
    }}
    
    Guidelines:
    1. Create a comprehensive mind map with up to {settings['max_levels']} levels of hierarchy for optimal detail.
    2. For each node, use concise yet informative phrases (max 50 characters).
    3. Include {settings['max_subtopics']} main subtopics that represent the content's core themes.
    4. For each subtopic, include up to {settings['max_details']} key details or supporting points.
    5. Mark node importance as "high" for critical concepts, "medium" for supporting concepts, "low" for minor details.
    6. Group related concepts together under appropriate parent nodes.
    7. Use parallel structure in node naming (e.g., all actions as verbs, all concepts as nouns).
    8. Ensure the central topic accurately represents the content's main subject.
    9. Include examples, applications, or specific cases where appropriate.
    10. Identify relationships and connections between different concepts.
    11. Add counter-arguments or limitations to show balanced perspective if present in the content.
    12. Focus on hierarchical organization rather than chronological sequence.
    
    Content for analysis:
    {text[:25000]}  # Taking first 25000 characters to stay within token limits
    
    Output only valid JSON, no explanation or other text.
    """
    
    try:
        progress_placeholder = st.empty()
        progress_bar = progress_placeholder.progress(0)
        
        # Simulate progress
        for i in range(5):
            progress_bar.progress((i+1) * 10)
            time.sleep(0.1)
            
        with st.spinner("AI is analyzing your content..."):
            # Update progress bar
            for i in range(5, 9):
                progress_bar.progress((i+1) * 10)
                time.sleep(0.3)
                
            response = model.generate_content(prompt)
            response_text = response.text
            
            # Complete progress bar
            progress_bar.progress(100)
            time.sleep(0.2)
            progress_placeholder.empty()
            
            # Extract JSON from the response if it's wrapped in code blocks
            if "```json" in response_text:
                json_match = re.search(r'```json\n(.*?)\n```', response_text, re.DOTALL)
                if json_match:
                    response_text = json_match.group(1)
            elif "```" in response_text:
                json_match = re.search(r'```\n(.*?)\n```', response_text, re.DOTALL)
                if json_match:
                    response_text = json_match.group(1)
            
            # Parse and return JSON
            mindmap_data = json.loads(response_text)
            
            # Add theme info if not present
            if "theme" not in mindmap_data:
                mindmap_data["theme"] = theme_option
                
            return mindmap_data
    except Exception as e:
        st.error(f"Error generating mind map: {str(e)}")
        st.error("Response from AI might not be in valid JSON format.")
        return None

def create_pyvis_network(mindmap_data):
    """Create a PyVis network from mindmap data"""
    with st.spinner("Creating your mind map visualization..."):
        # Progress bar for visualization
        progress_placeholder = st.empty()
        progress_bar = progress_placeholder.progress(0)
        
        # Create a PyVis network
        net = Network(height="750px", width="100%", bgcolor="#ffffff", font_color="black", directed=False)
        
        # Set up theme colors
        themes = {
            "standard": {
                "central": "#2563eb",  # Blue
                "level1": ["#1e40af", "#3b82f6", "#60a5fa"],  # Blues
                "level2": ["#0e7490", "#06b6d4", "#22d3ee"],  # Teals
                "level3": ["#4338ca", "#6366f1", "#818cf8"],  # Indigos
                "level4": ["#a21caf", "#c026d3", "#d946ef"],  # Purples
            },
            "nature": {
                "central": "#047857",  # Green
                "level1": ["#065f46", "#059669", "#10b981"],  # Greens
                "level2": ["#166534", "#22c55e", "#4ade80"],  # Light Greens
                "level3": ["#3f6212", "#65a30d", "#a3e635"],  # Limes
                "level4": ["#854d0e", "#d97706", "#f59e0b"],  # Ambers
            },
            "creative": {
                "central": "#7c3aed",  # Violet
                "level1": ["#6d28d9", "#8b5cf6", "#a78bfa"],  # Purples
                "level2": ["#be185d", "#ec4899", "#f472b6"],  # Pinks
                "level3": ["#0369a1", "#0ea5e9", "#38bdf8"],  # Blues
                "level4": ["#b45309", "#f59e0b", "#fbbf24"],  # Ambers
            },
            "professional": {
                "central": "#1e293b",  # Slate
                "level1": ["#334155", "#475569", "#64748b"],  # Slates
                "level2": ["#0f172a", "#1e293b", "#334155"],  # Dark Slates
                "level3": ["#374151", "#4b5563", "#6b7280"],  # Grays
                "level4": ["#1f2937", "#374151", "#4b5563"],  # Dark Grays
            },
            "vibrant": {
                "central": "#db2777",  # Pink
                "level1": ["#9d174d", "#ec4899", "#f472b6"],  # Pinks
                "level2": ["#7c2d12", "#ea580c", "#fb923c"],  # Oranges
                "level3": ["#b45309", "#f59e0b", "#fbbf24"],  # Ambers
                "level4": ["#4d7c0f", "#84cc16", "#bef264"],  # Limes
            }
        }
        
        # If theme is specified in mindmap data, use it; otherwise use standard
        theme_name = mindmap_data.get("theme", "standard")
        if theme_name not in themes:
            theme_name = "standard"
            
        theme = themes[theme_name]
        
        # Update progress
        progress_bar.progress(20)
        
        # Add central node
        central_topic = mindmap_data["central_topic"]
        net.add_node(0, label=central_topic, color=theme["central"], shape="ellipse", size=45, 
                    font={"size": 24, "face": "Arial", "color": "white"}, 
                    shadow=True, title=central_topic)
        
        node_counter = 1
        
        # Add child nodes using recursive function
        def add_children(parent_id, children, level=1):
            nonlocal node_counter
            
            # Define sizes based on level
            sizes = [35, 30, 25, 20, 15]
            
            # Get colors for this level
            level_colors = theme[f"level{min(level, 4)}"]
            
            for child in children:
                current_id = node_counter
                node_counter += 1
                
                # Determine color based on importance if available
                importance = child.get("importance", "medium")
                color_index = {"high": 0, "medium": 1, "low": 2}.get(importance, 1)
                color = level_colors[min(color_index, len(level_colors)-1)]
                
                # Determine size based on level and importance
                importance_multiplier = {"high": 1.2, "medium": 1.0, "low": 0.8}.get(importance, 1.0)
                size = sizes[min(level-1, len(sizes)-1)] * importance_multiplier
                
                # Text color - white for darker backgrounds, black for lighter
                # Determine if color is dark (crude approximation)
                is_dark = color.lstrip('#')[0] in "0123456789ab"
                text_color = "white" if is_dark else "black"
                
                # Add node
                net.add_node(current_id, label=child["name"], color=color, shape="ellipse", 
                            size=size, font={"size": max(16 - (level*1.5), 11), "color": text_color},
                            shadow=True, title=child["name"])
                
                # Add edge with varying width based on importance
                edge_width = {"high": 3, "medium": 2, "low": 1}.get(importance, 2)
                smooth_type = "dynamic" if level % 2 == 0 else "curvedCW"
                smooth_roundness = 0.2 if level < 3 else 0.15
                
                net.add_edge(parent_id, current_id, color="#a0a0a0", width=edge_width, 
                           smooth={"type": smooth_type, "roundness": smooth_roundness})
                
                # Process children if they exist
                if "children" in child and child["children"] and level < 5:
                    add_children(current_id, child["children"], level+1)
        
        # Update progress
        progress_bar.progress(40)
        
        if "children" in mindmap_data:
            add_children(0, mindmap_data["children"])
        
        # Update progress
        progress_bar.progress(70)
        
        # Set physics options for better layout
        net.set_options("""
        {
            "physics": {
                "forceAtlas2Based": {
                    "gravitationalConstant": -80,
                    "centralGravity": 0.015,
                    "springLength": 150,
                    "springConstant": 0.05,
                    "avoidOverlap": 0.8
                },
                "maxVelocity": 50,
                "minVelocity": 0.1,
                "solver": "forceAtlas2Based",
                "stabilization": {
                    "enabled": true,
                    "iterations": 1500,
                    "updateInterval": 50
                }
            },
            "interaction": {
                "hover": true,
                "tooltipDelay": 200,
                "zoomView": true,
                "dragView": true,
                "navigationButtons": true,
                "keyboard": {
                    "enabled": true
                }
            },
            "nodes": {
                "font": {
                    "strokeWidth": 4,
                    "strokeColor": "rgba(255,255,255,0.5)"
                },
                "shadow": {
                    "enabled": true,
                    "color": "rgba(0,0,0,0.2)",
                    "size": 10,
                    "x": 5,
                    "y": 5
                }
            },
            "edges": {
                "smooth": {
                    "type": "continuous",
                    "forceDirection": "none"
                },
                "shadow": {
                    "enabled": true,
                    "color": "rgba(0,0,0,0.1)",
                    "size": 3
                },
                "arrows": {
                    "to": {
                        "enabled": false
                    }
                }
            },
            "layout": {
                "improvedLayout": true
            }
        }
        """)
        
        # Update progress
        progress_bar.progress(90)
        
        # Generate HTML file
        html_file = "mindmap_network.html"
        net.save_graph(html_file)
        
        # Add custom HTML to the file to improve interactivity
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        enhanced_html = html_content.replace('</head>', '''
        <style>
            #mynetwork {
                border-radius: 12px;
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
            }
            .legend {
                position: absolute;
                bottom: 10px;
                left: 10px;
                background-color: rgba(255, 255, 255, 0.8);
                padding: 10px;
                border-radius: 8px;
                font-family: Arial, sans-serif;
                font-size: 12px;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
                z-index: 1000;
            }
            .legend-item {
                display: flex;
                align-items: center;
                margin-bottom: 5px;
            }
            .legend-color {
                width: 12px;
                height: 12px;
                border-radius: 50%;
                margin-right: 8px;
            }
            .controls {
                position: absolute;
                top: 10px;
                right: 10px;
                background-color: rgba(255, 255, 255, 0.8);
                padding: 10px;
                border-radius: 8px;
                font-family: Arial, sans-serif;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
                z-index: 1000;
            }
            .control-btn {
                margin: 5px;
                padding: 8px 12px;
                background-color: #2563eb;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 14px;
            }
            .control-btn:hover {
                background-color: #1d4ed8;
            }
        </style>
        </head>
        ''')
# Create legend for current theme
        legend_html = '''
        <div class="legend">
            <div style="font-weight: bold; margin-bottom: 8px;">Node Importance</div>
        '''
        
        for importance, label in [("high", "High"), ("medium", "Medium"), ("low", "Low")]:
            color_index = {"high": 0, "medium": 1, "low": 2}.get(importance, 1)
            color = theme["level1"][min(color_index, len(theme["level1"])-1)]
            legend_html += f'''
            <div class="legend-item">
                <div class="legend-color" style="background-color: {color};"></div>
                <div>{label} Importance</div>
            </div>
            '''
        
        legend_html += '</div>'
        
        # Add controls for better interactivity
        controls_html = '''
        <div class="controls">
            <button class="control-btn" onclick="network.fit()">Fit View</button>
            <button class="control-btn" onclick="network.stabilize()">Stabilize</button>
        </div>
        '''
        
        # Insert legend and controls
        enhanced_html = enhanced_html.replace('<div id="mynetwork"></div>', 
                                           f'<div id="mynetwork"></div>{legend_html}{controls_html}')
        
        # Write enhanced HTML back to file
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(enhanced_html)
        
        # Complete progress
        progress_bar.progress(100)
        time.sleep(0.5)
        progress_placeholder.empty()
        
        return html_file

def display_html_file(html_file):
    """Display an HTML file in Streamlit"""
    try:
        # Read HTML file
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Create a responsive container with fixed height for the visualization
        st.markdown("""
        <div style="height: 750px; width: 100%; border-radius: 12px; overflow: hidden; box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);">
        """, unsafe_allow_html=True)
        
        # Display the HTML content
        st.components.v1.html(html_content, height=750)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Add download button for HTML file
        with open(html_file, "rb") as f:
            html_bytes = f.read()
            
        st.download_button(
            label="Download Mind Map",
            data=html_bytes,
            file_name="mindmap.html",
            mime="text/html",
            key="download_mindmap",
            help="Download the mind map as an interactive HTML file",
            use_container_width=False
        )
        
    except Exception as e:
        st.error(f"Error displaying HTML file: {str(e)}")

def display_node_explorer(mindmap_data):
    """Display a node explorer for the mindmap data"""
    if not mindmap_data:
        return
    
    st.markdown("""
    <div style="background-color: white; border-radius: 12px; padding: 1.5rem; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);">
        <h3 style="margin-top: 0; color: #2563eb; border-bottom: 2px solid #e2e8f0; padding-bottom: 0.7rem;">
            Mind Map Content Explorer
        </h3>
    """, unsafe_allow_html=True)
    
    # Display metadata if available
    if "metadata" in mindmap_data:
        metadata = mindmap_data["metadata"]
        st.markdown("#### Content Overview")
        
        meta_col1, meta_col2 = st.columns(2)
        with meta_col1:
            if "source_type" in metadata:
                st.markdown(f"**Source Type:** {metadata['source_type'].capitalize()}")
            if "estimated_reading_time" in metadata:
                st.markdown(f"**Estimated Reading Time:** {metadata['estimated_reading_time']}")
        
        with meta_col2:
            if "key_takeaway" in metadata:
                st.markdown(f"**Key Takeaway:** {metadata['key_takeaway']}")
    
    # Display central topic
    st.markdown(f"### Main Topic: {mindmap_data['central_topic']}")
    
    # Create expandable sections for each main topic
    if "children" in mindmap_data:
        for i, child in enumerate(mindmap_data["children"]):
            with st.expander(f"{child['name']}", expanded=False):
                importance = child.get("importance", "medium").capitalize()
                st.markdown(f"**Importance:** {importance}")
                
                # Show secondary topics
                if "children" in child and child["children"]:
                    st.markdown("#### Key Points:")
                    for subchild in child["children"]:
                        subimportance = subchild.get("importance", "medium").capitalize()
                        st.markdown(f"- **{subchild['name']}** _{subimportance}_")
                        
                        # Show tertiary topics if any
                        if "children" in subchild and subchild["children"]:
                            for item in subchild["children"]:
                                st.markdown(f"  - {item['name']}")
    
    st.markdown("</div>", unsafe_allow_html=True)

def display_export_options(mindmap_data):
    """Display export options for the mindmap data"""
    if not mindmap_data:
        return
        
    st.markdown("""
    <div style="background-color: white; border-radius: 12px; padding: 1.5rem; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); margin-top: 1.5rem;">
        <h3 style="margin-top: 0; color: #2563eb; border-bottom: 2px solid #e2e8f0; padding-bottom: 0.7rem;">
            Export Options
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Create JSON download button
    json_str = json.dumps(mindmap_data, indent=2)
    st.download_button(
        label="Download as JSON",
        data=json_str,
        file_name="mindmap_data.json",
        mime="application/json"
    )
    
    # Create markdown text representation
    markdown_content = f"# {mindmap_data['central_topic']}\n\n"
    
    if "metadata" in mindmap_data and "key_takeaway" in mindmap_data["metadata"]:
        markdown_content += f"**Key Takeaway:** {mindmap_data['metadata']['key_takeaway']}\n\n"
    
    # Add main topics and subtopics
    if "children" in mindmap_data:
        for child in mindmap_data["children"]:
            markdown_content += f"## {child['name']}\n"
            
            # Add secondary topics
            if "children" in child and child["children"]:
                for subchild in child["children"]:
                    markdown_content += f"### {subchild['name']}\n"
                    
                    # Add tertiary topics
                    if "children" in subchild and subchild["children"]:
                        for item in subchild["children"]:
                            markdown_content += f"- {item['name']}\n"
                    
                    markdown_content += "\n"
            
            markdown_content += "\n"
    
    # Create markdown download button
    st.download_button(
        label="Download as Markdown",
        data=markdown_content,
        file_name="mindmap_outline.md",
        mime="text/markdown"
    )

def generate_thumbnail(mindmap_data):
    """Generate a simple thumbnail image of the mindmap"""
    try:
        # Create a matplotlib figure
        plt.figure(figsize=(10, 8), facecolor='white')
        
        # Create a directed graph
        G = nx.DiGraph()
        
        # Add central node
        central_topic = mindmap_data["central_topic"]
        G.add_node(central_topic)
        
        # Add main topics
        if "children" in mindmap_data:
            for child in mindmap_data["children"]:
                child_name = child["name"]
                G.add_node(child_name)
                G.add_edge(central_topic, child_name)
                
                # Add some second-level topics
                if "children" in child and child["children"]:
                    for i, subchild in enumerate(child["children"]):
                        if i < 3:  # Limit to 3 subtopics for thumbnail
                            subchild_name = subchild["name"]
                            G.add_node(subchild_name)
                            G.add_edge(child_name, subchild_name)
        
        # Set up the layout
        pos = nx.spring_layout(G, seed=42, k=0.3)
        
        # Draw nodes
        nx.draw_networkx_nodes(G, pos, 
                              node_color='#2563eb', 
                              node_size=1500, 
                              alpha=0.8,
                              node_shape='o',
                              linewidths=1,
                              edgecolors='white')
        
        # Draw central node with different color
        nx.draw_networkx_nodes(G, pos, 
                              nodelist=[central_topic],
                              node_color='#1e40af', 
                              node_size=2500, 
                              alpha=0.9,
                              node_shape='o',
                              linewidths=2,
                              edgecolors='white')
        
        # Draw edges
        nx.draw_networkx_edges(G, pos, 
                              edge_color='#94a3b8',
                              width=2, 
                              alpha=0.7,
                              arrowsize=20,
                              node_size=1500,
                              arrowstyle='->')
        
        # Draw labels with smaller font size
        nx.draw_networkx_labels(G, pos, 
                               font_size=9,
                               font_color='white',
                               font_weight='bold',
                               font_family='sans-serif')
        
        # Save the image to a BytesIO object
        img_data = BytesIO()
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(img_data, format='PNG', dpi=100, bbox_inches='tight')
        img_data.seek(0)
        plt.close()
        
        # Convert to base64 for display
        img_base64 = base64.b64encode(img_data.getvalue()).decode()
        
        return img_base64
    except Exception as e:
        print(f"Error generating thumbnail: {str(e)}")
        return None

def show_tips():
    """Show tips for getting better mind maps"""
    st.markdown("""
    <div style="background-color: #f8fafc; border-radius: 12px; padding: 1.5rem; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05); margin-top: 1.5rem;">
        <h3 style="margin-top: 0; color: #2563eb; border-bottom: 2px solid #e2e8f0; padding-bottom: 0.7rem;">
            Tips for Better Mind Maps
        </h3>
        
        <div class="tip-box">
            <strong>Quality Content:</strong> For best results, provide clear, well-structured content with headings, paragraphs, and key points.
        </div>
        
        <div class="tip-box">
            <strong>Length Matters:</strong> Provide enough content (at least 5 paragraphs) for the AI to extract meaningful relationships and hierarchies.
        </div>
        
        <div class="tip-box">
            <strong>Complexity Setting:</strong> Choose "Detailed" for academic papers or complex topics, "Simple" for quick overviews or simpler content.
        </div>
        
        <div class="tip-box">
            <strong>Theme Selection:</strong> Choose a theme that matches your purpose - "Professional" for work presentations, "Creative" for brainstorming, etc.
        </div>
        
        <div class="tip-box">
            <strong>Adjust After Generation:</strong> Use the mind map explorer to understand the structure and download options to refine it further.
        </div>
    </div>
    """, unsafe_allow_html=True)

def show_sample_gallery():
    """Show sample mind map gallery"""
    st.markdown("""
    <div style="background-color: white; border-radius: 12px; padding: 1.5rem; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); margin-top: 1.5rem;">
        <h3 style="margin-top: 0; color: #2563eb; border-bottom: 2px solid #e2e8f0; padding-bottom: 0.7rem;">
            Sample Mind Map Gallery
        </h3>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1.5rem; margin-top: 1rem;">
    """, unsafe_allow_html=True)
    
    # Display sample thumbnails
    sample_topics = [
        {"name": "Climate Change", "theme": "nature"},
        {"name": "Project Management", "theme": "professional"},
        {"name": "Creative Writing", "theme": "creative"},
        {"name": "Machine Learning", "theme": "standard"},
        {"name": "Web Development", "theme": "vibrant"},
        {"name": "Leadership Skills", "theme": "professional"}
    ]
    
    # Create sample JSONs for thumbnails
    for sample in sample_topics:
        sample_json = {
            "central_topic": sample["name"],
            "theme": sample["theme"],
            "children": [
                {"name": f"Aspect 1 of {sample['name']}", "children": []},
                {"name": f"Aspect 2 of {sample['name']}", "children": []},
                {"name": f"Aspect 3 of {sample['name']}", "children": []},
                {"name": f"Aspect 4 of {sample['name']}", "children": []}
            ]
        }
        
        # Generate thumbnail
        img_base64 = generate_thumbnail(sample_json)
        
        if img_base64:
            st.markdown(f"""
            <div style="background-color: #f8fafc; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                <img src="data:image/png;base64,{img_base64}" style="width: 100%; height: auto;">
                <div style="padding: 1rem;">
                    <h4 style="margin: 0; color: #2563eb;">{sample['name']}</h4>
                    <p style="margin: 0.5rem 0 0 0; color: #64748b;">Theme: {sample['theme'].capitalize()}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("</div></div>", unsafe_allow_html=True)

# Main application layout
tabs = st.tabs(["Create Mind Map", "About & Tips"])

with tabs[0]:
    # Create Mind Map Tab
    left_col, right_col = st.columns([3, 2])
    
    with left_col:
        st.markdown("""
        <div class="card">
            <h2 style="margin-top: 0;">Input Your Content</h2>
            <p style="color: #475569;">Choose a content source to generate your mind map</p>
        </div>
        """, unsafe_allow_html=True)
        
        input_type = st.radio(
            "Select input method:",
            ["Text Input", "URL", "YouTube Video", "PDF Upload"],
            horizontal=True
        )
        
        content_text = None
        
        # Handle different input types
        if input_type == "Text Input":
            content_text = st.text_area(
                "Enter your content here (articles, lecture notes, essays, etc.):",
                height=300,
                placeholder="Paste or type your content here. The more detailed and structured the content, the better the mind map."
            )
        
        elif input_type == "URL":
            url = st.text_input("Enter webpage URL:", placeholder="https://example.com/article")
            if url:
                content_text = extract_text_from_url(url)
                if content_text:
                    st.success(f"Successfully extracted content from URL (Length: {len(content_text)} characters)")
                    
                    # Show preview
                    with st.expander("Show content preview"):
                        st.text(content_text[:1000] + "...")
        
        elif input_type == "YouTube Video":
            youtube_url = st.text_input("Enter YouTube video URL:", placeholder="https://www.youtube.com/watch?v=...")
            if youtube_url:
                content_text = extract_text_from_youtube(youtube_url)
                if content_text:
                    st.success(f"Successfully extracted transcript from YouTube video (Length: {len(content_text)} characters)")
                    
                    # Show preview
                    with st.expander("Show transcript preview"):
                        st.text(content_text[:1000] + "...")
        
        elif input_type == "PDF Upload":
            uploaded_file = st.file_uploader("Upload a PDF file", type=['pdf'])
            if uploaded_file:
                content_text = extract_text_from_pdf(uploaded_file)
                if content_text:
                    st.success(f"Successfully extracted text from PDF (Length: {len(content_text)} characters)")
                    
                    # Show preview
                    with st.expander("Show content preview"):
                        st.text(content_text[:1000] + "...")
    
    with right_col:
        st.markdown("""
        <div class="card">
            <h2 style="margin-top: 0;">Mind Map Options</h2>
            <p style="color: #475569;">Customize your mind map appearance and structure</p>
        </div>
        """, unsafe_allow_html=True)
        
        theme_option = st.selectbox(
            "Visual Theme:",
            ["standard", "nature", "creative", "professional", "vibrant"],
            index=0,
            format_func=lambda x: x.capitalize()
        )
        
        complexity = st.select_slider(
            "Complexity Level:",
            options=["simple", "standard", "detailed"],
            value="standard",
            format_func=lambda x: x.capitalize()
        )
        
        # Display theme preview
        theme_colors = {
            "standard": "#2563eb",
            "nature": "#047857",
            "creative": "#7c3aed",
            "professional": "#1e293b",
            "vibrant": "#db2777"
        }
        
        st.markdown(f"""
        <div style="margin-top: 1rem; margin-bottom: 1rem;">
            <span style="font-weight: 600;">Theme Preview:</span>
            <div style="display: flex; align-items: center; margin-top: 0.5rem;">
                <div style="width: 24px; height: 24px; border-radius: 50%; background-color: {theme_colors[theme_option]}; margin-right: 0.5rem;"></div>
                <span>{theme_option.capitalize()}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Generate button row
    generate_col1, generate_col2 = st.columns([3, 1])
    
    with generate_col1:
        generate_button = st.button("Generate Mind Map", type="primary", use_container_width=True)
    
    with generate_col2:
        clear_button = st.button("Clear", type="secondary", use_container_width=True)
    
    # Reset everything if clear is pressed
    if clear_button:
        st.experimental_rerun()
    
    # Generate Mind Map when button is clicked
    if generate_button and content_text:
        mindmap_data = generate_mindmap_json(content_text, theme_option, complexity)
        
        if mindmap_data:
            st.session_state.mindmap_data = mindmap_data
            
            # Show success message
            st.markdown("""
            <div class="success-msg">
                Mind map successfully generated! Scroll down to explore.
            </div>
            """, unsafe_allow_html=True)
            
            # Create tabs for different views
            result_tabs = st.tabs(["Visualization", "Content Explorer", "Export Options"])
            
            with result_tabs[0]:
                # Create and display visualization
                html_file = create_pyvis_network(mindmap_data)
                if html_file:
                    display_html_file(html_file)
            
            with result_tabs[1]:
                # Display node explorer
                display_node_explorer(mindmap_data)
            
            with result_tabs[2]:
                # Display export options
                display_export_options(mindmap_data)
    
    elif generate_button and not content_text:
        st.error("Please enter or upload content first.")

with tabs[1]:
    # About & Tips Tab
    st.markdown("""
    <div class="card">
        <h2 style="margin-top: 0;">About Mind Map Generator</h2>
        <p>This tool uses advanced AI to transform any content into an interactive, visually engaging mind map. 
        Perfect for students, researchers, writers, and professionals looking to organize and understand complex information.</p>
        
        <h3>Key Features</h3>
        <ul>
            <li><strong>Multiple Input Sources:</strong> Text, URLs, YouTube videos, and PDFs</li>
            <li><strong>Interactive Visualization:</strong> Explore your content through an engaging network visualization</li>
            <li><strong>Custom Themes:</strong> Choose from multiple visual styles to suit your purpose</li>
            <li><strong>Adjustable Complexity:</strong> Control the detail level of your mind map</li>
            <li><strong>Export Options:</strong> Download as HTML, JSON, or Markdown for further editing</li>
        </ul>
        
        <h3>Perfect For</h3>
        <ul>
            <li>Summarizing research papers and academic content</li>
            <li>Creating study guides from lecture notes or textbooks</li>
            <li>Organizing thoughts and ideas for writing projects</li>
            <li>Breaking down complex concepts into manageable chunks</li>
            <li>Generating visual aids for presentations</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Display tips
    show_tips()
    
    # Display sample gallery
    show_sample_gallery()

# Add footer
st.markdown("""
<div class="footer">
    <p>Created with ❤️ using Streamlit and Google Gemini | Version 1.2.0</p>
</div>
""", unsafe_allow_html=True)