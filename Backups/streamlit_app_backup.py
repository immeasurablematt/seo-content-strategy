"""
Streamlit SEO Content Brief Generator
A user-friendly web interface for generating SEO content briefs

To run: streamlit run streamlit_app.py
"""

import streamlit as st
import os
import json
import base64
import requests
import csv
from datetime import datetime
from dotenv import load_dotenv
from anthropic import Anthropic
from bs4 import BeautifulSoup

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="SEO Brief Generator",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .status-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'brief_generated' not in st.session_state:
    st.session_state.brief_generated = False
if 'brief_content' not in st.session_state:
    st.session_state.brief_content = ""
if 'keyword_metrics' not in st.session_state:
    st.session_state.keyword_metrics = {}
if 'serp_results' not in st.session_state:
    st.session_state.serp_results = {}
if 'competition_assessment' not in st.session_state:
    st.session_state.competition_assessment = {}

# API Configuration
DATAFORSEO_BASE_URL = "https://api.dataforseo.com/v3"

# Helper Functions
def get_dataforseo_auth():
    """Create Basic Authentication header for DataForSEO API"""
    login = os.getenv("DATAFORSEO_LOGIN")
    password = os.getenv("DATAFORSEO_PASSWORD")
    credentials = f"{login}:{password}"
    encoded = base64.b64encode(credentials.encode()).decode()
    return {
        "Authorization": f"Basic {encoded}",
        "Content-Type": "application/json"
    }

def get_keyword_metrics(keyword):
    """Fetch keyword metrics from DataForSEO"""
    try:
        url = f"{DATAFORSEO_BASE_URL}/keywords_data/google_ads/search_volume/live"
        payload = [{
            "keywords": [keyword],
            "location_code": 2840,
            "language_code": "en",
            "search_partners": False,
            "include_adult_keywords": False
        }]
        
        response = requests.post(url, headers=get_dataforseo_auth(), json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if data.get("tasks") and len(data["tasks"]) > 0:
            task_result = data["tasks"][0]
            if task_result.get("result") and len(task_result["result"]) > 0:
                result_data = task_result["result"][0]
                return {
                    "keyword": keyword,
                    "search_volume": result_data.get("search_volume"),
                    "competition": result_data.get("competition"),
                    "competition_index": result_data.get("competition_index"),
                    "cpc": result_data.get("cpc"),
                    "monthly_searches": result_data.get("monthly_searches", [])[:12]
                }
        return {"error": "No results found"}
    except Exception as e:
        return {"error": str(e)}

def get_domain_metrics(domains):
    """Fetch domain authority metrics from DataForSEO"""
    try:
        url = f"{DATAFORSEO_BASE_URL}/dataforseo_labs/google/domain_rank_overview/live"
        
        payload = []
        clean_domains = []
        for domain in domains:
            clean = domain.replace('https://', '').replace('http://', '').replace('www.', '')
            clean = clean.split('/')[0]
            if clean:
                clean_domains.append(clean)
                payload.append({
                    "target": clean,
                    "location_code": 2840,
                    "language_code": "en"
                })
        
        response = requests.post(url, headers=get_dataforseo_auth(), json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        
        domain_metrics = {}
        if data.get("tasks"):
            for task_result in data["tasks"]:
                if task_result.get("status_code") == 20000:
                    if task_result.get("result") and len(task_result["result"]) > 0:
                        item = task_result["result"][0]
                        domain = item.get("target")
                        metrics = item.get("metrics", {})
                        organic = metrics.get("organic", {})
                        domain_metrics[domain] = {
                            "pos_1": organic.get("pos_1", 0),
                            "keywords": organic.get("count", 0),
                            "etv": organic.get("etv", 0),
                        }
        return domain_metrics
    except Exception as e:
        st.error(f"Domain metrics error: {str(e)}")
        return {}

def get_serp_results(keyword, your_domain="io.net"):
    """Fetch SERP results with domain metrics"""
    try:
        url = f"{DATAFORSEO_BASE_URL}/serp/google/organic/live/advanced"
        payload = [{
            "keyword": keyword,
            "location_code": 2840,
            "language_code": "en",
            "device": "desktop",
            "os": "windows",
            "depth": 10
        }]
        
        response = requests.post(url, headers=get_dataforseo_auth(), json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        if data.get("tasks") and len(data["tasks"]) > 0:
            task_result = data["tasks"][0]
            if task_result.get("result") and len(task_result["result"]) > 0:
                serp_items = task_result["result"][0].get("items", [])
                
                formatted_results = []
                competitor_domains = set()
                
                for item in serp_items[:10]:
                    if item.get("type") == "organic":
                        domain = item.get("domain")
                        formatted_results.append({
                            "position": item.get("rank_group"),
                            "title": item.get("title"),
                            "url": item.get("url"),
                            "domain": domain,
                            "description": item.get("description"),
                        })
                        if domain:
                            competitor_domains.add(domain)
                
                all_domains = list(competitor_domains)
                if your_domain not in all_domains:
                    all_domains.append(your_domain)
                
                domain_metrics = get_domain_metrics(all_domains)
                
                for result in formatted_results:
                    domain = result.get("domain")
                    if domain and domain in domain_metrics:
                        result["domain_metrics"] = domain_metrics[domain]
                
                return {
                    "keyword": keyword,
                    "total_results": len(formatted_results),
                    "results": formatted_results,
                    "domain_metrics": domain_metrics,
                    "your_domain": your_domain,
                    "your_domain_metrics": domain_metrics.get(your_domain, {})
                }
        return {"error": "No SERP results found"}
    except Exception as e:
        return {"error": str(e)}


# ============================================================================
# AUDIENCE & GOAL RECOMMENDATION FUNCTIONS
# ============================================================================

def analyze_competitor_audience_and_goals(serp_results, primary_keyword):
    """Analyze top 4 SERP results to recommend target audience and content goal"""
    if not serp_results.get("results"):
        return {
            "target_audience": "Technical Decision Makers",
            "content_goal": "Educational",
            "rationale": "Default values - no competitor data available"
        }
    
    top_4 = serp_results.get("results", [])[:4]
    competitor_data = [{
        "position": r.get("position"),
        "title": r.get("title"),
        "url": r.get("url"),
        "domain": r.get("domain"),
        "description": r.get("description")
    } for r in top_4]
    
    competitor_data_str = json.dumps(competitor_data, indent=2)
    
    prompt = f"""Analyze competitor content and recommend target audience and content goal.

PRIMARY KEYWORD: {primary_keyword}
TOP 4 COMPETITORS: {competitor_data_str}

Analyze each competitor's target audience, content goal, and content type. Then identify overserved/underserved audiences and dominant/missing content goals. Recommend a specific, underserved audience with buying power and a differentiated content goal.

OUTPUT JSON:
{{
  "competitor_analysis": [{{"position": 1, "domain": "...", "target_audience": "...", "content_goal": "...", "content_type": "..."}}],
  "patterns": {{"overserved_audiences": ["..."], "underserved_audiences": ["..."], "dominant_content_goals": ["..."], "missing_content_goals": ["..."]}},
  "recommendation": {{"target_audience": "...", "content_goal": "...", "rationale": "..."}}
}}"""

    try:
        client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        response = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        response_text = response.content[0].text.strip()
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        analysis = json.loads(response_text)
        recommendation = analysis.get("recommendation", {})
        
        return {
            "target_audience": recommendation.get("target_audience", "Technical Decision Makers"),
            "content_goal": recommendation.get("content_goal", "Educational"),
            "rationale": recommendation.get("rationale", ""),
            "full_analysis": analysis
        }
    except Exception as e:
        return {
            "target_audience": "Technical Decision Makers",
            "content_goal": "Educational",
            "rationale": f"Error: {str(e)}"
        }


def get_actual_word_count(url, timeout=10):
    """Fetch URL and count actual words in main content"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'form', 'iframe']):
            element.decompose()
        
        main_content = None
        for selector in ['article', 'main', '[role="main"]', '.content', '#content', '.post', '.entry-content']:
            main_content = soup.select_one(selector)
            if main_content:
                break
        
        if not main_content:
            main_content = soup.body
        
        if main_content:
            text = main_content.get_text(separator=' ', strip=True)
            words = text.split()
            return len([w for w in words if len(w) > 0])
        
        return None
    except:
        return None


def estimate_content_length(serp_results):
    """Fetch competitor pages and count actual word counts"""
    word_counts = []
    detailed_estimates = []
    
    for result in serp_results.get("results", [])[:4]:
        position = result.get("position", 999)
        title = result.get("title", "")
        url = result.get("url", "")
        domain = result.get("domain", "")
        
        actual_words = get_actual_word_count(url)
        
        if actual_words and actual_words > 100:
            word_count = actual_words
        else:
            word_count = 2000
        
        word_counts.append(word_count)
        detailed_estimates.append({
            "position": position,
            "domain": domain,
            "actual_words": word_count,
            "title": title[:60] + "..." if len(title) > 60 else title,
            "fetched": actual_words is not None
        })
    
    if word_counts:
        avg_words = sum(word_counts) / len(word_counts)
        sorted_counts = sorted(word_counts)
        median_words = sorted_counts[len(sorted_counts) // 2]
        min_words = min(word_counts)
        max_words = max(word_counts)
        recommended_min = int(avg_words * 1.1)
        recommended_max = int(avg_words * 1.2)
        
        return {
            "average": avg_words,
            "median": median_words,
            "min": min_words,
            "max": max_words,
            "recommended_min": recommended_min,
            "recommended_max": recommended_max,
            "detailed_estimates": detailed_estimates
        }
    else:
        return {
            "average": 3000,
            "median": 3000,
            "min": 1500,
            "max": 5000,
            "recommended_min": 3000,
            "recommended_max": 4000,
            "detailed_estimates": []
        }


def load_internal_pages(csv_path="io_net_pages.csv"):
    """Load io.net internal pages from CSV file"""
    pages = []
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                pages.append({
                    'category': row.get('Category', ''),
                    'title': row.get('Page Title', ''),
                    'url': row.get('URL', ''),
                    'description': row.get('Description', ''),
                    'keywords': row.get('Keywords', '')
                })
        return pages
    except:
        return []


def find_relevant_internal_links(primary_keyword, target_audience, content_goal, internal_pages, num_links=5):
    """Use Claude to find most relevant internal links"""
    if not internal_pages:
        return []
    
    pages_str = "\n".join([
        f"{i+1}. [{p['title']}]({p['url']}) - {p['description']} (Keywords: {p['keywords']})"
        for i, p in enumerate(internal_pages)
    ])
    
    prompt = f"""Select the {num_links} MOST RELEVANT pages to link to from an article about "{primary_keyword}" targeting {target_audience} for {content_goal}.

AVAILABLE PAGES:
{pages_str}

OUTPUT JSON:
[
  {{"title": "...", "url": "...", "anchor_text": "..."}}
]"""

    try:
        client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        response = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        response_text = response.content[0].text.strip()
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        return json.loads(response_text)
    except:
        return []


def calculate_competition_assessment(your_domain_metrics, competitor_metrics_dict, serp_results):
    """Calculate competition assessment with content length analysis"""
    # First, estimate content lengths
    content_length_analysis = estimate_content_length(serp_results)
    
    your_pos_1 = your_domain_metrics.get("pos_1", 0)
    your_etv = your_domain_metrics.get("etv", 0)
    your_keywords = your_domain_metrics.get("keywords", 0)
    
    competitor_analysis = []
    
    for result in serp_results.get("results", []):
        domain = result.get("domain")
        position = result.get("position", 999)
        
        if domain and domain in competitor_metrics_dict:
            metrics = competitor_metrics_dict[domain]
            comp_pos_1 = metrics.get("pos_1", 0)
            comp_etv = metrics.get("etv", 0)
            comp_keywords = metrics.get("keywords", 0)
            
            if your_pos_1 > 0:
                pos_1_ratio = comp_pos_1 / your_pos_1
            else:
                pos_1_ratio = comp_pos_1 / 100 if comp_pos_1 > 0 else 0
            
            if your_etv > 0:
                etv_ratio = comp_etv / your_etv
            else:
                etv_ratio = comp_etv / 10000 if comp_etv > 0 else 0
            
            if your_keywords > 0:
                keywords_ratio = comp_keywords / your_keywords
            else:
                keywords_ratio = comp_keywords / 5000 if comp_keywords > 0 else 0
            
            strength_score = min(100, (pos_1_ratio * 50) + (etv_ratio * 30) + (keywords_ratio * 20))
            
            if strength_score <= 30:
                difficulty = "WEAK"
            elif strength_score <= 60:
                difficulty = "MEDIUM"
            elif strength_score <= 85:
                difficulty = "STRONG"
            else:
                difficulty = "DOMINANT"
            
            competitor_analysis.append({
                "domain": domain,
                "position": position,
                "pos_1": comp_pos_1,
                "etv": comp_etv,
                "keywords": comp_keywords,
                "strength_score": round(strength_score, 1),
                "difficulty": difficulty
            })
    
    competitor_analysis.sort(key=lambda x: x["strength_score"])
    
    top_5 = competitor_analysis[:5] if len(competitor_analysis) >= 5 else competitor_analysis
    overall_score = sum(c["strength_score"] for c in top_5) / len(top_5) if top_5 else 0
    
    if overall_score <= 30:
        verdict = "LOW COMPETITION"
        target_position = "1-3"
    elif overall_score <= 60:
        verdict = "MEDIUM COMPETITION"
        target_position = "3-5"
    elif overall_score <= 85:
        verdict = "HIGH COMPETITION"
        target_position = "5-10"
    else:
        verdict = "VERY HIGH COMPETITION"
        target_position = "10-20 initially"
    
    recommendations = []
    if overall_score <= 30:
        recommendations = ["Focus on content quality", "Quick wins possible", "Build topical authority"]
    elif overall_score <= 60:
        recommendations = ["Create better content than top 10", "Build quality backlinks", "Focus on UX"]
    elif overall_score <= 85:
        recommendations = ["Develop pillar content", "Aggressive link building", "Build brand authority"]
    else:
        recommendations = ["Long-term strategy (6-12+ months)", "Build authority through easier wins first", "Focus on long-tail initially"]
    
    return {
        "your_metrics": {"pos_1": your_pos_1, "etv": your_etv, "keywords": your_keywords},
        "competitor_analysis": competitor_analysis,
        "overall_score": round(overall_score, 1),
        "verdict": verdict,
        "target_position": target_position,
        "recommendations": recommendations,
        "content_length_analysis": content_length_analysis
    }

def generate_content_brief(keyword_metrics, serp_results, primary_keyword, target_audience, content_goal, competition_assessment, internal_links=[], audience_goal_recommendation=None):
    """Generate content brief using Claude"""
    anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    # Extract content length recommendations
    content_length = competition_assessment.get('content_length_analysis', {})
    avg_words = content_length.get('average', 3000)
    min_words = content_length.get('min', 1500)
    max_words = content_length.get('max', 5000)
    recommended_min = content_length.get('recommended_min', 3000)
    recommended_max = content_length.get('recommended_max', 4000)
    
    keyword_data_str = json.dumps(keyword_metrics, indent=2)
    serp_data_str = json.dumps(serp_results, indent=2)
    competition_data_str = json.dumps(competition_assessment, indent=2)
    
    prompt = f"""You are an expert SEO content strategist. Generate a comprehensive SEO content brief.

PRIMARY KEYWORD: {primary_keyword}
TARGET AUDIENCE: {target_audience}
CONTENT GOAL: {content_goal}

KEYWORD METRICS: {keyword_data_str}
SERP DATA: {serp_data_str}
COMPETITION DATA: {competition_data_str}

Create a comprehensive SEO content brief in markdown with these sections:
1. Executive Summary
2. Keyword Strategy
3. Search Intent & Audience Analysis
4. SERP Competitive Analysis (use ACTUAL data from above)
5. Competition Domain Authority Analysis (use ACTUAL metrics)
6. Content Recommendations
7. SEO Optimization Guidelines
8. Competitive Differentiation Strategy
9. Content Goals & Success Metrics
10. Writing Guidelines
11. Research & Sources to Include"""
    
    message = anthropic_client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=8000,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return message.content[0].text

# Main App
st.markdown('<div class="main-header">📝 SEO Content Brief Generator</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Check API credentials
    api_status = st.empty()
    if os.getenv("ANTHROPIC_API_KEY"):
        api_status.success("✅ Anthropic API Key Found")
    else:
        api_status.error("❌ Anthropic API Key Missing")
    
    if os.getenv("DATAFORSEO_LOGIN") and os.getenv("DATAFORSEO_PASSWORD"):
        st.success("✅ DataForSEO Credentials Found")
    else:
        st.error("❌ DataForSEO Credentials Missing")
    
    st.markdown("---")
    st.markdown("### 📖 How to Use")
    st.markdown("""
    1. Enter your primary keyword
    2. Describe your target audience
    3. Define your content goal
    4. Enter your domain (optional)
    5. Click Generate Brief
    6. Download the result
    """)

# Main Content
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🎯 Brief Configuration")
    
    primary_keyword = st.text_input(
        "Primary Keyword",
        placeholder="e.g., gpu cluster for machine learning",
        help="The main keyword you want to rank for"
    )
    
    target_audience = st.text_input(
        "Target Audience",
        placeholder="e.g., AI/ML Startup CTOs",
        help="Who is this content for?"
    )
    
    content_goal = st.text_input(
        "Content Goal",
        placeholder="e.g., Educational + Demand Generation",
        help="What should this content achieve?"
    )
    
    your_domain = st.text_input(
        "Your Domain (Optional)",
        value="io.net",
        placeholder="e.g., yoursite.com",
        help="Your website domain for competition analysis"
    )

with col2:
    st.subheader("📊 Quick Stats")
    if st.session_state.keyword_metrics and 'error' not in st.session_state.keyword_metrics:
        st.metric("Search Volume", f"{st.session_state.keyword_metrics.get('search_volume', 'N/A'):,}")
        st.metric("Competition", st.session_state.keyword_metrics.get('competition', 'N/A'))
        st.metric("CPC", f"${st.session_state.keyword_metrics.get('cpc', 0):.2f}")
    else:
        st.info("Generate a brief to see stats")

# Generate Button
st.markdown("---")
if st.button("🚀 Generate SEO Brief", type="primary", use_container_width=True):
    if not primary_keyword or not target_audience or not content_goal:
        st.error("⚠️ Please fill in all required fields (keyword, audience, and goal)")
    else:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Step 1: Keyword Research
            status_text.text("📊 Step 1/4: Researching keyword metrics...")
            progress_bar.progress(25)
            keyword_metrics = get_keyword_metrics(primary_keyword)
            st.session_state.keyword_metrics = keyword_metrics
            
            if 'error' in keyword_metrics:
                st.error(f"Keyword research failed: {keyword_metrics['error']}")
                st.stop()
            
            # Step 2: SERP Analysis
            status_text.text("🔍 Step 2/4: Analyzing SERP results...")
            progress_bar.progress(50)
            serp_results = get_serp_results(primary_keyword, your_domain)
            st.session_state.serp_results = serp_results
            
            if 'error' in serp_results:
                st.error(f"SERP analysis failed: {serp_results['error']}")
                st.stop()
            
            # Step 3: Competition Assessment
            status_text.text("🎯 Step 3/4: Assessing competition...")
            progress_bar.progress(75)
            competition_assessment = calculate_competition_assessment(
                serp_results.get("your_domain_metrics", {}),
                serp_results.get("domain_metrics", {}),
                serp_results
            )
            st.session_state.competition_assessment = competition_assessment
            
            # Step 4: Generate Brief
            status_text.text("🤖 Step 4/4: Generating content brief with AI...")
            progress_bar.progress(90)
            brief_content = generate_content_brief(
                keyword_metrics,
                serp_results,
                primary_keyword,
                target_audience,
                content_goal,
                competition_assessment
            )
            
            progress_bar.progress(100)
            status_text.text("✅ Brief generated successfully!")
            
            st.session_state.brief_generated = True
            st.session_state.brief_content = brief_content
            
            st.balloons()
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            progress_bar.empty()
            status_text.empty()

# Display Results
if st.session_state.brief_generated:
    st.markdown("---")
    st.subheader("📄 Generated Content Brief")
    
    # Competition Summary
    if st.session_state.competition_assessment:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "Competition Score",
                f"{st.session_state.competition_assessment['overall_score']}/100"
            )
        with col2:
            st.metric(
                "Verdict",
                st.session_state.competition_assessment['verdict']
            )
        with col3:
            st.metric(
                "Target Position",
                st.session_state.competition_assessment['target_position']
            )
    
    # Brief Content
    st.markdown(st.session_state.brief_content)
    
    # Download Button
    safe_keyword = primary_keyword.lower().replace(" ", "-")
    filename = f"{safe_keyword}-brief.md"
    
    final_brief = f"""# SEO Content Brief: {primary_keyword}

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Target Audience:** {target_audience}
**Content Goal:** {content_goal}

---

{st.session_state.brief_content}

---

*Generated by SEO Brief Generator*
"""
    
    st.download_button(
        label="📥 Download Brief as Markdown",
        data=final_brief,
        file_name=filename,
        mime="text/markdown",
        use_container_width=True
    )
