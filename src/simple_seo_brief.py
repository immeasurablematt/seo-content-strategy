"""
Simple SEO Content Brief Generator (No CrewAI)

This script generates an SEO content brief by:
1. Calling DataForSEO API for keyword metrics
2. Calling DataForSEO API for SERP analysis
3. Using Claude (Anthropic) to synthesize insights into a comprehensive brief
4. Saving the final brief as a markdown file

No complex dependencies - just requests, anthropic, and dotenv.
"""

import os
import json
import base64
import requests
import csv
from datetime import datetime
from dotenv import load_dotenv
from anthropic import Anthropic

# ============================================================================
# ENVIRONMENT SETUP
# ============================================================================
load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
DATAFORSEO_LOGIN = os.getenv("DATAFORSEO_LOGIN")
DATAFORSEO_PASSWORD = os.getenv("DATAFORSEO_PASSWORD")

# DataForSEO API base URL
DATAFORSEO_BASE_URL = "https://api.dataforseo.com/v3"

# Initialize Anthropic client
anthropic_client = Anthropic(api_key=ANTHROPIC_API_KEY)

# ============================================================================
# DATAFORSEO API FUNCTIONS
# ============================================================================

def get_dataforseo_auth():
    """Create Basic Authentication header for DataForSEO API"""
    credentials = f"{DATAFORSEO_LOGIN}:{DATAFORSEO_PASSWORD}"
    encoded = base64.b64encode(credentials.encode()).decode()
    return {
        "Authorization": f"Basic {encoded}",
        "Content-Type": "application/json"
    }


def get_keyword_metrics(keyword):
    """
    Fetch keyword search volume and metrics from DataForSEO
    
    Args:
        keyword (str): The keyword to research
        
    Returns:
        dict: Keyword metrics data
    """
    print(f"\n📊 Fetching keyword metrics for: '{keyword}'...")
    
    try:
        url = f"{DATAFORSEO_BASE_URL}/keywords_data/google_ads/search_volume/live"
        
        payload = [{
            "keywords": [keyword],
            "location_code": 2840,  # United States
            "language_code": "en",
            "search_partners": False,
            "include_adult_keywords": False
        }]
        
        response = requests.post(
            url,
            headers=get_dataforseo_auth(),
            json=payload,
            timeout=30
        )
        
        response.raise_for_status()
        data = response.json()
        
        if data.get("tasks") and len(data["tasks"]) > 0:
            task_result = data["tasks"][0]
            
            if task_result.get("result") and len(task_result["result"]) > 0:
                result_data = task_result["result"][0]
                
                metrics = {
                    "keyword": keyword,
                    "search_volume": result_data.get("search_volume"),
                    "competition": result_data.get("competition"),
                    "competition_index": result_data.get("competition_index"),
                    "low_top_of_page_bid": result_data.get("low_top_of_page_bid"),
                    "high_top_of_page_bid": result_data.get("high_top_of_page_bid"),
                    "cpc": result_data.get("cpc"),
                    "monthly_searches": result_data.get("monthly_searches", [])[:12]
                }
                
                print(f"✅ Keyword metrics retrieved successfully")
                print(f"   - Search Volume: {metrics['search_volume']}")
                print(f"   - Competition: {metrics['competition']}")
                print(f"   - CPC: ${metrics['cpc']}")
                
                return metrics
            else:
                print("⚠️  No results found for keyword")
                return {"error": "No results found"}
        else:
            print("⚠️  No tasks returned from API")
            return {"error": "No tasks returned"}
            
    except requests.exceptions.RequestException as e:
        print(f"❌ API request failed: {str(e)}")
        return {"error": f"API request failed: {str(e)}"}
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return {"error": f"Unexpected error: {str(e)}"}


def get_domain_metrics(domains):
    """
    Fetch domain authority metrics from DataForSEO Labs API
    
    This function retrieves key domain metrics including:
    - pos_1: Number of keywords ranking in position 1
    - keywords: Total number of ranking keywords
    - etv: Estimated traffic value (monthly organic traffic value)
    - traffic_cost: Estimated cost if traffic was paid
    
    Args:
        domains (list): List of domain names to analyze
        
    Returns:
        dict: Domain metrics keyed by domain name
    """
    print(f"\n📈 Fetching domain authority metrics for {len(domains)} domains...")
    print(f"   - Domains: {', '.join(domains[:3])}{'...' if len(domains) > 3 else ''}")
    
    try:
        url = f"{DATAFORSEO_BASE_URL}/dataforseo_labs/google/domain_rank_overview/live"
        
        # Clean domains first
        clean_domains = []
        for domain in domains:
            # Clean domain: remove protocol, www., and paths
            clean = domain.replace('https://', '').replace('http://', '').replace('www.', '')
            clean = clean.split('/')[0]  # Remove any path
            if clean:
                clean_domains.append(clean)
        
        print(f"   - Cleaned targets: {clean_domains[:3]}{'...' if len(clean_domains) > 3 else ''}")
        
        domain_metrics = {}
        
        # Make separate API call for each domain (API limitation: one task at a time)
        for idx, clean_domain in enumerate(clean_domains):
            print(f"   - Fetching metrics for {clean_domain} ({idx+1}/{len(clean_domains)})...")
            
            payload = [{
                "target": clean_domain,
                "location_code": 2840,  # United States
                "language_code": "en"
            }]
            
            try:
                response = requests.post(
                    url,
                    headers=get_dataforseo_auth(),
                    json=payload,
                    timeout=30
                )
                
                response.raise_for_status()
                data = response.json()
                
                # Process the single task response
                if data.get("tasks") and len(data["tasks"]) > 0:
                    task_result = data["tasks"][0]
                    
                    # Check for task errors
                    if task_result.get("status_code") != 20000:
                        print(f"     ⚠️  API Error: {task_result.get('status_message', 'Unknown error')}")
                        continue
                    
                    # Extract domain metrics
                    if task_result.get("result") and len(task_result["result"]) > 0:
                        result_item = task_result["result"][0]
                        domain = result_item.get("target")
                        
                        # The actual metrics are in the 'items' array
                        if result_item.get("items") and len(result_item["items"]) > 0:
                            metrics_item = result_item["items"][0]
                            
                            # Debug: show full response for first domain
                            if idx == 0:
                                print(f"     [DEBUG] Metrics item keys: {list(metrics_item.keys())}")
                                print(f"     [DEBUG] Metrics item: {json.dumps(metrics_item, indent=2)[:800]}")
                            
                            if domain:
                                # Extract key domain authority indicators from metrics
                                metrics = metrics_item.get("metrics", {})
                                organic = metrics.get("organic", {})
                                
                                domain_metrics[domain] = {
                                    "pos_1": organic.get("pos_1", 0),
                                    "pos_2_3": organic.get("pos_2_3", 0),
                                    "pos_4_10": organic.get("pos_4_10", 0),
                                    "keywords": organic.get("count", 0),
                                    "etv": organic.get("etv", 0),
                                    "traffic_cost": organic.get("estimated_paid_traffic_cost", 0),
                                    "is_new": organic.get("is_new", 0),
                                    "is_up": organic.get("is_up", 0),
                                    "is_down": organic.get("is_down", 0)
                                }
                                
                                print(f"     ✓ pos_1: {domain_metrics[domain]['pos_1']:,}, keywords: {domain_metrics[domain]['keywords']:,}, etv: ${domain_metrics[domain]['etv']:,.0f}")
                        else:
                            print(f"     [DEBUG] No items data for {domain}")
                    else:
                        print(f"     [DEBUG] No result data for {clean_domain}")
                
            except requests.exceptions.RequestException as e:
                print(f"     ⚠️  Request failed for {clean_domain}: {str(e)}")
                continue
        
        if domain_metrics:
            print(f"✅ Domain metrics retrieved successfully")
            print(f"   - Analyzed {len(domain_metrics)} domains")
            return domain_metrics
        else:
            print("⚠️  No domain metrics found for any domain")
            return {}
            
    except requests.exceptions.RequestException as e:
        print(f"❌ API request failed: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   - Response text: {e.response.text[:500]}")
        return {}
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        import traceback
        print(f"   - Traceback: {traceback.format_exc()}")
        return {}


def get_serp_results(keyword, your_domain="io.net"):
    """
    Fetch top 10 organic search results from Google with domain authority analysis
    
    Args:
        keyword (str): The keyword to get SERP results for
        your_domain (str): Your domain to compare against competitors
        
    Returns:
        dict: SERP results data with domain metrics
    """
    print(f"\n🔍 Fetching SERP results for: '{keyword}'...")
    
    try:
        url = f"{DATAFORSEO_BASE_URL}/serp/google/organic/live/advanced"
        
        payload = [{
            "keyword": keyword,
            "location_code": 2840,  # United States
            "language_code": "en",
            "device": "desktop",
            "os": "windows",
            "depth": 10  # Top 10 results
        }]
        
        response = requests.post(
            url,
            headers=get_dataforseo_auth(),
            json=payload,
            timeout=30
        )
        
        response.raise_for_status()
        data = response.json()
        
        if data.get("tasks") and len(data["tasks"]) > 0:
            task_result = data["tasks"][0]
            
            if task_result.get("result") and len(task_result["result"]) > 0:
                serp_items = task_result["result"][0].get("items", [])
                
                formatted_results = []
                competitor_domains = set()
                
                # First pass: collect results and domains
                for item in serp_items[:10]:
                    if item.get("type") == "organic":
                        domain = item.get("domain")
                        formatted_results.append({
                            "position": item.get("rank_group"),
                            "title": item.get("title"),
                            "url": item.get("url"),
                            "domain": domain,
                            "description": item.get("description"),
                            "breadcrumb": item.get("breadcrumb"),
                        })
                        if domain:
                            competitor_domains.add(domain)
                
                # Add your domain for comparison
                all_domains = list(competitor_domains)
                if your_domain not in all_domains:
                    all_domains.append(your_domain)
                
                print(f"✅ SERP results retrieved successfully")
                print(f"   - Found {len(formatted_results)} organic results")
                
                # Get domain authority metrics for all domains
                domain_metrics = get_domain_metrics(all_domains)
                
                # Second pass: add domain metrics to each result
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
            else:
                print("⚠️  No SERP results found")
                return {"error": "No SERP results found"}
        else:
            print("⚠️  No tasks returned from API")
            return {"error": "No tasks returned"}
            
    except requests.exceptions.RequestException as e:
        print(f"❌ API request failed: {str(e)}")
        return {"error": f"API request failed: {str(e)}"}
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return {"error": f"Unexpected error: {str(e)}"}


# ============================================================================
# AUDIENCE & GOAL RECOMMENDATION FUNCTIONS
# ============================================================================

def analyze_competitor_audience_and_goals(serp_results, primary_keyword):
    """
    Analyze top 4 SERP results to identify their target audiences and content goals,
    then recommend a differentiated target audience and content goal for our content.
    
    Args:
        serp_results (dict): SERP data from get_serp_results()
        primary_keyword (str): The target keyword
        
    Returns:
        dict: Recommended target_audience, content_goal, and analysis
    """
    print(f"\n🎯 Analyzing competitor audiences and content goals...")
    
    if not serp_results.get("results"):
        print("⚠️  No SERP results to analyze")
        return {
            "target_audience": "Technical Decision Makers",
            "content_goal": "Educational",
            "rationale": "Default values - no competitor data available"
        }
    
    # Prepare competitor data for analysis (top 4 only)
    top_4 = serp_results.get("results", [])[:4]
    
    competitor_data = []
    for result in top_4:
        competitor_data.append({
            "position": result.get("position"),
            "title": result.get("title"),
            "url": result.get("url"),
            "domain": result.get("domain"),
            "description": result.get("description")
        })
    
    competitor_data_str = json.dumps(competitor_data, indent=2)
    
    # Create analysis prompt for Claude
    prompt = f"""You are an expert SEO strategist analyzing competitor content to recommend target audience and content goal.

PRIMARY KEYWORD: {primary_keyword}

TOP 4 RANKING COMPETITORS:
{competitor_data_str}

TASK 1: Analyze each competitor
For each of the top 4 results, identify:
1. **Target Audience** - Who is this content written for? (be specific about role, company size, experience level)
2. **Content Goal** - What is this content trying to achieve?
3. **Content Type** - What format/approach does it use?

TASK 2: Identify patterns and gaps
- What audiences are OVER-SERVED by current top content?
- What audiences are UNDER-SERVED or completely ignored?
- What content goals dominate the current SERP?
- What content goals are missing?

TASK 3: Recommend differentiated approach
Based on your analysis, recommend:
1. **Target Audience** - A specific, underserved audience with search intent and buying power
2. **Content Goal** - A content goal that fills a gap in the current SERP
3. **Rationale** - 2-3 sentences explaining why this combination will be effective

CRITICAL REQUIREMENTS:
- Be SPECIFIC with audience (not just "developers" but "Senior ML Engineers at Series A startups")
- Recommend an audience that has search intent for this keyword but isn't well-served
- The content goal should differentiate from competitors while matching search intent
- Consider commercial value - who has buying power and decision authority?

OUTPUT FORMAT (JSON only):
{{
  "competitor_analysis": [
    {{
      "position": 1,
      "domain": "...",
      "target_audience": "...",
      "content_goal": "...",
      "content_type": "..."
    }}
  ],
  "patterns": {{
    "overserved_audiences": ["...", "..."],
    "underserved_audiences": ["...", "..."],
    "dominant_content_goals": ["...", "..."],
    "missing_content_goals": ["...", "..."]
  }},
  "recommendation": {{
    "target_audience": "...",
    "content_goal": "...",
    "rationale": "..."
  }}
}}
"""

    try:
        response = anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        response_text = response.content[0].text.strip()
        
        # Extract JSON from response
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        analysis = json.loads(response_text)
        
        recommendation = analysis.get("recommendation", {})
        target_audience = recommendation.get("target_audience", "Technical Decision Makers")
        content_goal = recommendation.get("content_goal", "Educational")
        rationale = recommendation.get("rationale", "")
        
        print(f"✅ Audience & goal analysis complete")
        print(f"\n   📊 RECOMMENDED TARGET AUDIENCE:")
        print(f"   {target_audience}")
        print(f"\n   🎯 RECOMMENDED CONTENT GOAL:")
        print(f"   {content_goal}")
        print(f"\n   💡 RATIONALE:")
        print(f"   {rationale}")
        
        return {
            "target_audience": target_audience,
            "content_goal": content_goal,
            "rationale": rationale,
            "full_analysis": analysis
        }
        
    except Exception as e:
        print(f"⚠️  Error analyzing audiences: {str(e)}")
        return {
            "target_audience": "Technical Decision Makers",
            "content_goal": "Educational",
            "rationale": f"Error occurred, using defaults: {str(e)}"
        }


# ============================================================================
# COMPETITION ANALYSIS FUNCTIONS
# ============================================================================

def get_actual_word_count(url, timeout=10):
    """
    Fetch a URL and count the actual words in the main content
    
    Args:
        url (str): URL to fetch
        timeout (int): Request timeout in seconds
        
    Returns:
        int: Actual word count, or None if failed
    """
    try:
        from bs4 import BeautifulSoup
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script, style, nav, footer, header elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'form', 'iframe']):
            element.decompose()
        
        # Try to find main content area (common selectors)
        main_content = None
        for selector in ['article', 'main', '[role="main"]', '.content', '#content', '.post', '.entry-content']:
            main_content = soup.select_one(selector)
            if main_content:
                break
        
        # Fallback to body if no main content found
        if not main_content:
            main_content = soup.body
        
        if main_content:
            text = main_content.get_text(separator=' ', strip=True)
            words = text.split()
            word_count = len([w for w in words if len(w) > 0])
            return word_count
        
        return None
        
    except Exception as e:
        print(f"     ⚠️  Failed to fetch: {str(e)[:50]}")
        return None


def estimate_content_length(serp_results):
    """
    Fetch competitor pages and count actual word counts
    
    Analyzes only the top 4 results for efficiency and relevance.
    
    Args:
        serp_results (dict): SERP results with URLs
        
    Returns:
        dict: Word count analysis and statistics
    """
    print(f"\n📏 Fetching top 4 competitor pages and counting words...")
    
    word_counts = []
    detailed_estimates = []
    
    # Only analyze top 4 results
    for result in serp_results.get("results", [])[:4]:
        position = result.get("position", 999)
        title = result.get("title", "")
        url = result.get("url", "")
        domain = result.get("domain", "")
        
        print(f"   - Position #{position} ({domain})...")
        
        # Fetch and count actual words
        actual_words = get_actual_word_count(url)
        
        if actual_words and actual_words > 100:  # Sanity check
            word_count = actual_words
            print(f"     ✓ {word_count:,} words (actual)")
        else:
            # Fallback: reasonable default if fetch fails
            word_count = 2000
            print(f"     ⚠️  Using default: {word_count:,} words (fetch failed)")
        
        word_counts.append(word_count)
        detailed_estimates.append({
            "position": position,
            "domain": domain,
            "actual_words": word_count,
            "title": title[:60] + "..." if len(title) > 60 else title,
            "fetched": actual_words is not None
        })
        
    
    # Calculate statistics
    if word_counts:
        avg_words = sum(word_counts) / len(word_counts)
        sorted_counts = sorted(word_counts)
        median_words = sorted_counts[len(sorted_counts) // 2]
        min_words = min(word_counts)
        max_words = max(word_counts)
        
        # Recommend 10-20% more than average of top 4
        recommended_min = int(avg_words * 1.1)
        recommended_max = int(avg_words * 1.2)
        
        print(f"✅ Content length analysis complete (top 4 results)")
        print(f"   - Average: {avg_words:,.0f} words")
        print(f"   - Median: {median_words:,} words")
        print(f"   - Range: {min_words:,} - {max_words:,} words")
        print(f"   - Recommended: {recommended_min:,} - {recommended_max:,} words (10-20% above avg)")
        
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


def calculate_competition_assessment(your_domain_metrics, competitor_metrics_dict, serp_results):
    """
    Analyze competition strength and calculate competitiveness assessment
    
    This function compares your domain's authority against competitors using:
    - pos_1: Keywords ranking in position 1 (highest weight - shows dominance)
    - etv: Estimated traffic value (shows monetization and traffic)
    - keywords: Total ranking keywords (shows overall visibility)
    
    Competition Score Calculation:
    - Compare your metrics against each competitor
    - Score 0-100 where:
      * 0-30: Weak competitors - easier to outrank
      * 31-60: Medium competitors - requires good content
      * 61-85: Strong competitors - requires exceptional content + authority building
      * 86-100: Dominant competitors - very difficult to outrank directly
    
    Args:
        your_domain_metrics (dict): Your domain's authority metrics
        competitor_metrics_dict (dict): All competitor domain metrics
        serp_results (dict): SERP results with positioning
        
    Returns:
        dict: Competition assessment with scores and recommendations
    """
    print(f"\n🎯 Calculating competition assessment...")
    
    # First, estimate content lengths
    content_length_analysis = estimate_content_length(serp_results)
    
    # Extract your metrics
    your_pos_1 = your_domain_metrics.get("pos_1", 0)
    your_etv = your_domain_metrics.get("etv", 0)
    your_keywords = your_domain_metrics.get("keywords", 0)
    
    # Analyze each competitor
    competitor_analysis = []
    
    for result in serp_results.get("results", []):
        domain = result.get("domain")
        position = result.get("position", 999)
        
        if domain and domain in competitor_metrics_dict:
            metrics = competitor_metrics_dict[domain]
            
            comp_pos_1 = metrics.get("pos_1", 0)
            comp_etv = metrics.get("etv", 0)
            comp_keywords = metrics.get("keywords", 0)
            
            # Calculate strength score (0-100)
            # pos_1 is weighted heavily as it indicates domain authority
            # etv indicates traffic quality and monetization
            # keywords indicates overall visibility
            
            if your_pos_1 > 0:
                pos_1_ratio = comp_pos_1 / your_pos_1 if your_pos_1 > 0 else comp_pos_1
            else:
                # If your domain has no pos_1 rankings, any competitor with rankings is stronger
                pos_1_ratio = comp_pos_1 / 100 if comp_pos_1 > 0 else 0
            
            if your_etv > 0:
                etv_ratio = comp_etv / your_etv if your_etv > 0 else comp_etv / 1000
            else:
                etv_ratio = comp_etv / 10000 if comp_etv > 0 else 0
            
            if your_keywords > 0:
                keywords_ratio = comp_keywords / your_keywords if your_keywords > 0 else comp_keywords / 1000
            else:
                keywords_ratio = comp_keywords / 5000 if comp_keywords > 0 else 0
            
            # Weighted score calculation
            # pos_1 = 50% weight (most important for authority)
            # etv = 30% weight (traffic value)
            # keywords = 20% weight (overall visibility)
            strength_score = min(100, (
                (pos_1_ratio * 50) +
                (etv_ratio * 30) +
                (keywords_ratio * 20)
            ))
            
            # Determine difficulty level
            if strength_score <= 30:
                difficulty = "WEAK - Easy to outrank"
            elif strength_score <= 60:
                difficulty = "MEDIUM - Moderate effort needed"
            elif strength_score <= 85:
                difficulty = "STRONG - Significant effort required"
            else:
                difficulty = "DOMINANT - Very difficult to outrank"
            
            competitor_analysis.append({
                "domain": domain,
                "position": position,
                "pos_1": comp_pos_1,
                "etv": comp_etv,
                "keywords": comp_keywords,
                "strength_score": round(strength_score, 1),
                "difficulty": difficulty
            })
    
    # Sort by strength score
    competitor_analysis.sort(key=lambda x: x["strength_score"])
    
    # Calculate overall competition score (average of top 5)
    top_5 = competitor_analysis[:5] if len(competitor_analysis) >= 5 else competitor_analysis
    overall_score = sum(c["strength_score"] for c in top_5) / len(top_5) if top_5 else 0
    
    # Determine overall verdict
    if overall_score <= 30:
        verdict = "LOW COMPETITION - Excellent opportunity"
        target_position = "1-3"
    elif overall_score <= 60:
        verdict = "MEDIUM COMPETITION - Good opportunity with quality content"
        target_position = "3-5"
    elif overall_score <= 85:
        verdict = "HIGH COMPETITION - Requires exceptional content and link building"
        target_position = "5-10"
    else:
        verdict = "VERY HIGH COMPETITION - Long-term strategy needed"
        target_position = "10-20 initially"
    
    # Generate strategic recommendations
    recommendations = []
    
    if overall_score <= 30:
        recommendations.append("Focus on content quality - competitors are weak")
        recommendations.append("Quick wins possible with on-page optimization")
        recommendations.append("Build topical authority in this niche")
    elif overall_score <= 60:
        recommendations.append("Create significantly better content than current top 10")
        recommendations.append("Build high-quality backlinks from relevant sites")
        recommendations.append("Focus on user experience and engagement metrics")
    elif overall_score <= 85:
        recommendations.append("Develop comprehensive pillar content")
        recommendations.append("Aggressive link building campaign required")
        recommendations.append("Build brand authority and E-E-A-T signals")
        recommendations.append("Consider targeting easier related keywords first")
    else:
        recommendations.append("Long-term strategy needed (6-12+ months)")
        recommendations.append("Build domain authority through easier wins first")
        recommendations.append("Focus on long-tail variations initially")
        recommendations.append("Invest heavily in content quality and backlinks")
    
    # Identify easiest competitors to beat
    easiest_targets = [c for c in competitor_analysis if c["strength_score"] <= 40]
    if easiest_targets:
        recommendations.append(f"Target to outrank first: {', '.join([c['domain'] for c in easiest_targets[:3]])}")
    
    print(f"✅ Competition assessment completed")
    print(f"   - Overall Score: {round(overall_score, 1)}/100")
    print(f"   - Verdict: {verdict}")
    
    return {
        "your_metrics": {
            "pos_1": your_pos_1,
            "etv": your_etv,
            "keywords": your_keywords
        },
        "competitor_analysis": competitor_analysis,
        "overall_score": round(overall_score, 1),
        "verdict": verdict,
        "target_position": target_position,
        "recommendations": recommendations,
        "content_length_analysis": content_length_analysis
    }


# ============================================================================
# INTERNAL LINKING FUNCTIONS
# ============================================================================

def load_internal_pages(csv_path="io_net_pages.csv"):
    """
    Load io.net internal pages from CSV file
    
    Args:
        csv_path (str): Path to CSV file with internal pages
        
    Returns:
        list: List of dicts with page information
    """
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
        
        print(f"✅ Loaded {len(pages)} internal pages from {csv_path}")
        return pages
        
    except FileNotFoundError:
        print(f"⚠️  CSV file not found: {csv_path}")
        return []
    except Exception as e:
        print(f"⚠️  Error loading CSV: {str(e)}")
        return []


def find_relevant_internal_links(primary_keyword, target_audience, content_goal, internal_pages, num_links=5):
    """
    Use Claude to find the most relevant internal links for the content brief
    
    Args:
        primary_keyword (str): The target keyword for the brief
        target_audience (str): Target audience
        content_goal (str): Content goal
        internal_pages (list): List of available internal pages
        num_links (int): Number of links to recommend
        
    Returns:
        list: Recommended internal links with anchor text suggestions
    """
    print(f"\n🔗 Finding relevant internal links for '{primary_keyword}'...")
    
    if not internal_pages:
        return []
    
    # Prepare pages data for Claude
    pages_str = "\n".join([
        f"{i+1}. [{p['title']}]({p['url']}) - {p['description']} (Keywords: {p['keywords']})"
        for i, p in enumerate(internal_pages)
    ])
    
    prompt = f"""You are an SEO expert analyzing internal linking opportunities.

PRIMARY KEYWORD: {primary_keyword}
TARGET AUDIENCE: {target_audience}
CONTENT GOAL: {content_goal}

AVAILABLE INTERNAL PAGES:
{pages_str}

Task: Select the {num_links} MOST RELEVANT pages from the list above to internally link to from an article about "{primary_keyword}".

For each selected page, provide:
1. The page title and URL (exactly as shown above)
2. Suggested anchor text (natural, contextual, includes relevant keywords)

Return ONLY a JSON array in this exact format:
[
  {{
    "title": "Page Title",
    "url": "https://io.net/...",
    "anchor_text": "suggested anchor text"
  }}
]

Select pages that:
- Are highly relevant to the topic
- Add value for the target audience
- Support the content goal
- Have natural link placement opportunities
"""

    try:
        response = anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        response_text = response.content[0].text.strip()
        
        # Extract JSON from response (might have markdown code blocks)
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        links = json.loads(response_text)
        
        print(f"✅ Found {len(links)} relevant internal links")
        for link in links:
            print(f"   - {link['title']}")
        
        return links
        
    except Exception as e:
        print(f"⚠️  Error finding internal links: {str(e)}")
        return []


# ============================================================================
# CLAUDE AI FUNCTIONS
# ============================================================================

def generate_content_brief(keyword_metrics, serp_results, primary_keyword, target_audience, content_goal, competition_assessment, internal_links):
    """
    Use Claude to generate a comprehensive SEO content brief
    
    Args:
        keyword_metrics (dict): Keyword data from DataForSEO
        serp_results (dict): SERP data from DataForSEO
        primary_keyword (str): The target keyword
        target_audience (str): Target audience description
        content_goal (str): Content goal/purpose
        
    Returns:
        str: Generated content brief in markdown format
    """
    print(f"\n🤖 Generating content brief with Claude AI...")
    
    # Prepare the data for Claude
    keyword_data_str = json.dumps(keyword_metrics, indent=2)
    serp_data_str = json.dumps(serp_results, indent=2)
    competition_data_str = json.dumps(competition_assessment, indent=2)
    internal_links_str = json.dumps(internal_links, indent=2)
    
    # Extract content length recommendations
    content_length = competition_assessment.get('content_length_analysis', {})
    avg_words = content_length.get('average', 3000)
    min_words = content_length.get('min', 1500)
    max_words = content_length.get('max', 5000)
    recommended_min = content_length.get('recommended_min', 3000)
    recommended_max = content_length.get('recommended_max', 4000)
    
    # Create the prompt for Claude
    prompt = f"""You are an expert SEO content strategist. Generate a strategically focused SEO content brief.

PRIMARY KEYWORD: {primary_keyword}
TARGET AUDIENCE: {target_audience}
CONTENT GOAL: {content_goal}

KEYWORD METRICS DATA:
{keyword_data_str}

SERP ANALYSIS DATA (Top 4 Results):
{serp_data_str}

COMPETITION DOMAIN AUTHORITY ANALYSIS:
{competition_data_str}

COMPETITOR CONTENT LENGTH ANALYSIS:
- Average: {avg_words:.0f} words | Range: {min_words:.0f}-{max_words:.0f}
- Recommended: {recommended_min:.0f}-{recommended_max:.0f} words (10-20% above top competitors)

RECOMMENDED INTERNAL LINKS:
{internal_links_str}

**CRITICAL INSTRUCTIONS:**

1. PRESERVE ALL STRATEGIC SEO ELEMENTS:
   - Detailed SERP analysis with URLs, strengths, gaps for top 4 results
   - Complete H2/H3 structure outline (show subsections)
   - Keyword placement strategy (where to use primary keyword)
   - External linking requirements (specific source types)
   - Content quality signals (E-E-A-T, expertise requirements)
   - Strategic recommendations from competition data
   - Prioritized competitor targets with rationale
   - Call-to-Action strategy (primary, secondary, soft CTAs)
   - Semantic keywords list
   - Unique value propositions (specific, not generic)

2. FORMAT FOR EFFICIENCY (not cutting substance):
   - Use tables for SERP comparison and domain metrics
   - Use structured data format for keyword/audience section
   - Use bullets for lists
   - Keep explanations concise but complete

3. REMOVE ONLY:
   - Generic writing advice ("use professional tone", "clear formatting")
   - Redundant explanations of the same point
   - Meta-commentary about the brief

4. USE ACTUAL DATA:
   - Top 4 SERP results with specific URLs, content types, strengths, gaps
   - Domain metrics in tables with real numbers
   - Strategic recommendations from competition_data
   - Internal links exactly as provided
   - Word count with rationale based on competition verdict

**WRITING PROCESS:** Complete sections 2-7 first, THEN write Section 1 (Executive Summary) to summarize the article you just briefed.

Output format:

# SEO Content Brief: {primary_keyword}

## 1. Executive Summary
[Write this LAST after completing sections 2-7. Max 150 words. Summarize: the unique article approach, key differentiators from competitors, main topics covered, and why this content will succeed in ranking and engaging {target_audience}. Remove this instruction in final output.]

## 2. Keyword & Audience Intelligence
**Target: 250-300 words. Use structured data format with bullets. MUST include all keyword metrics, monthly trends, semantic keywords, detailed audience profile, intent breakdown, key questions, pain points.**

**Primary Target:**
- Keyword: {primary_keyword}
- Volume: [use actual from data]/mo | CPC: $[actual] | Competition: [level] ([score]/100)
- Trend: [seasonal pattern from monthly_searches with interpretation - e.g., "Peak in April (590), steady 390-480, indicates budget planning cycles"]

**Audience:** {target_audience}
- Budget Authority: $[estimated range] infrastructure decisions
- Primary Intent: [X]% Commercial Investigation / [Y]% Informational / [Z]% Other
- Key Question: "[what they're trying to solve in their words]"
- Pain Points: [2-3 specific pain points from their perspective]

**Secondary Keywords:** [comma-separated list of 5-7 keywords]

**Long-tail Opportunities:** [comma-separated list of 6-8 long-tail variations]

**Semantic Keywords:** [comma-separated list for NLP/topic coverage - related terms Google associates]

## 3. Internal Linking Strategy
**Target: 100-150 words. Table format. Convert the RECOMMENDED INTERNAL LINKS JSON data into a markdown table with the following columns: Page Title, URL, Suggested Anchor Text. Include ALL links from the data.**

| Page Title | URL | Suggested Anchor Text |
|------------|-----|----------------------|
| [from data] | [from data] | [from data] |

## 4. Competitive Landscape  
**Target: 500-600 words. CRITICAL: Analyze top 4 SERP results in detail with full URLs, content types, strengths, gaps. Include domain authority table, strategic recommendations (4-5 bullets), and prioritized target list (3 competitors with rationale).**

**SERP Analysis (Top 4):**

**Position #1: "[Exact Title]" - [domain]**
- **Full URL:** [complete URL from data]
- **Content Type:** [article/guide/tool/directory/product page]
- **Focus:** [what page primarily covers]
- **Strengths:** [what they do well]
- **Gaps:** [what they're missing]

[Repeat format for positions 2, 3, and 4]

**Common Topics Across Top Results:**
- [topic 1]
- [topic 2]
- [topic 3]

**Content Gap Opportunities:**
- [specific gap 1 with brief explanation why this is an opportunity]
- [specific gap 2 with brief explanation]
- [specific gap 3 with brief explanation]

**Domain Authority Comparison:**

**Your Domain Baseline (io.net):**
- Pos#1 Keywords: [actual] | Total Keywords: [actual] | ETV: $[actual]

**Competitor Domain Authority:**

| Domain | Position | Pos#1 KW | Total KW | ETV | Strength Score | Difficulty |
|--------|----------|----------|----------|-----|----------------|------------|
[Use ACTUAL domain metrics from competition data - include all competitors]

**Competition Assessment:**
- **Overall Score:** [actual]/100
- **Verdict:** [actual verdict from data]
- **Target Position:** [actual target position from data]

**Strategic Recommendations:**
[List all 4-5 recommendations from competition_data exactly as provided]

**Prioritized Outranking Targets:**
1. **[domain]** - [specific rationale why easiest based on domain metrics]
2. **[domain]** - [specific rationale for secondary target]
3. **[domain]** - [specific rationale for tertiary target]

## 5. Content Strategy & Differentiation
**Target: 600-700 words. MUST include complete H2/H3 outline, keyword placement strategy, external source requirements, content quality signals, unique elements, and CTA strategy. Be specific, not generic.**

**Content Type:** [guide/article/listicle/comparison - based on gap analysis]

**Recommended Title & Meta:**
- **H1:** [60 chars max, include {primary_keyword}] (include actual char count)
- **Meta Title:** [60 chars, keyword prominent] (include char count)
- **Meta Description:** [155 chars, compelling, include keyword] (include char count)
- **URL Structure:** [suggested-url-path]

**Article Structure (H2 and H3 Outline):**

**H2:** [Section 1 Title]
- H3: [Subsection]
- H3: [Subsection]
- H3: [Subsection]

**H2:** [Section 2 Title]
- H3: [Subsection]
- H3: [Subsection]

[Continue for 6-8 major H2 sections with H3 subsections]

**Target Length:** {recommended_min:.0f}-{recommended_max:.0f} words

**Rationale:** Competitor analysis shows top 4 average {avg_words:.0f} words (range: {min_words:.0f}-{max_words:.0f}). This recommendation is 10-20% above average to ensure comprehensive coverage. Explain why this specific length is appropriate given the competition verdict and topic complexity.

**Keyword Placement Strategy:**
- **H1:** Include primary keyword exactly
- **First 100 words:** Use primary keyword once naturally
- **H2 Headers:** Include keyword variations in [specific number] section headers
- **URL:** Include primary keyword hyphenated
- **Meta Elements:** Primary keyword prominent in both title and description
- **Throughout Content:** Integrate semantic keywords naturally for topical relevance
- **Density:** Target appropriate percentage for primary keyword (natural, not forced)

**Key Topics to Cover:**

*Must-Have Topics (from SERP analysis):*
- [topic 1 from competitors]
- [topic 2 from competitors]
- [topic 3 from competitors]
- [additional must-have topics]

*Differentiating Topics (content gaps):*
- [unique topic 1]: [brief explanation why this is a differentiator]
- [unique topic 2]: [brief explanation]
- [unique topic 3]: [brief explanation]
- [additional differentiating topics]

**Required External Sources:**
- [Source category]: [specific examples - e.g., "Industry reports: Gartner, IDC, McKinsey GPU market analysis"]
- [Source category]: [specific examples]
- [Source category]: [specific examples]
- [Source category]: [specific examples]

**Content Quality Signals:**
- [Specific requirement]: [what to include - e.g., "Include actual performance benchmarks with specific numbers"]
- [Specific requirement]: [what to include]
- [Specific requirement]: [what to include]
- Technical depth level: [appropriate level for {target_audience}]
- E-E-A-T: [specific expertise signals to demonstrate]

**Unique Content Elements (Must Include):**
- [Specific unique element 1]: [what this is and why it's unique]
- [Specific unique element 2]: [what this is]
- [Specific unique element 3]: [what this is]

**Multimedia Requirements:**
- [Type]: [specific purpose - e.g., "Comparison table: top 5 providers with pricing, GPU specs, performance"]
- [Type]: [specific purpose]
- [Type]: [specific purpose]

**Call-to-Action Strategy:**
- **Primary CTA:** "[specific CTA text]" → [placement location and destination]
- **Secondary CTA:** "[specific CTA text]" → [placement location and destination]
- **Soft CTA:** "[specific CTA text]" → [placement location and destination]

**Unique Value Propositions vs. Competitors:**
- [Specific differentiator 1 based on gap analysis]
- [Specific differentiator 2]
- [Specific differentiator 3]
- [Specific differentiator 4]

---

**FINAL STEP:** Go back to Section 1 (Executive Summary) and write a compelling 150-word summary of the article you just outlined. Focus on the unique approach, key differentiators, main topics, and why this will succeed.

---"""

    try:
        # Call Claude API
        message = anthropic_client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=16000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        # Extract the response
        brief_content = message.content[0].text
        
        print(f"✅ Content brief generated successfully")
        print(f"   - Length: {len(brief_content)} characters")
        
        return brief_content
        
    except Exception as e:
        print(f"❌ Error generating brief with Claude: {str(e)}")
        return f"Error generating brief: {str(e)}"


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function"""
    
    print("=" * 80)
    print("SEO CONTENT BRIEF GENERATOR")
    print("(Simple Version - No CrewAI)")
    print("=" * 80)
    
    # ========================================================================
    # CONFIGURATION - MODIFY PRIMARY KEYWORD ONLY
    # ========================================================================
    primary_keyword = "high performance computing"
    
    print(f"\n📋 Configuration:")
    print(f"   Primary Keyword: {primary_keyword}")
    print(f"   Target Audience: [Auto-recommended based on competitor analysis]")
    print(f"   Content Goal: [Auto-recommended based on competitor analysis]")
    
    # Validate environment variables
    if not ANTHROPIC_API_KEY:
        print("\n❌ ERROR: ANTHROPIC_API_KEY not found in .env file")
        return
    
    if not DATAFORSEO_LOGIN or not DATAFORSEO_PASSWORD:
        print("\n⚠️  WARNING: DataForSEO credentials not found in .env file")
        print("   API calls will fail without proper credentials")
    
    print("\n" + "=" * 80)
    print("STEP 1: KEYWORD RESEARCH")
    print("=" * 80)
    
    # Step 1: Get keyword metrics
    keyword_metrics = get_keyword_metrics(primary_keyword)
    
    print("\n" + "=" * 80)
    print("STEP 2: SERP ANALYSIS & DOMAIN AUTHORITY")
    print("=" * 80)
    
    # Step 2: Get SERP results with domain metrics
    serp_results = get_serp_results(primary_keyword, your_domain="io.net")
    
    print("\n" + "=" * 80)
    print("STEP 3: AUDIENCE & GOAL RECOMMENDATION")
    print("=" * 80)
    
    # Step 3: Analyze competitors and recommend target audience and content goal
    audience_goal_recommendation = analyze_competitor_audience_and_goals(
        serp_results,
        primary_keyword
    )
    
    target_audience = audience_goal_recommendation.get("target_audience")
    content_goal = audience_goal_recommendation.get("content_goal")
    
    print("\n" + "=" * 80)
    print("STEP 4: COMPETITION ASSESSMENT")
    print("=" * 80)
    
    # Step 4: Calculate competition assessment
    your_domain_metrics = serp_results.get("your_domain_metrics", {})
    domain_metrics = serp_results.get("domain_metrics", {})
    
    competition_assessment = calculate_competition_assessment(
        your_domain_metrics,
        domain_metrics,
        serp_results
    )
    
    print("\n" + "=" * 80)
    print("STEP 5: INTERNAL LINKING ANALYSIS")
    print("=" * 80)
    
    # Step 5: Load internal pages and find relevant links
    # Try the actual CSV file first, fallback to template
    if os.path.exists("Internal-Links-Oct-10- 2025.csv"):
        internal_pages = load_internal_pages("Internal-Links-Oct-10- 2025.csv")
    else:
        internal_pages = load_internal_pages("io_net_pages.csv")
    
    if internal_pages:
        internal_links = find_relevant_internal_links(
            primary_keyword,
            target_audience,
            content_goal,
            internal_pages,
            num_links=5
        )
    else:
        print("⚠️  No internal pages loaded - skipping internal link recommendations")
        internal_links = []
    
    print("\n" + "=" * 80)
    print("STEP 6: GENERATE CONTENT BRIEF")
    print("=" * 80)
    
    # Step 6: Generate content brief with Claude
    content_brief = generate_content_brief(
        keyword_metrics,
        serp_results,
        primary_keyword,
        target_audience,
        content_goal,
        competition_assessment,
        internal_links
    )
    
    print("\n" + "=" * 80)
    print("STEP 7: SAVE BRIEF TO FILE")
    print("=" * 80)
    
    # Step 7: Save to markdown file
    safe_keyword = primary_keyword.lower().replace(" ", "-")
    output_filename = f"{safe_keyword}-brief.md"
    
    # Extract word count from competition assessment
    content_length_data = competition_assessment.get('content_length_analysis', {})
    recommended_min = content_length_data.get('recommended_min', 0)
    recommended_max = content_length_data.get('recommended_max', 0)
    
    # Add metadata header to the brief
    rationale = audience_goal_recommendation.get('rationale', 'Based on competitive analysis')
    
    final_brief = f"""# SEO Content Brief: {primary_keyword}

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Target Audience:** {target_audience}  
**Content Goal:** {content_goal}  
**Primary Keyword:** {primary_keyword}  
**Target Length:** {recommended_min:.0f}-{recommended_max:.0f} words

**Audience & Goal Rationale:**  
_{rationale}_

---

{content_brief}

---

## Brief Metadata

### Keyword Metrics
- **Primary Keyword:** {primary_keyword}
- **Search Volume:** {keyword_metrics.get('search_volume', 'N/A')}
- **Competition:** {keyword_metrics.get('competition', 'N/A')}
- **CPC:** ${keyword_metrics.get('cpc', 'N/A')}

### Domain Authority Metrics
- **Your Domain (io.net):**
  - Pos #1 Keywords: {your_domain_metrics.get('pos_1', 'N/A')}
  - Total Keywords: {your_domain_metrics.get('keywords', 'N/A')}
  - Estimated Traffic Value: ${your_domain_metrics.get('etv', 0):,.0f} (monthly)
  
### Competition Analysis
- **SERP Results Analyzed:** {serp_results.get('total_results', 'N/A')}
- **Competitor Domains Analyzed:** {len(domain_metrics) - 1 if domain_metrics else 0}
- **Overall Competition Score:** {competition_assessment.get('overall_score', 'N/A')}/100
- **Competition Verdict:** {competition_assessment.get('verdict', 'N/A')}
- **Target Ranking Position:** {competition_assessment.get('target_position', 'N/A')}

### Generation Details
- **Generated By:** Claude AI (Anthropic) + DataForSEO
- **Generation Date:** {datetime.now().strftime("%Y-%m-%d")}
- **Analysis Includes:** Keyword Research, SERP Analysis, Domain Authority Comparison, Competition Assessment

---

*This brief was generated using DataForSEO API for keyword data, SERP analysis, and domain authority metrics, combined with Claude AI for strategic analysis and synthesis.*
"""
    
    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(final_brief)
        
        print(f"\n✅ Content brief saved successfully!")
        print(f"   📄 File: {output_filename}")
        print(f"   📏 Size: {len(final_brief)} characters")
        
    except Exception as e:
        print(f"\n❌ Error saving file: {str(e)}")
    
    print("\n" + "=" * 80)
    print("PROCESS COMPLETE")
    print("=" * 80)
    print(f"\n🎉 Your SEO content brief is ready: {output_filename}\n")


if __name__ == "__main__":
    main()

