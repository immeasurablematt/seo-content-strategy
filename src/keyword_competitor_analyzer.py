"""
Keyword Competitor Analysis Script

Takes a list of keywords and analyzes:
1. Target audience (based on competitor analysis)
2. Content goal (based on SERP gaps)
3. Recommended content length (based on top 4 competitors)
4. Competition difficulty score
5. Strategic recommendations

Outputs a CSV file with results for all keywords.
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

DATAFORSEO_BASE_URL = "https://api.dataforseo.com/v3"
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


def get_serp_results(keyword):
    """
    Fetch top 10 organic search results from Google
    
    Args:
        keyword (str): The keyword to get SERP results for
        
    Returns:
        dict: SERP results data
    """
    print(f"  → Fetching SERP results for '{keyword}'...")
    
    try:
        url = f"{DATAFORSEO_BASE_URL}/serp/google/organic/live/advanced"
        
        payload = [{
            "keyword": keyword,
            "location_code": 2840,  # United States
            "language_code": "en",
            "device": "desktop",
            "os": "windows",
            "depth": 10
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
                for item in serp_items[:10]:
                    if item.get("type") == "organic":
                        formatted_results.append({
                            "position": item.get("rank_group"),
                            "title": item.get("title"),
                            "url": item.get("url"),
                            "domain": item.get("domain"),
                            "description": item.get("description"),
                        })
                
                print(f"    ✓ Found {len(formatted_results)} results")
                return {
                    "keyword": keyword,
                    "results": formatted_results
                }
            
        return {"error": "No SERP results found"}
            
    except Exception as e:
        print(f"    ✗ Error: {str(e)}")
        return {"error": f"API request failed: {str(e)}"}


def get_actual_word_count(url, timeout=10):
    """
    Fetch a URL and count actual words in main content
    
    Args:
        url (str): URL to fetch
        timeout (int): Request timeout in seconds
        
    Returns:
        int: Actual word count, or None if failed
    """
    try:
        from bs4 import BeautifulSoup
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove non-content elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'form', 'iframe']):
            element.decompose()
        
        # Find main content
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
            word_count = len([w for w in words if len(w) > 0])
            return word_count
        
        return None
        
    except Exception as e:
        return None


def analyze_content_length(serp_results):
    """
    Analyze top 4 competitor content lengths
    
    Args:
        serp_results (dict): SERP results with URLs
        
    Returns:
        dict: Word count statistics
    """
    print(f"  → Analyzing competitor content length (top 4)...")
    
    word_counts = []
    
    for result in serp_results.get("results", [])[:4]:
        url = result.get("url", "")
        domain = result.get("domain", "")
        
        actual_words = get_actual_word_count(url)
        
        if actual_words and actual_words > 100:
            word_counts.append(actual_words)
        else:
            word_counts.append(2000)  # Default fallback
    
    if word_counts:
        avg_words = sum(word_counts) / len(word_counts)
        recommended_min = int(avg_words * 1.1)
        recommended_max = int(avg_words * 1.2)
        
        print(f"    ✓ Average: {avg_words:,.0f} words")
        print(f"    ✓ Recommended: {recommended_min:,}-{recommended_max:,} words")
        
        return {
            "average": avg_words,
            "min": min(word_counts),
            "max": max(word_counts),
            "recommended_min": recommended_min,
            "recommended_max": recommended_max
        }
    
    return {
        "average": 3000,
        "min": 1500,
        "max": 5000,
        "recommended_min": 3000,
        "recommended_max": 4000
    }


# ============================================================================
# COMPETITOR ANALYSIS WITH CLAUDE
# ============================================================================

def analyze_competitors_with_claude(keyword, serp_results):
    """
    Use Claude to analyze top 4 competitors and recommend:
    - Target audience
    - Content goal
    - Competition difficulty
    - Strategic recommendations
    
    Args:
        keyword (str): Target keyword
        serp_results (dict): SERP data
        
    Returns:
        dict: Analysis results
    """
    print(f"  → Analyzing competitors with Claude AI...")
    
    if not serp_results.get("results"):
        return {
            "target_audience": "Technical Decision Makers",
            "content_goal": "Educational",
            "difficulty": "UNKNOWN",
            "difficulty_score": 50,
            "recommendations": ["No competitor data available"]
        }
    
    # Prepare top 4 competitor data
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
    
    prompt = f"""Analyze these top 4 search results and provide strategic recommendations.

KEYWORD: {keyword}

TOP 4 COMPETITORS:
{competitor_data_str}

TASK 1: Competitor Analysis
For each competitor, identify:
- Target audience (be specific about role, company size, experience)
- Content goal (what the content aims to achieve)
- Content approach (format and style)

TASK 2: Identify Gaps
- What audiences are over-served?
- What audiences are under-served?
- What content goals dominate?
- What content goals are missing?

TASK 3: Competition Difficulty
Rate the overall competition difficulty:
- WEAK (0-30): Easy to outrank with quality content
- MEDIUM (31-60): Requires strong content and some authority
- STRONG (61-85): Needs exceptional content and link building
- DOMINANT (86-100): Very difficult, long-term strategy needed

Provide a numerical score (0-100).

TASK 4: Strategic Recommendations
Provide 3-5 specific, actionable recommendations for creating content that can compete.

TASK 5: Recommend Target Audience & Goal
Based on gaps, recommend:
- A specific, underserved target audience with buying power
- A content goal that fills a gap and matches search intent

OUTPUT (JSON only, no markdown):
{{
  "competitor_analysis": [
    {{
      "position": 1,
      "domain": "...",
      "target_audience": "...",
      "content_goal": "...",
      "content_approach": "..."
    }}
  ],
  "gaps": {{
    "overserved_audiences": ["..."],
    "underserved_audiences": ["..."],
    "dominant_goals": ["..."],
    "missing_goals": ["..."]
  }},
  "difficulty": {{
    "level": "MEDIUM",
    "score": 55,
    "rationale": "..."
  }},
  "recommendations": [
    "...",
    "...",
    "..."
  ],
  "target_audience": "...",
  "content_goal": "...",
  "rationale": "..."
}}
"""

    try:
        response = anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        response_text = response.content[0].text.strip()
        
        # Extract JSON
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        analysis = json.loads(response_text)
        
        difficulty = analysis.get("difficulty", {})
        
        result = {
            "target_audience": analysis.get("target_audience", "Technical Decision Makers"),
            "content_goal": analysis.get("content_goal", "Educational"),
            "difficulty": difficulty.get("level", "MEDIUM"),
            "difficulty_score": difficulty.get("score", 50),
            "difficulty_rationale": difficulty.get("rationale", ""),
            "recommendations": analysis.get("recommendations", []),
            "gaps": analysis.get("gaps", {}),
            "full_analysis": analysis
        }
        
        print(f"    ✓ Target Audience: {result['target_audience'][:50]}...")
        print(f"    ✓ Content Goal: {result['content_goal']}")
        print(f"    ✓ Difficulty: {result['difficulty']} ({result['difficulty_score']}/100)")
        
        return result
        
    except Exception as e:
        print(f"    ✗ Error: {str(e)}")
        return {
            "target_audience": "Technical Decision Makers",
            "content_goal": "Educational",
            "difficulty": "UNKNOWN",
            "difficulty_score": 50,
            "recommendations": [f"Analysis failed: {str(e)}"]
        }


# ============================================================================
# MAIN ANALYSIS FUNCTION
# ============================================================================

def analyze_keyword(keyword):
    """
    Complete analysis for a single keyword
    
    Args:
        keyword (str): Keyword to analyze
        
    Returns:
        dict: Complete analysis results
    """
    print(f"\n{'='*60}")
    print(f"Analyzing: {keyword}")
    print(f"{'='*60}")
    
    # Step 1: Get SERP results
    serp_results = get_serp_results(keyword)
    
    if "error" in serp_results:
        return {
            "keyword": keyword,
            "error": serp_results["error"],
            "target_audience": "N/A",
            "content_goal": "N/A",
            "recommended_min_words": 0,
            "recommended_max_words": 0,
            "difficulty": "ERROR",
            "difficulty_score": 0,
            "recommendations": ["Failed to fetch SERP data"]
        }
    
    # Step 2: Analyze content length
    content_length = analyze_content_length(serp_results)
    
    # Step 3: Analyze competitors with Claude
    competitor_analysis = analyze_competitors_with_claude(keyword, serp_results)
    
    # Combine results
    result = {
        "keyword": keyword,
        "target_audience": competitor_analysis["target_audience"],
        "content_goal": competitor_analysis["content_goal"],
        "recommended_min_words": content_length["recommended_min"],
        "recommended_max_words": content_length["recommended_max"],
        "avg_competitor_words": int(content_length["average"]),
        "difficulty": competitor_analysis["difficulty"],
        "difficulty_score": competitor_analysis["difficulty_score"],
        "difficulty_rationale": competitor_analysis.get("difficulty_rationale", ""),
        "recommendations": competitor_analysis["recommendations"],
        "top_4_urls": [r["url"] for r in serp_results.get("results", [])[:4]]
    }
    
    print(f"\n✓ Analysis complete for '{keyword}'")
    
    return result


# ============================================================================
# BATCH PROCESSING
# ============================================================================

def analyze_keyword_list(keywords, output_csv="keyword_analysis_results.csv"):
    """
    Analyze a list of keywords and save results to CSV
    
    Args:
        keywords (list): List of keywords to analyze
        output_csv (str): Output CSV filename
        
    Returns:
        list: Analysis results for all keywords
    """
    print(f"\n{'='*60}")
    print(f"KEYWORD COMPETITOR ANALYSIS")
    print(f"{'='*60}")
    print(f"Total keywords to analyze: {len(keywords)}")
    print(f"Output file: {output_csv}")
    
    results = []
    
    for i, keyword in enumerate(keywords, 1):
        print(f"\n[{i}/{len(keywords)}] Processing: {keyword}")
        
        result = analyze_keyword(keyword)
        results.append(result)
        
        # Brief pause to avoid rate limits
        import time
        time.sleep(2)
    
    # Save to CSV
    print(f"\n{'='*60}")
    print(f"Saving results to {output_csv}...")
    
    try:
        with open(output_csv, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'keyword',
                'target_audience',
                'content_goal',
                'recommended_min_words',
                'recommended_max_words',
                'avg_competitor_words',
                'difficulty',
                'difficulty_score',
                'difficulty_rationale',
                'top_recommendation',
                'all_recommendations',
                'top_4_urls'
            ]
            
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in results:
                # Format recommendations
                recs = result.get('recommendations', [])
                top_rec = recs[0] if recs else ''
                all_recs = ' | '.join(recs)
                
                # Format URLs
                urls = ' | '.join(result.get('top_4_urls', []))
                
                writer.writerow({
                    'keyword': result.get('keyword', ''),
                    'target_audience': result.get('target_audience', ''),
                    'content_goal': result.get('content_goal', ''),
                    'recommended_min_words': result.get('recommended_min_words', 0),
                    'recommended_max_words': result.get('recommended_max_words', 0),
                    'avg_competitor_words': result.get('avg_competitor_words', 0),
                    'difficulty': result.get('difficulty', ''),
                    'difficulty_score': result.get('difficulty_score', 0),
                    'difficulty_rationale': result.get('difficulty_rationale', ''),
                    'top_recommendation': top_rec,
                    'all_recommendations': all_recs,
                    'top_4_urls': urls
                })
        
        print(f"✓ Results saved successfully!")
        print(f"\n{'='*60}")
        print(f"ANALYSIS COMPLETE")
        print(f"{'='*60}")
        print(f"Analyzed {len(results)} keywords")
        print(f"Output: {output_csv}")
        
    except Exception as e:
        print(f"✗ Error saving CSV: {str(e)}")
    
    return results


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function"""
    
    # ========================================================================
    # CONFIGURATION - ADD YOUR KEYWORDS HERE
    # ========================================================================
    
    keywords_to_analyze = [
        "high performance computing",
        "ai inference",
        "what is ai inference",
        "ai inference vs training",
        "gpu computing",
        "gpu as a service",
        "decentralized computing"
    ]
    
    # ========================================================================
    # RUN ANALYSIS
    # ========================================================================
    
    # Validate environment
    if not ANTHROPIC_API_KEY:
        print("ERROR: ANTHROPIC_API_KEY not found in .env file")
        return
    
    if not DATAFORSEO_LOGIN or not DATAFORSEO_PASSWORD:
        print("ERROR: DataForSEO credentials not found in .env file")
        return
    
    # Run batch analysis
    results = analyze_keyword_list(
        keywords_to_analyze,
        output_csv=f"keyword_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    )
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    
    for result in results:
        print(f"\n{result['keyword']}:")
        print(f"  Audience: {result['target_audience'][:60]}...")
        print(f"  Goal: {result['content_goal']}")
        print(f"  Length: {result['recommended_min_words']:,}-{result['recommended_max_words']:,} words")
        print(f"  Difficulty: {result['difficulty']} ({result['difficulty_score']}/100)")


if __name__ == "__main__":
    main()