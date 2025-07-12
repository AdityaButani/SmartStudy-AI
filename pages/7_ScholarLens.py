import streamlit as st
from groq import Groq
import os
from dotenv import load_dotenv
import requests
import json
from datetime import datetime
import re

# Page configuration
st.set_page_config(
    page_title="Academic Paper Analyzer",
    page_icon="📄",
    layout="wide"
)

# Load environment variables
load_dotenv()
groq_api_key = os.environ.get("GROQ_API_KEY")
serper_api_key = os.environ.get("SERPER_API_KEY")

if not groq_api_key:
    st.error("❌ GROQ_API_KEY environment variable not set. Please set it.")
    st.stop()

if not serper_api_key:
    st.error("❌ SERPER_API_KEY environment variable not set. Please set it.")
    st.stop()

# Initialize Groq client
client = Groq(api_key=groq_api_key)

# Initialize session state variables
if "search_history" not in st.session_state:
    st.session_state.search_history = []
if "papers" not in st.session_state:
    st.session_state.papers = []
if "current_paper_id" not in st.session_state:
    st.session_state.current_paper_id = None
if "paper_analyses" not in st.session_state:
    st.session_state.paper_analyses = {}
if "model" not in st.session_state:
    st.session_state.model = "llama3-70b-8192"
if "saved_papers" not in st.session_state:
    st.session_state.saved_papers = []

def search_papers(query, limit=8):
    """Search for papers using Serper API (Google Scholar)"""
    url = "https://google.serper.dev/scholar"
    payload = json.dumps({
        "q": query,
        "num": limit
    })
    headers = {
        'X-API-KEY': serper_api_key,
        'Content-Type': 'application/json'
    }
    
    try:
        with st.spinner("Searching for papers..."):
            response = requests.post(url, headers=headers, data=payload)
            
            if response.status_code == 200:
                results = response.json().get("organic", [])
                papers = []
                
                for i, result in enumerate(results):
                    # Extract relevant information from Serper API response
                    paper = {
                        "id": f"paper_{i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        "title": result.get("title", "No title"),
                        "authors": parse_authors(result.get("authors", "")),
                        "year": extract_year(result.get("publicationInfo", "")),
                        "venue": result.get("publication", "N/A"),
                        "abstract": result.get("snippet", "No abstract available"),
                        "url": result.get("link", "#"),
                        "citation_count": extract_citation_count(result.get("citationCount", ""))
                    }
                    papers.append(paper)
                
                # Add search to history
                if papers and query not in [h["query"] for h in st.session_state.search_history]:
                    st.session_state.search_history.append({
                        "query": query,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "count": len(papers)
                    })
                    # Keep only last 10 searches
                    if len(st.session_state.search_history) > 10:
                        st.session_state.search_history.pop(0)
                
                return papers
            else:
                st.error(f"API Error: {response.status_code}, {response.text}")
                return []
    except Exception as e:
        st.error(f"Error searching papers: {str(e)}")
        return []

def parse_authors(authors_string):
    """Parse authors string into a list of author objects"""
    if not authors_string:
        return []
    
    # Split author string by commas or 'and'
    authors_list = [name.strip() for name in authors_string.replace(" and ", ", ").split(",")]
    
    # Convert to the format expected by the UI
    return [{"name": author} for author in authors_list if author]

def extract_year(publication_info):
    """Extract year from publication info string"""
    # Try to find a 4-digit year in the string
    year_match = re.search(r'(19|20)\d{2}', publication_info)
    if year_match:
        return year_match.group(0)
    return "N/A"

def extract_citation_count(citation_string):
    """Extract citation count from citation string"""
    if not citation_string:
        return 0
    
    # Try to find a number in the citation string
    match = re.search(r'(\d+)', str(citation_string))
    if match:
        return int(match.group(1))
    return 0

def save_paper(paper):
    """Save a paper to the user's library"""
    if paper not in st.session_state.saved_papers:
        st.session_state.saved_papers.append(paper)
        return True
    return False

def remove_paper(paper_id):
    """Remove a paper from the user's library"""
    st.session_state.saved_papers = [p for p in st.session_state.saved_papers if p["id"] != paper_id]

def analyze_paper(paper):
    """Generate an in-depth analysis of the paper using LLM"""
    
    prompt = f"""
    Please provide a comprehensive analysis of the following academic paper:
    
    Title: {paper['title']}
    Authors: {', '.join([author.get('name', '') for author in paper.get('authors', [])])}
    Year: {paper['year']}
    Venue: {paper['venue']}
    Abstract: {paper['abstract']}
    
    Please include:
    1. A clear summary of the paper's main contributions and findings
    2. The research methodology used
    3. The theoretical framework or background
    4. Practical implications of the research
    5. Limitations of the study
    6. How this paper connects to related work in the field
    7. Potential research directions that build on this work
    8. Key concepts that students should understand from this paper
    
    Format your response in a clear, structured way that would help a student understand this paper deeply.
    """
    
    try:
        with st.spinner(f"Analyzing paper: {paper['title']}..."):
            response = client.chat.completions.create(
                model=st.session_state.model,
                messages=[
                    {"role": "system", "content": "You are an academic research assistant that helps students understand research papers. Your analysis should be thorough yet accessible."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2048
            )
            
            analysis = response.choices[0].message.content
            # Store analysis in session state
            st.session_state.paper_analyses[paper["id"]] = analysis
            return analysis
    except Exception as e:
        st.error(f"Error analyzing paper: {str(e)}")
        return "Unable to generate analysis. Please try again later."

def format_authors(authors):
    """Format author list nicely"""
    if not authors:
        return "Unknown"
    
    author_names = [a.get("name", "") for a in authors]
    if len(author_names) == 1:
        return author_names[0]
    elif len(author_names) == 2:
        return f"{author_names[0]} and {author_names[1]}"
    else:
        return f"{author_names[0]} et al."

def get_paper_by_id(paper_id):
    """Get paper object by ID from papers or saved papers"""
    for paper in st.session_state.papers:
        if paper["id"] == paper_id:
            return paper
    
    for paper in st.session_state.saved_papers:
        if paper["id"] == paper_id:
            return paper
    
    return None

# Sidebar
with st.sidebar:
    st.title("📄 ScholarLens")
    
    # Model selection
    st.markdown("### Model Settings")
    model_options = {
        'Llama3 70b': 'llama3-70b-8192',
        'Llama3 8b': 'llama3-8b-8192',
        'Mixtral 8x7b': 'mixtral-8x7b-32768'
    }
    selected_model = st.selectbox(
        "Analysis Model:",
        options=list(model_options.keys()),
        index=0
    )
    st.session_state.model = model_options[selected_model]
    
    st.divider()
    
    # Search history
    st.markdown("### Recent Searches")
    if st.session_state.search_history:
        for history in reversed(st.session_state.search_history):
            if st.button(
                f"🔍 {history['query'][:25]}... ({history['count']} papers)",
                key=f"history_{history['query'][:10]}",
                use_container_width=True
            ):
                # Re-run the search
                st.session_state.papers = search_papers(history['query'])
                st.session_state.current_paper_id = None  # Reset current paper
                st.rerun()
    else:
        st.info("Your search history will appear here")
    
    st.divider()
    
    # Saved papers count
    st.markdown(f"### Saved Papers: {len(st.session_state.saved_papers)}")
    if st.session_state.saved_papers:
        for paper in st.session_state.saved_papers:
            if st.button(
                f"📎 {paper['title'][:30]}...",
                key=f"saved_{paper['id']}",
                use_container_width=True
            ):
                # Set this as current paper
                st.session_state.current_paper_id = paper['id']
                # Make sure it's in the paper list
                if paper not in st.session_state.papers:
                    st.session_state.papers = [paper] + st.session_state.papers
                st.rerun()

# Main content area
st.title("ScholarLens - Academic Paper Search & Analysis")

# Research interface at the top
st.markdown("""
<div class="search-card">
    <h3>Research Paper Search</h3>
    <p>Search for academic papers related to your research topic. Results will include paper details, abstracts, and in-depth analysis.</p>
</div>
""", unsafe_allow_html=True)

# Search interface
col1, col2 = st.columns([0.8, 0.2])

with col1:
    search_query = st.text_input("Enter keywords, title, author, or topic to search for papers:", key="search_box")

with col2:
    search_button = st.button("🔍 Search", use_container_width=True)

# Advanced search options
with st.expander("Advanced Search Options"):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        year_filter = st.selectbox(
            "Publication Year:",
            options=["Any", "Last 5 years", "Last 10 years", "Custom..."],
            index=0
        )
        
        if year_filter == "Custom...":
            year_range = st.slider("Select Year Range:", 1950, datetime.now().year, (2010, datetime.now().year))
    
    with col2:
        sort_by = st.selectbox(
            "Sort Results By:",
            options=["Relevance", "Citation Count", "Recency"],
            index=0
        )
    
    with col3:
        result_limit = st.slider("Number of Results:", 5, 15, 8)

# Run search
if search_button and search_query:
    # Modify search query with advanced filters
    modified_query = search_query
    if year_filter == "Last 5 years":
        modified_query += f" after:{datetime.now().year - 5}"
    elif year_filter == "Last 10 years":
        modified_query += f" after:{datetime.now().year - 10}"
    elif year_filter == "Custom...":
        modified_query += f" after:{year_range[0]} before:{year_range[1]}"
    
    # Get papers
    st.session_state.papers = search_papers(modified_query, limit=result_limit)
    st.session_state.current_paper_id = None  # Reset current paper selection

# Display search results and analyses
if st.session_state.papers:
    # Sort results if needed
    if "sort_by" in locals():
        if sort_by == "Citation Count":
            st.session_state.papers.sort(key=lambda x: x.get("citation_count", 0), reverse=True)
        elif sort_by == "Recency":
            st.session_state.papers.sort(key=lambda x: x.get("year", "0000"), reverse=True)
    
    st.markdown(f"### Found {len(st.session_state.papers)} Relevant Papers")
    
    # Display papers
    for i, paper in enumerate(st.session_state.papers):
        paper_id = paper['id']
        is_current = st.session_state.current_paper_id == paper_id
        
        # Paper card with elevated style if selected
        card_style = "paper-card" if not is_current else "paper-card paper-card-selected"
        
        with st.container():
            st.markdown(f"""
            <div class="{card_style}">
                <h3>{paper['title']}</h3>
                <p class="authors"><strong>Authors:</strong> {format_authors(paper['authors'])}</p>
                <div class="paper-meta">
                    <span class="year"><strong>Year:</strong> {paper['year']}</span>
                    <span class="venue"><strong>Venue:</strong> {paper['venue']}</span>
                    <span class="citations"><strong>Citations:</strong> {paper['citation_count']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Paper abstract is always shown but in a collapsible section
            with st.expander("📖 Abstract", expanded=is_current):
                st.markdown(f"""
                <div class="abstract-box">
                    {paper['abstract']}
                </div>
                """, unsafe_allow_html=True)
            
            # Paper actions
            col1, col2, col3 = st.columns([1, 1, 2])
            
            with col1:
                if st.button(f"🔍 {'' if is_current else 'Show '}Analysis", key=f"analyze_{paper_id}", 
                           use_container_width=True):
                    st.session_state.current_paper_id = paper_id
                    st.rerun()
            
            with col2:
                is_saved = paper in st.session_state.saved_papers
                if is_saved:
                    if st.button(f"❌ Remove Saved", key=f"unsave_{paper_id}", use_container_width=True):
                        remove_paper(paper_id)
                        st.rerun()
                else:
                    if st.button(f"📎 Save Paper", key=f"save_{paper_id}", use_container_width=True):
                        if save_paper(paper):
                            st.success("Paper saved!")
                            st.rerun()
            
            with col3:
                st.markdown(f"""
                <div class="link-container">
                    <a href="{paper['url']}" class="button-link" target="_blank">🔗 View Original Paper</a>
                </div>
                """, unsafe_allow_html=True)
            
            # Show analysis if this is the current paper
            if is_current:
                st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
                st.markdown(f"## Analysis: {paper['title']}")
                
                # Check if we already have an analysis
                if paper_id in st.session_state.paper_analyses:
                    analysis = st.session_state.paper_analyses[paper_id]
                else:
                    # Generate a new analysis
                    analysis = analyze_paper(paper)
                
                # Display analysis sections in tabs
                if analysis:
                    # Parse the analysis into sections
                    sections = re.split(r'##?\s+', analysis)
                    
                    # First part is usually introduction
                    if sections and len(sections) > 1:
                        intro = sections[0].strip()
                        if intro:
                            st.markdown(f"""
                            <div class="analysis-intro">
                                {intro}
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Create tabs for the rest of the sections
                        section_titles = []
                        section_contents = []
                        
                        for section in sections[1:]:
                            lines = section.strip().split('\n', 1)
                            if len(lines) > 1:
                                title, content = lines
                                section_titles.append(title.strip())
                                section_contents.append(content.strip())
                        
                        if section_titles:
                            tabs = st.tabs(section_titles)
                            for i, tab in enumerate(tabs):
                                with tab:
                                    st.markdown(section_contents[i])
                    else:
                        # If no clear sections, just display the whole analysis
                        st.markdown(analysis)
                    
                    # Regenerate analysis button
                    if st.button("🔄 Regenerate Analysis", key=f"regen_{paper_id}"):
                        analysis = analyze_paper(paper)
                        st.rerun()
                else:
                    st.info("Analysis is being generated...")
                
                st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
            
            st.markdown("<hr>", unsafe_allow_html=True)
else:
    if search_button and search_query:
        st.info("No papers found matching your search criteria. Try different keywords.")
    else:
        st.info("Enter keywords above and click 'Search' to find relevant papers")

# Add CSS
st.markdown("""
<style>
.stApp {
    background-color: #f8f9fa;
}

.search-card {
    background-color: #ffffff;
    border-radius: 10px;
    padding: 1.2rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.08);
    border: 1px solid #e9ecef;
}

.paper-card {
    background-color: #ffffff;
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 2px 5px rgba(0,0,0,0.06);
    border-left: 4px solid #3b82f6;
    transition: all 0.2s ease;
}

.paper-card-selected {
    border-left: 6px solid #2563eb;
    background-color: #f0f7ff;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.15);
}

.paper-card h3 {
    color: #1e3a8a;
    margin-bottom: 0.6rem;
    font-size: 1.25rem;
    line-height: 1.4;
}

.authors {
    color: #4b5563;
    margin-bottom: 0.7rem;
    font-size: 0.95rem;
}

.paper-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 0.8rem;
    margin-top: 0.7rem;
}

.year, .venue, .citations {
    font-size: 0.85rem;
    padding: 0.3rem 0.7rem;
    background-color: #f1f5f9;
    border-radius: 20px;
    display: inline-flex;
    align-items: center;
}

.citations {
    background-color: #e0f2fe;
    color: #0369a1;
    font-weight: 500;
}

.abstract-box {
    background-color: #ffffff;
    border-left: 3px solid #64748b;
    padding: 1.2rem;
    margin: 0.8rem 0;
    border-radius: 4px;
    font-size: 1rem;
    line-height: 1.6;
    color: #334155;
}

.analysis-intro {
    background-color: #f0f9ff;
    padding: 1rem;
    border-radius: 6px;
    margin-bottom: 1.2rem;
    font-size: 1rem;
    line-height: 1.6;
    color: #0c4a6e;
}

.section-divider {
    margin: 1.5rem 0;
    border: none;
    height: 1px;
    background-color: #cbd5e1;
}

hr {
    margin: 1.5rem 0;
    border: none;
    height: 1px;
    background-color: #e2e8f0;
}

.link-container {
    display: flex;
    justify-content: flex-end;
}

.button-link {
    display: inline-block;
    padding: 0.5rem 1rem;
    background-color: #3b82f6;
    color: white !important;
    text-decoration: none;
    border-radius: 4px;
    font-weight: 500;
    text-align: center;
    transition: all 0.2s ease;
}

.button-link:hover {
    background-color: #2563eb;
    box-shadow: 0 2px 4px rgba(37, 99, 235, 0.3);
    transform: translateY(-1px);
}

/* Make the tabs more visually appealing */
.stTabs [data-baseweb="tab-list"] {
    gap: 0.5rem;
}

.stTabs [data-baseweb="tab"] {
    padding: 0.5rem 1rem;
    background-color: #f1f5f9;
    border-radius: 6px 6px 0 0;
}

.stTabs [aria-selected="true"] {
    background-color: #e0f2fe !important;
    font-weight: 600;
}

/* Custom styling for Streamlit expander */
.streamlit-expanderHeader {
    font-size: 1rem;
    font-weight: 600;
    color: #1e40af;
}

/* Improve button styles */
button[kind="primary"] {
    background-color: #3b82f6;
    border: none;
    transition: all 0.2s ease;
}

button[kind="primary"]:hover {
    background-color: #2563eb;
    box-shadow: 0 2px 4px rgba(37, 99, 235, 0.3);
}
</style>
""", unsafe_allow_html=True)