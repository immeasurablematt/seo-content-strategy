"""
SEO Content Brief Generator using CrewAI

This script creates a comprehensive SEO content brief by:
1. Researching keywords and their metrics
2. Analyzing SERP (Search Engine Results Page) data
3. Analyzing competitor content
4. Gathering additional research sources
5. Synthesizing all data into a structured brief
6. Validating the output for quality

Author: SEO Content Team
"""

import os
import json
import base64
import requests
from datetime import datetime
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from crewai_tools import tool
from langchain_anthropic import ChatAnthropic

# ============================================================================
# ENVIRONMENT SETUP
# ============================================================================
# Load environment variables from .env file
# This keeps sensitive API keys out of the codebase
load_dotenv()

# Get API credentials from environment variables
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
DATAFORSEO_LOGIN = os.getenv("DATAFORSEO_LOGIN")
DATAFORSEO_PASSWORD = os.getenv("DATAFORSEO_PASSWORD")

# DataForSEO API endpoints
DATAFORSEO_BASE_URL = "https://api.dataforseo.com/v3"

# Initialize Claude LLM
# Using Claude Sonnet 4.5 for high-quality content generation
llm = ChatAnthropic(
    model="claude-sonnet-4-5-20250929",
    anthropic_api_key=ANTHROPIC_API_KEY
)

# ============================================================================
# DATAFORSEO API TOOLS
# ============================================================================
# These custom tools allow our agents to interact with DataForSEO's API
# We use the @tool decorator to make them available to CrewAI agents

def get_dataforseo_auth():
    """
    Creates Basic Authentication header for DataForSEO API
    
    Returns:
        dict: Headers with Authorization token
    """
    # Combine login:password and encode in base64 for Basic Auth
    credentials = f"{DATAFORSEO_LOGIN}:{DATAFORSEO_PASSWORD}"
    encoded = base64.b64encode(credentials.encode()).decode()
    return {
        "Authorization": f"Basic {encoded}",
        "Content-Type": "application/json"
    }


@tool("Get Keyword Search Volume and Metrics")
def get_keyword_metrics(keyword: str) -> str:
    """
    Fetches keyword search volume, competition, and related keywords from Google Ads API
    
    This tool queries DataForSEO's keywords_data endpoint to get:
    - Monthly search volume
    - Competition level
    - Cost-per-click (CPC) data
    - Related keywords and their metrics
    
    Args:
        keyword (str): The primary keyword to research
        
    Returns:
        str: JSON string containing keyword metrics or error message
    """
    try:
        # API endpoint for Google Ads keyword data
        url = f"{DATAFORSEO_BASE_URL}/keywords_data/google_ads/search_volume/live"
        
        # Prepare the API request payload
        # We're requesting data for US, English language
        payload = [{
            "keywords": [keyword],
            "location_code": 2840,  # United States
            "language_code": "en",   # English
            "search_partners": False,
            "include_adult_keywords": False
        }]
        
        # Make the API request with authentication
        response = requests.post(
            url,
            headers=get_dataforseo_auth(),
            json=payload,
            timeout=30
        )
        
        # Check if request was successful
        response.raise_for_status()
        
        data = response.json()
        
        # Extract relevant metrics from response
        if data.get("tasks") and len(data["tasks"]) > 0:
            task_result = data["tasks"][0]
            
            if task_result.get("result") and len(task_result["result"]) > 0:
                result_data = task_result["result"][0]
                
                # Format the response in a readable way
                formatted_result = {
                    "keyword": keyword,
                    "search_volume": result_data.get("search_volume"),
                    "competition": result_data.get("competition"),
                    "competition_index": result_data.get("competition_index"),
                    "low_top_of_page_bid": result_data.get("low_top_of_page_bid"),
                    "high_top_of_page_bid": result_data.get("high_top_of_page_bid"),
                    "cpc": result_data.get("cpc"),
                    "monthly_searches": result_data.get("monthly_searches", [])[:12]  # Last 12 months
                }
                
                return json.dumps(formatted_result, indent=2)
            else:
                return json.dumps({"error": "No results found for keyword"})
        else:
            return json.dumps({"error": "No tasks returned from API"})
            
    except requests.exceptions.RequestException as e:
        # Handle network/API errors gracefully
        return json.dumps({"error": f"API request failed: {str(e)}"})
    except Exception as e:
        # Handle any other unexpected errors
        return json.dumps({"error": f"Unexpected error: {str(e)}"})


@tool("Get SERP Results for Keyword")
def get_serp_results(keyword: str) -> str:
    """
    Fetches the top 10 organic search results from Google for a given keyword
    
    This tool provides detailed information about:
    - Page titles and descriptions
    - URLs and domains
    - Ranking positions
    - On-page SEO elements
    
    Args:
        keyword (str): The keyword to get SERP results for
        
    Returns:
        str: JSON string containing SERP analysis or error message
    """
    try:
        # API endpoint for live SERP data
        url = f"{DATAFORSEO_BASE_URL}/serp/google/organic/live/advanced"
        
        # Prepare the API request payload
        payload = [{
            "keyword": keyword,
            "location_code": 2840,  # United States
            "language_code": "en",   # English
            "device": "desktop",     # Desktop search results
            "os": "windows",
            "depth": 10              # Get top 10 results
        }]
        
        # Make the API request with authentication
        response = requests.post(
            url,
            headers=get_dataforseo_auth(),
            json=payload,
            timeout=30
        )
        
        # Check if request was successful
        response.raise_for_status()
        
        data = response.json()
        
        # Extract and format SERP results
        if data.get("tasks") and len(data["tasks"]) > 0:
            task_result = data["tasks"][0]
            
            if task_result.get("result") and len(task_result["result"]) > 0:
                serp_items = task_result["result"][0].get("items", [])
                
                # Extract key information from each result
                formatted_results = []
                for item in serp_items[:10]:  # Top 10 only
                    if item.get("type") == "organic":
                        formatted_results.append({
                            "position": item.get("rank_group"),
                            "title": item.get("title"),
                            "url": item.get("url"),
                            "domain": item.get("domain"),
                            "description": item.get("description"),
                            "breadcrumb": item.get("breadcrumb"),
                            "is_featured": item.get("is_featured", False),
                            "timestamp": item.get("timestamp")
                        })
                
                return json.dumps({
                    "keyword": keyword,
                    "total_results": len(formatted_results),
                    "results": formatted_results
                }, indent=2)
            else:
                return json.dumps({"error": "No SERP results found"})
        else:
            return json.dumps({"error": "No tasks returned from API"})
            
    except requests.exceptions.RequestException as e:
        # Handle network/API errors gracefully
        return json.dumps({"error": f"API request failed: {str(e)}"})
    except Exception as e:
        # Handle any other unexpected errors
        return json.dumps({"error": f"Unexpected error: {str(e)}"})


# ============================================================================
# AGENT DEFINITIONS
# ============================================================================
# Agents are autonomous units that perform specific tasks
# Each agent has a role, goal, backstory, and access to tools

# Agent 1: Keyword Researcher
# This agent focuses on understanding keyword metrics and search demand
keyword_researcher = Agent(
    role="Senior Keyword Research Specialist",
    goal="Analyze keyword metrics, search volume, competition, and identify related keyword opportunities for '{primary_keyword}'",
    backstory="""You are an expert SEO keyword researcher with 10+ years of experience.
    You excel at identifying high-value keywords, understanding search intent, and 
    finding keyword opportunities that competitors miss. You use data-driven insights
    to guide content strategy and always consider the business goals behind the keywords.
    You understand seasonal trends, competition levels, and how to balance search volume
    with ranking difficulty.""",
    tools=[get_keyword_metrics],  # This agent can call the keyword metrics tool
    verbose=True,  # Show detailed output
    allow_delegation=False,  # This agent works independently
    llm=llm  # Use Claude for this agent
)

# Agent 2: SERP Analyst
# This agent analyzes the competitive landscape in search results
serp_analyst = Agent(
    role="SERP Analysis Expert",
    goal="Analyze the top 10 Google search results for '{primary_keyword}' and identify patterns, content types, and ranking factors",
    backstory="""You are a SERP analysis specialist who understands Google's ranking algorithms
    and competitive dynamics. You can identify what makes top-ranking content successful by
    analyzing titles, meta descriptions, content structure, domain authority, and user intent
    alignment. You excel at finding patterns across multiple results and identifying gaps
    in competitor coverage that present opportunities for new content.""",
    tools=[get_serp_results],  # This agent can call the SERP results tool
    verbose=True,
    allow_delegation=False,
    llm=llm  # Use Claude for this agent
)

# Agent 3: Content Analyzer
# This agent performs deep analysis of competitor content
content_analyzer = Agent(
    role="Content Strategy Analyst",
    goal="Perform deep competitor content analysis to identify gaps, opportunities, and best practices for '{primary_keyword}'",
    backstory="""You are a content strategist with expertise in competitive analysis.
    You can read between the lines of competitor content to identify what's working,
    what's missing, and where opportunities exist. You understand content depth,
    topical coverage, user engagement signals, and how to create content that's
    better than anything currently ranking. You think about content from both
    SEO and user experience perspectives.""",
    verbose=True,
    allow_delegation=False,
    llm=llm  # Use Claude for this agent
    # This agent doesn't use external tools, but analyzes data from previous tasks
)

# Agent 4: Research Gatherer
# This agent gathers additional supporting research and data
research_gatherer = Agent(
    role="Research Intelligence Specialist",
    goal="Gather authoritative sources, statistics, case studies, and supporting research relevant to '{primary_keyword}' and '{target_audience}'",
    backstory="""You are a research specialist who excels at finding credible sources,
    recent statistics, industry reports, case studies, and expert opinions. You know
    how to identify authoritative sources that will make content more credible and
    valuable. You understand the target audience's information needs and can find
    data that resonates with them. You prioritize recent, relevant, and reputable
    sources.""",
    verbose=True,
    allow_delegation=False,
    llm=llm  # Use Claude for this agent
    # This agent works with general knowledge and context from other agents
)

# Agent 5: Brief Synthesizer
# This agent creates the final comprehensive content brief
brief_synthesizer = Agent(
    role="Senior Content Brief Architect",
    goal="Synthesize all research, SERP data, and competitive insights into a comprehensive, actionable content brief for '{primary_keyword}' targeting '{target_audience}' with goal '{content_goal}'",
    backstory="""You are a master content strategist who creates comprehensive content
    briefs that lead to top-ranking content. You excel at synthesizing complex research
    into clear, actionable guidance for writers. Your briefs include clear structure,
    key talking points, SEO recommendations, competitor insights, and tone guidance.
    You understand how to balance SEO requirements with user value and business goals.
    Your briefs are detailed enough to guide writers while leaving room for creativity.""",
    verbose=True,
    allow_delegation=False,
    llm=llm  # Use Claude for this agent
)

# Agent 6: QA Validator
# This agent validates the quality of the final brief
qa_validator = Agent(
    role="Content Quality Assurance Lead",
    goal="Validate the content brief for completeness, accuracy, SEO best practices, and alignment with '{content_goal}' and '{target_audience}' needs",
    backstory="""You are a meticulous QA specialist with expertise in both SEO and
    content quality. You have a keen eye for detail and ensure that content briefs
    meet the highest standards. You check for completeness, logical flow, SEO best
    practices, target audience alignment, and actionability. You identify gaps,
    inconsistencies, or areas that need strengthening. Your feedback is constructive
    and helps improve the final output.""",
    verbose=True,
    allow_delegation=False,
    llm=llm  # Use Claude for this agent
)

# ============================================================================
# TASK DEFINITIONS
# ============================================================================
# Tasks define specific work that agents need to complete
# Tasks can use context from previous tasks to build on each other

# Task 1: Keyword Research
# Get comprehensive keyword metrics and related opportunities
task1_keyword_research = Task(
    description="""Research the primary keyword '{primary_keyword}' and gather:
    
    1. Monthly search volume and trends over the last 12 months
    2. Competition level and competition index
    3. Cost-per-click (CPC) data and bid ranges
    4. Search intent analysis (informational, transactional, navigational)
    5. Seasonality patterns if any
    6. Recommendations for related keywords to target
    
    Use the keyword metrics tool to gather data and provide a comprehensive analysis.
    Consider the target audience: {target_audience}
    Consider the content goal: {content_goal}
    
    Your output should help guide the content strategy with data-driven insights.""",
    agent=keyword_researcher,
    expected_output="""A detailed keyword research report including:
    - Search volume and trend analysis
    - Competition assessment
    - CPC data and commercial intent indicators
    - Search intent classification
    - Related keyword opportunities
    - Strategic recommendations based on the data"""
)

# Task 2: SERP Analysis
# Analyze top-ranking content and identify patterns
task2_serp_analysis = Task(
    description="""Analyze the top 10 Google search results for '{primary_keyword}':
    
    1. Identify common content types (articles, guides, tools, product pages)
    2. Analyze title patterns and meta description approaches
    3. Note domain types ranking (authority sites, niche sites, forums)
    4. Identify common topics covered across top results
    5. Find content gaps - topics NOT covered by top results
    6. Analyze content depth and comprehensiveness
    7. Note any featured snippets or SERP features
    
    Use the SERP results tool and provide actionable insights for outranking competitors.
    Context from keyword research: {task1_keyword_research}""",
    agent=serp_analyst,
    expected_output="""A comprehensive SERP analysis report including:
    - Overview of top 10 results and their characteristics
    - Common patterns and success factors
    - Content type recommendations
    - Topic coverage analysis
    - Identified content gaps and opportunities
    - SERP feature opportunities (featured snippets, etc.)
    - Strategic recommendations for ranking"""
)

# Task 3: Competitor Content Analysis
# Deep dive into what makes competitor content successful
task3_content_analysis = Task(
    description="""Perform deep competitor content analysis for '{primary_keyword}':
    
    1. Identify the top 3-5 most comprehensive competitors from SERP results
    2. Analyze their content structure and organization
    3. List key topics and subtopics they cover
    4. Identify content strengths (what they do well)
    5. Identify content weaknesses and gaps (what they miss)
    6. Analyze content depth (word count, detail level, examples)
    7. Note use of multimedia (images, videos, infographics)
    8. Evaluate content quality and user value
    9. Identify opportunities to create superior content
    
    Use context from: 
    - Keyword research: {task1_keyword_research}
    - SERP analysis: {task2_serp_analysis}
    
    Target audience: {target_audience}
    Content goal: {content_goal}""",
    agent=content_analyzer,
    expected_output="""A detailed competitor content analysis including:
    - Top competitor profiles and their approaches
    - Content structure and organization patterns
    - Comprehensive topic and subtopic lists
    - Strengths and weaknesses analysis
    - Content depth assessment
    - Opportunities to create better content
    - Differentiation strategies"""
)

# Task 4: Research Gathering (ASYNC)
# Gather supporting research, stats, and sources in parallel
task4_research_gathering = Task(
    description="""Gather authoritative research and supporting materials for '{primary_keyword}':
    
    1. Identify 5-10 authoritative sources (industry reports, research papers, expert articles)
    2. Find recent statistics and data points (within last 2 years)
    3. Locate relevant case studies and real-world examples
    4. Identify expert opinions and thought leader perspectives
    5. Find supporting tools, resources, or frameworks to reference
    6. Consider what sources would be most credible to: {target_audience}
    
    Focus on sources that support the content goal: {content_goal}
    
    This task runs in parallel with other analysis to gather supporting materials.""",
    agent=research_gatherer,
    expected_output="""A curated research collection including:
    - 5-10 authoritative sources with URLs and key takeaways
    - Recent statistics and data points with sources
    - Relevant case studies and examples
    - Expert opinions and quotes
    - Recommended tools and resources to mention
    - Source credibility assessment""",
    async_execution=True  # This task runs in parallel/async
)

# Task 5: Brief Synthesis
# Create the final comprehensive content brief
task5_brief_synthesis = Task(
    description="""Create a comprehensive SEO content brief for '{primary_keyword}':
    
    Synthesize ALL previous research into a structured, actionable brief including:
    
    ## Brief Header
    - Primary keyword and target variations
    - Target audience: {target_audience}
    - Content goal: {content_goal}
    - Recommended word count
    - Content type recommendation
    
    ## Keyword Strategy
    - Primary keyword usage recommendations
    - Secondary keywords to include
    - Long-tail variations
    - Semantic keywords and related terms
    
    ## Audience & Intent
    - Target audience profile
    - User search intent
    - Key questions to answer
    - User journey stage
    
    ## SEO Requirements
    - Title tag recommendation (with character count)
    - Meta description recommendation
    - URL structure suggestion
    - Header (H1, H2, H3) structure
    - Internal linking opportunities
    - External linking requirements
    
    ## Content Structure & Outline
    - Recommended article structure
    - Detailed outline with H2 and H3 headings
    - Key points to cover in each section
    - Estimated word count per section
    
    ## Competitor Insights
    - What competitors do well
    - Content gaps to exploit
    - Differentiation strategy
    
    ## Research & Sources
    - Key statistics to include
    - Authoritative sources to cite
    - Case studies and examples
    
    ## Tone & Style Guidelines
    - Writing tone and voice
    - Technical depth level
    - Style recommendations
    
    ## Multimedia Requirements
    - Images needed
    - Video opportunities
    - Graphics/infographics suggestions
    
    ## Success Metrics
    - How to measure content success
    - KPIs to track
    
    Use context from:
    - {task1_keyword_research}
    - {task2_serp_analysis}
    - {task3_content_analysis}
    - {task4_research_gathering}""",
    agent=brief_synthesizer,
    expected_output="""A complete, publication-ready content brief in markdown format with all sections filled out in detail. The brief should be comprehensive enough that a writer can create excellent content from it without additional research."""
)

# Task 6: QA Validation
# Validate the brief for quality and completeness
task6_qa_validation = Task(
    description="""Perform quality assurance on the content brief:
    
    Validate the brief for:
    
    1. COMPLETENESS
       - All required sections present and filled out
       - Sufficient detail in each section
       - No placeholder text or TODO items
    
    2. ACCURACY
       - Keyword data correctly represented
       - SERP insights accurately reflect research
       - Sources are credible and relevant
    
    3. SEO BEST PRACTICES
       - Keyword targeting is appropriate
       - Title and meta recommendations follow best practices
       - Content structure supports SEO
       - Internal/external linking guidance included
    
    4. AUDIENCE ALIGNMENT
       - Brief aligns with target audience: {target_audience}
       - Content addresses audience needs and pain points
       - Tone and style appropriate for audience
    
    5. GOAL ALIGNMENT
       - Brief supports content goal: {content_goal}
       - Success metrics align with goal
       - Content type appropriate for goal
    
    6. ACTIONABILITY
       - Writer can execute from this brief
       - Clear, specific guidance provided
       - No ambiguity in requirements
    
    Review the brief: {task5_brief_synthesis}
    
    Provide a validation report with:
    - Pass/Fail for each category
    - Specific issues found
    - Recommendations for improvement
    - Overall quality score (1-10)
    - Final approval or revision needed
    
    If critical issues are found, flag them clearly.""",
    agent=qa_validator,
    expected_output="""A comprehensive QA validation report including:
    - Category-by-category assessment (Completeness, Accuracy, SEO, Audience, Goal, Actionability)
    - Pass/Fail status for each category
    - List of specific issues or gaps found
    - Recommendations for improvement
    - Overall quality score out of 10
    - Final recommendation: APPROVED or NEEDS REVISION (with specific revision requests)"""
)

# ============================================================================
# CREW CONFIGURATION
# ============================================================================
# The Crew orchestrates all agents and tasks in a coordinated workflow

seo_crew = Crew(
    agents=[
        keyword_researcher,
        serp_analyst,
        content_analyzer,
        research_gatherer,
        brief_synthesizer,
        qa_validator
    ],
    tasks=[
        task1_keyword_research,
        task2_serp_analysis,
        task3_content_analysis,
        task4_research_gathering,  # This runs async/parallel
        task5_brief_synthesis,
        task6_qa_validation
    ],
    process=Process.sequential,  # Tasks run in sequence (except task4 which is async)
    memory=True,  # Enable memory so agents can learn from previous interactions
    verbose=True,  # Show detailed output for debugging and monitoring
    full_output=True  # Return complete output including intermediate results
)

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("SEO CONTENT BRIEF GENERATOR")
    print("=" * 80)
    print()
    
    # ========================================================================
    # INPUT CONFIGURATION
    # ========================================================================
    # Define your content brief parameters here
    
    primary_keyword = "gpu cluster for machine learning"
    target_audience = "AI/ML Startup CTOs"
    content_goal = "Educational + Demand Generation"
    
    print(f"Primary Keyword: {primary_keyword}")
    print(f"Target Audience: {target_audience}")
    print(f"Content Goal: {content_goal}")
    print()
    print("=" * 80)
    print("Starting SEO Brief Generation Process...")
    print("=" * 80)
    print()
    
    # Validate environment variables
    if not ANTHROPIC_API_KEY:
        print("ERROR: ANTHROPIC_API_KEY not found in environment variables")
        print("Please create a .env file with your Anthropic API key")
        exit(1)
    
    if not DATAFORSEO_LOGIN or not DATAFORSEO_PASSWORD:
        print("WARNING: DataForSEO credentials not found")
        print("API tools may not work without proper credentials")
        print()
    
    try:
        # ====================================================================
        # RUN THE CREW
        # ====================================================================
        # The crew will execute all tasks in sequence
        # Task 4 (research gathering) will run asynchronously
        
        result = seo_crew.kickoff(inputs={
            "primary_keyword": primary_keyword,
            "target_audience": target_audience,
            "content_goal": content_goal
        })
        
        print()
        print("=" * 80)
        print("CREW EXECUTION COMPLETED")
        print("=" * 80)
        print()
        
        # ====================================================================
        # SAVE OUTPUT TO MARKDOWN FILE
        # ====================================================================
        # Create filename from keyword (replace spaces with hyphens)
        safe_keyword = primary_keyword.lower().replace(" ", "-")
        output_filename = f"{safe_keyword}-brief.md"
        
        # Prepare the final brief content
        brief_content = f"""# SEO Content Brief: {primary_keyword}

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Target Audience:** {target_audience}
**Content Goal:** {content_goal}

---

{result}

---

## Brief Metadata

- **Primary Keyword:** {primary_keyword}
- **Target Audience:** {target_audience}
- **Content Goal:** {content_goal}
- **Generated By:** SEO Crew AI
- **Generation Date:** {datetime.now().strftime("%Y-%m-%d")}

---

*This brief was generated using CrewAI with multiple specialized agents for keyword research, SERP analysis, content analysis, research gathering, brief synthesis, and quality assurance.*
"""
        
        # Write to file
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(brief_content)
        
        print(f"✅ Content brief saved to: {output_filename}")
        print()
        print("=" * 80)
        print("PROCESS COMPLETE")
        print("=" * 80)
        
    except Exception as e:
        print()
        print("=" * 80)
        print("ERROR DURING EXECUTION")
        print("=" * 80)
        print(f"An error occurred: {str(e)}")
        print()
        print("Please check:")
        print("1. Your API keys are correct in the .env file")
        print("2. You have internet connectivity")
        print("3. Your DataForSEO account has sufficient credits")
        print("4. All required packages are installed (pip install -r requirements.txt)")
        print()
        import traceback
        traceback.print_exc()

