"""
Advanced Analysis Script for Content Authority Mapper

This script provides extended features for competitive analysis,
content performance tracking, and internal linking suggestions.
"""

import pandas as pd
from content_authority_mapper import ContentAuthorityMapper
from typing import List, Dict
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AdvancedAnalyzer(ContentAuthorityMapper):
    
    def competitive_gap_analysis(self, competitors: List[str]) -> pd.DataFrame:
        """Compare authority against competitors"""
        print("\n=== Competitive Gap Analysis ===\n")
        
        all_competitor_data = []
        
        for competitor in competitors:
            print(f"Analyzing competitor: {competitor}")
            rankings = self.check_domain_rankings(competitor)
            for item in rankings:
                item['competitor'] = competitor
                all_competitor_data.append(item)
        
        comp_df = pd.DataFrame(all_competitor_data)
        
        # Compare with io.net
        ionet_rankings = self.check_domain_rankings("io.net")
        ionet_df = pd.DataFrame(ionet_rankings)
        ionet_df['competitor'] = 'io.net'
        
        # Combine data
        all_df = pd.concat([comp_df, ionet_df], ignore_index=True)
        
        # Find gaps where competitors rank but io.net doesn't
        competitor_keywords = set(comp_df['keyword'])
        ionet_keywords = set(ionet_df['keyword'])
        
        gap_keywords = competitor_keywords - ionet_keywords
        
        gaps = comp_df[comp_df['keyword'].isin(gap_keywords)].copy()
        gaps = gaps.sort_values(['search_volume', 'position'], ascending=[False, True])
        
        print(f"Found {len(gap_keywords)} keywords where competitors rank but io.net doesn't")
        
        return gaps
    
    def track_content_performance(self, published_content: List[Dict]) -> pd.DataFrame:
        """Track performance of published content"""
        print("\n=== Tracking Content Performance ===\n")
        
        performance = []
        
        for content in published_content:
            keyword = content['target_keyword']
            print(f"Checking performance for: {keyword}")
            
            # Get current ranking
            serp_data = self.get_serp_competitors(keyword)
            
            ionet_position = None
            for item in serp_data:
                if 'io.net' in item['domain']:
                    ionet_position = item['rank']
                    break
            
            performance.append({
                'title': content['title'],
                'keyword': keyword,
                'publish_date': content.get('publish_date'),
                'current_position': ionet_position,
                'status': 'Ranking' if ionet_position else 'Not Ranking',
                'target_position': 10  # Top 10 goal
            })
        
        return pd.DataFrame(performance)
    
    def suggest_internal_linking(self, df: pd.DataFrame) -> List[Dict]:
        """Suggest internal linking opportunities"""
        print("\n=== Internal Linking Suggestions ===\n")
        
        suggestions = []
        
        # Group by cluster
        for cluster in df['cluster_name'].unique():
            cluster_content = df[df['cluster_name'] == cluster]
            
            # Find pillar
            pillar = cluster_content.nlargest(1, 'search_volume').iloc[0]
            
            # Find supporting content
            supporting = cluster_content[cluster_content['keyword'] != pillar['keyword']]
            
            for _, support in supporting.iterrows():
                suggestions.append({
                    'from_page': support['keyword'],
                    'to_page': pillar['keyword'],
                    'anchor_text': pillar['keyword'],
                    'cluster': cluster,
                    'reason': 'Hub structure - supporting to pillar'
                })
        
        return suggestions
    
    def analyze_content_velocity(self, df: pd.DataFrame) -> Dict:
        """Analyze content velocity needs by cluster"""
        print("\n=== Content Velocity Analysis ===\n")
        
        velocity_analysis = {}
        
        for cluster in df['cluster_name'].unique():
            cluster_data = df[df['cluster_name'] == cluster]
            
            # Calculate metrics
            total_volume = cluster_data['search_volume'].sum()
            avg_authority = cluster_data['authority_score'].mean()
            gap_count = len(cluster_data[cluster_data['authority_score'] < 40])
            
            # Determine velocity needs
            if gap_count > 10 and total_volume > 10000:
                velocity = "High - 2-3 pieces per month"
            elif gap_count > 5 and total_volume > 5000:
                velocity = "Medium - 1-2 pieces per month"
            else:
                velocity = "Low - 1 piece per month"
            
            velocity_analysis[cluster] = {
                'total_volume': total_volume,
                'avg_authority': avg_authority,
                'content_gaps': gap_count,
                'recommended_velocity': velocity,
                'priority_keywords': cluster_data.nlargest(5, 'opportunity_score')['keyword'].tolist()
            }
        
        return velocity_analysis
    
    def generate_competitor_report(self, competitors: List[str]) -> str:
        """Generate comprehensive competitor analysis report"""
        print("\n=== Generating Competitor Report ===\n")
        
        # Get competitor data
        gaps = self.competitive_gap_analysis(competitors)
        
        # Analyze each competitor
        competitor_analysis = {}
        for competitor in competitors:
            rankings = self.check_domain_rankings(competitor)
            if rankings:
                comp_df = pd.DataFrame(rankings)
                competitor_analysis[competitor] = {
                    'total_keywords': len(comp_df),
                    'top_3_rankings': len(comp_df[comp_df['position'] <= 3]),
                    'top_10_rankings': len(comp_df[comp_df['position'] <= 10]),
                    'total_volume': comp_df['search_volume'].sum(),
                    'avg_position': comp_df['position'].mean(),
                    'top_keywords': comp_df.nlargest(10, 'search_volume')['keyword'].tolist()
                }
        
        # Generate report using Claude
        prompt = f"""Create a competitive analysis report for io.net vs competitors.

Competitor Analysis:
{json.dumps(competitor_analysis, indent=2)}

Content Gaps (keywords competitors rank for but io.net doesn't):
{gaps[['keyword', 'search_volume', 'competition', 'competitor', 'position']].head(20).to_json(orient='records')}

Create a comprehensive report covering:
1. Competitive Landscape Overview
2. Strengths and Weaknesses vs Each Competitor
3. Key Content Gaps and Opportunities
4. Strategic Recommendations

Format as markdown with clear sections and actionable insights.
"""
        
        message = self.anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        report = message.content[0].text
        
        # Save report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = f'competitor_analysis_{timestamp}.md'
        with open(report_path, 'w') as f:
            f.write(f"# Competitive Analysis Report - io.net\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            f.write(report)
        
        print(f"✅ Competitor report saved: {report_path}")
        
        return report_path
    
    def create_content_brief_template(self, keyword: str) -> Dict:
        """Create a detailed content brief for a specific keyword"""
        print(f"\n=== Creating Content Brief for: {keyword} ===\n")
        
        # Get keyword data
        volume_data = self.get_keyword_ideas(keyword)
        serp_data = self.get_serp_competitors(keyword)
        
        # Analyze top competitors
        competitor_analysis = []
        for item in serp_data[:5]:
            competitor_analysis.append({
                'rank': item['rank'],
                'title': item['title'],
                'domain': item['domain'],
                'url': item['url']
            })
        
        # Generate brief using Claude
        prompt = f"""Create a comprehensive content brief for the keyword: "{keyword}"

Keyword Data:
{json.dumps(volume_data[0] if volume_data else {}, indent=2)}

Top 5 Competitors:
{json.dumps(competitor_analysis, indent=2)}

Create a detailed content brief including:
1. Target Audience
2. Content Angle/Unique Value Proposition
3. Content Structure/Outline
4. Key Points to Cover
5. Internal Linking Opportunities
6. Call-to-Action Strategy
7. SEO Optimization Tips

Format as a structured brief that a content writer can follow.
"""
        
        message = self.anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        brief = message.content[0].text
        
        return {
            'keyword': keyword,
            'search_volume': volume_data[0].get('search_volume') if volume_data else None,
            'competition': volume_data[0].get('competition') if volume_data else None,
            'cpc': volume_data[0].get('cpc') if volume_data else None,
            'competitor_analysis': competitor_analysis,
            'content_brief': brief
        }

def main():
    """Run advanced analysis examples"""
    
    # Validate environment variables
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    dataforseo_login = os.getenv('DATAFORSEO_LOGIN')
    dataforseo_password = os.getenv('DATAFORSEO_PASSWORD')
    
    if not anthropic_key:
        print("\n❌ ERROR: ANTHROPIC_API_KEY not found in .env file")
        return
    
    if not dataforseo_login or not dataforseo_password:
        print("\n⚠️  WARNING: DataForSEO credentials not found in .env file")
        print("   API calls will fail without proper credentials")
    
    analyzer = AdvancedAnalyzer()
    
    print("🔬 Advanced Content Authority Analysis")
    print("=" * 50)
    
    # Example 1: Competitive Analysis
    print("\n1. Competitive Gap Analysis")
    competitors = ['runpod.io', 'vast.ai', 'lambda.cloud']
    gaps = analyzer.competitive_gap_analysis(competitors)
    
    if not gaps.empty:
        print(f"\nTop 10 Content Gaps:")
        for _, row in gaps.head(10).iterrows():
            print(f"• {row['keyword']} (Vol: {row['search_volume']:,}, Comp: {row['competitor']})")
    
    # Example 2: Content Performance Tracking
    print("\n2. Content Performance Tracking")
    published_content = [
        {'title': 'Getting Started with Decentralized GPU Computing', 'target_keyword': 'decentralized gpu', 'publish_date': '2024-01-15'},
        {'title': 'AI Model Training on Distributed Networks', 'target_keyword': 'ai model training', 'publish_date': '2024-01-20'}
    ]
    
    performance = analyzer.track_content_performance(published_content)
    print("\nContent Performance:")
    for _, row in performance.iterrows():
        print(f"• {row['title']}: Position {row['current_position'] or 'Not ranking'}")
    
    # Example 3: Internal Linking Suggestions
    print("\n3. Internal Linking Suggestions")
    # This would require the full keyword dataset from the main analysis
    print("Run the main analysis first to get internal linking suggestions.")
    
    # Example 4: Content Velocity Analysis
    print("\n4. Content Velocity Analysis")
    # This would also require the full dataset
    print("Run the main analysis first to get velocity recommendations.")
    
    # Example 5: Competitor Report
    print("\n5. Generating Competitor Report")
    report_path = analyzer.generate_competitor_report(competitors)
    print(f"Competitor report saved: {report_path}")
    
    # Example 6: Content Brief Template
    print("\n6. Content Brief Template")
    brief = analyzer.create_content_brief_template("decentralized gpu computing")
    print(f"Content brief created for: {brief['keyword']}")
    
    return analyzer

if __name__ == "__main__":
    analyzer = main()

