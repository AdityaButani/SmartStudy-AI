import streamlit as st
import os
from groq import Groq
from dotenv import load_dotenv
import json
import time
import re

# Load environment variables from .env file
load_dotenv()

# Initialize Groq client
client = Groq(
    api_key=os.environ.get("GROQ_API_KEY")
)

# Set page configuration
st.set_page_config(
    page_title="WriteWise - AI Creative Writing Mentor",
    page_icon="✍️",
    layout="wide"
)

# Custom CSS for better appearance
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stTextArea textarea {
        height: 300px;
    }
    .feedback-box {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        background-color: #f8f9fa;
    }
    .highlight {
        background-color: #FFE8B2;
        padding: 2px 5px;
        border-radius: 3px;
    }
    .suggestion {
        color: #1E6823;
        font-weight: 500;
    }
    h1, h2, h3 {
        color: #1E3A8A;
    }
    </style>
""", unsafe_allow_html=True)

# Application title and description
st.title("✍️ WriteWise: AI Creative Writing Mentor")
st.markdown("""
    Transform your storytelling with deep analysis of tone, style, and narrative flow.
    Get personalized suggestions for plot twists, character development, and dialogue improvements.
""")

# Sidebar configuration
with st.sidebar:
    st.header("Analysis Settings")
    
    analysis_depth = st.select_slider(
        "Analysis Depth",
        options=["Quick", "Standard", "Deep"],
        value="Standard",
        help="Deeper analysis provides more detailed feedback but takes longer"
    )
    
    focus_areas = st.multiselect(
        "Focus Areas",
        ["Narrative Structure", "Character Development", "Dialogue", "Emotional Impact", 
         "Pacing", "World Building", "Thematic Elements", "Style Consistency"],
        default=["Narrative Structure", "Character Development", "Emotional Impact"],
        help="Select specific aspects of your writing to receive focused feedback on"
    )
    
    genre = st.selectbox(
        "Genre",
        ["General", "Science Fiction", "Fantasy", "Mystery", "Romance", "Horror", 
         "Literary Fiction", "Historical Fiction", "Young Adult", "Children's Literature"],
        index=0,
        help="Providing your genre helps tailor the analysis to genre-specific conventions"
    )
    
    st.divider()
    
    model = st.selectbox(
        "AI Model",
        ["llama3-8b-8192", "llama3-70b-8192", "mixtral-8x7b-32768", "gemma-7b-it"],
        index=1,
        help="Select the Groq LLM model to use for analysis"
    )

    st.divider()
    
    temperature = st.slider("Creativity Level", min_value=0.0, max_value=1.0, value=0.7, step=0.1,
                       help="Higher values make suggestions more creative but potentially less focused")
    
    st.divider()
    
    # Sample text examples for demonstration
    st.subheader("Try Sample Texts")
    
    sample_texts = {
        "Fantasy Adventure": """The ancient tower loomed against the blood-red sunset, its twisted spires reaching like desperate fingers toward the sky. Elara clutched her mother's amulet, feeling its warmth pulse against her palm. "We shouldn't be here," Thorne whispered, his hand resting nervously on his sword hilt. "The boundary stones were a warning, not a challenge." But Elara had come too far to turn back now.""",
        
        "Noir Mystery": """The rain hammered against my office window like it had a personal vendetta. Three days without a client, and my bottle of whiskey wasn't getting any fuller. Then she walked in—red dress, troubled eyes, and a story that stank worse than the harbor at low tide. "Mr. Blackwood," she said, voice steady despite her trembling hands, "I need you to find someone who doesn't want to be found." Don't they all?""",
        
        "Coming of Age": """The graduation caps made black constellations against the summer sky. Emma stood apart from her classmates, diploma clutched so tight her knuckles ached. Eighteen years in this town, and tomorrow she'd be gone. Her father's voice echoed in her head: "Sometimes leaving is the only way to find yourself." She wondered if he'd known that when he left them five years ago."""
    }
    
    selected_sample = st.selectbox("Load Sample Text", ["None"] + list(sample_texts.keys()))
    
    if selected_sample != "None" and st.button("Load Sample"):
        st.session_state.writing_text = sample_texts[selected_sample]

# Initialize session state for storing text and analysis results
if 'writing_text' not in st.session_state:
    st.session_state.writing_text = ""
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'is_analyzing' not in st.session_state:
    st.session_state.is_analyzing = False

# Main text input area
text_input = st.text_area("Enter your writing here (paragraphs, scenes, or entire stories):", 
                          value=st.session_state.writing_text,
                          height=300)

# Update session state when text changes
if text_input != st.session_state.writing_text:
    st.session_state.writing_text = text_input
    st.session_state.analysis_results = None  # Reset analysis when text changes

# Character and word count display
if st.session_state.writing_text:
    col1, col2 = st.columns(2)
    word_count = len(re.findall(r'\b\w+\b', st.session_state.writing_text))
    with col1:
        st.info(f"Characters: {len(st.session_state.writing_text)}")
    with col2:
        st.info(f"Words: {word_count}")

# Analysis button and process
if st.button("Analyze My Writing", disabled=st.session_state.is_analyzing or not st.session_state.writing_text.strip()):
    st.session_state.is_analyzing = True
    progress_bar = st.progress(0)
    
    # Define the analysis request based on user settings
    depth_tokens = {"Quick": 1800, "Standard": 2500, "Deep": 4000}
    max_tokens = depth_tokens[analysis_depth]
    
    # Create the prompt for the LLM
    prompt = f"""You are WritingMuse, a professional creative writing mentor with expertise in literary analysis and storytelling. 
    Analyze the following piece of creative writing in the {genre} genre, focusing specifically on {', '.join(focus_areas)}.

    Your job is to provide helpful, constructive feedback that will improve the writer's craft while respecting their unique voice and style.

    Text to analyze:
    ```
    {st.session_state.writing_text}
    ```

    Provide your analysis in the following JSON format:
    {{
        "overall_impression": "Brief overall impression of the writing (2-3 sentences)",
        "tone_and_style": {{
            "description": "Analysis of the writer's tone and stylistic choices",
            "strengths": ["List 2-3 stylistic strengths"],
            "improvement_areas": ["List 2-3 areas for stylistic improvement"]
        }},
        "narrative_flow": {{
            "description": "Analysis of how the narrative progresses and flows",
            "strengths": ["List 2-3 strengths in narrative structure"],
            "improvement_areas": ["List 2-3 areas for narrative improvement"]
        }},
        "emotional_impact": {{
            "description": "Analysis of the emotional resonance of the piece",
            "strongest_moments": ["List 1-2 emotionally strong moments"],
            "enhancement_suggestions": ["List 2-3 ways to enhance emotional impact"]
        }},
        "dialogue_assessment": {{
            "description": "Analysis of dialogue if present, or suggestions for adding it if not",
            "natural_examples": ["Example of particularly natural dialogue if present"],
            "improvement_suggestions": ["List 2-3 ways to improve dialogue or add effective dialogue"]
        }},
        "creative_suggestions": {{
            "plot_developments": ["List 2-3 interesting ways the plot could develop"],
            "character_developments": ["List 2-3 ways characters could be developed further"],
            "world_building": ["Suggestion for enriching the story's world"]
        }},
        "specific_examples": [
            {{
                "original_text": "A short excerpt from the original text (1-2 sentences max)",
                "suggestion": "A specific rewrite suggestion showing how it could be improved",
                "explanation": "Brief explanation of why this change helps"
            }},
            {{
                "original_text": "Another short excerpt from the original text",
                "suggestion": "Another specific rewrite suggestion",
                "explanation": "Brief explanation of why this change helps"
            }}
        ]
    }}

    Format your response as valid JSON without any additional text outside the JSON structure.
    """
    
    # Simulate progress
    for i in range(10):
        progress_bar.progress((i + 1) * 10)
        time.sleep(0.2)
    
    try:
        # Call the Groq API
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are WritingMuse, a creative writing mentor with expertise in narrative analysis."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=1
        )
        
        # Extract and parse the JSON response
        result_text = response.choices[0].message.content
        # Find JSON content (in case there's any text outside the JSON structure)
        json_pattern = r'({[\s\S]*})'
        json_match = re.search(json_pattern, result_text)
        
        if json_match:
            result_text = json_match.group(1)
            
        analysis_data = json.loads(result_text)
        st.session_state.analysis_results = analysis_data
        
    except Exception as e:
        st.error(f"Error analyzing your writing: {str(e)}")
        st.session_state.analysis_results = None
    finally:
        st.session_state.is_analyzing = False
        progress_bar.empty()
        
# Display analysis results
if st.session_state.analysis_results:
    analysis = st.session_state.analysis_results
    
    st.subheader("📝 Analysis Results")
    
    # Overall impression section
    st.markdown(f"### Overall Impression")
    st.markdown(f"<div class='feedback-box'>{analysis['overall_impression']}</div>", unsafe_allow_html=True)
    
    # Create tabs for different analysis sections
    tab1, tab2, tab3, tab4 = st.tabs(["Style & Narrative", "Emotional Impact", "Dialogue", "Creative Suggestions"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🎭 Tone & Style")
            st.markdown(f"<div class='feedback-box'>{analysis['tone_and_style']['description']}</div>", unsafe_allow_html=True)
            
            st.markdown("#### Strengths:")
            for strength in analysis['tone_and_style']['strengths']:
                st.markdown(f"- ✅ {strength}")
                
            st.markdown("#### Areas for Improvement:")
            for area in analysis['tone_and_style']['improvement_areas']:
                st.markdown(f"- 🔍 {area}")
        
        with col2:
            st.markdown("### 📊 Narrative Flow")
            st.markdown(f"<div class='feedback-box'>{analysis['narrative_flow']['description']}</div>", unsafe_allow_html=True)
            
            st.markdown("#### Strengths:")
            for strength in analysis['narrative_flow']['strengths']:
                st.markdown(f"- ✅ {strength}")
                
            st.markdown("#### Areas for Improvement:")
            for area in analysis['narrative_flow']['improvement_areas']:
                st.markdown(f"- 🔍 {area}")
    
    with tab2:
        st.markdown("### ❤️ Emotional Impact")
        st.markdown(f"<div class='feedback-box'>{analysis['emotional_impact']['description']}</div>", unsafe_allow_html=True)
        
        st.markdown("#### Strongest Emotional Moments:")
        for moment in analysis['emotional_impact']['strongest_moments']:
            st.markdown(f"- 🌟 {moment}")
            
        st.markdown("#### Enhancement Suggestions:")
        for suggestion in analysis['emotional_impact']['enhancement_suggestions']:
            st.markdown(f"- 💡 {suggestion}")
    
    with tab3:
        st.markdown("### 💬 Dialogue Assessment")
        st.markdown(f"<div class='feedback-box'>{analysis['dialogue_assessment']['description']}</div>", unsafe_allow_html=True)
        
        if analysis['dialogue_assessment'].get('natural_examples') and analysis['dialogue_assessment']['natural_examples'][0]:
            st.markdown("#### Natural Examples:")
            for example in analysis['dialogue_assessment']['natural_examples']:
                if example:  # Check if not empty
                    st.markdown(f"- 👍 \"{example}\"")
            
        st.markdown("#### Improvement Suggestions:")
        for suggestion in analysis['dialogue_assessment']['improvement_suggestions']:
            st.markdown(f"- 💡 {suggestion}")
    
    with tab4:
        st.markdown("### 💫 Creative Suggestions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Plot Developments:")
            for plot in analysis['creative_suggestions']['plot_developments']:
                st.markdown(f"- 📚 {plot}")
                
            st.markdown("#### Character Developments:")
            for character in analysis['creative_suggestions']['character_developments']:
                st.markdown(f"- 👤 {character}")
        
        with col2:
            st.markdown("#### World Building:")
            for world in analysis['creative_suggestions']['world_building']:
                st.markdown(f"- 🌍 {world}")
    
    # Specific examples section
    st.subheader("📌 Specific Examples & Suggestions")
    
    for i, example in enumerate(analysis['specific_examples']):
        with st.expander(f"Example {i+1}"):
            st.markdown("**Original Text:**")
            st.markdown(f"<div class='feedback-box'>{example['original_text']}</div>", unsafe_allow_html=True)
            
            st.markdown("**Suggestion:**")
            st.markdown(f"<div class='feedback-box suggestion'>{example['suggestion']}</div>", unsafe_allow_html=True)
            
            st.markdown("**Why This Works Better:**")
            st.markdown(f"{example['explanation']}")

# Footer
st.divider()
st.markdown("""
    <div style="text-align: center; color: #666;">
        WriteWise - Helping writers unleash their creative potential.
    </div>
""", unsafe_allow_html=True)