"""
Content Calendar & Topical Authority Mapping Script for io.net

This script uses DataForSEO API for keyword research and Claude for content strategy insights.
It creates a comprehensive content strategy with topical clusters, authority assessment,
and a 90-day content calendar.
"""

import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
from collections import defaultdict
import requests
import base64
from anthropic import Anthropic
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from dotenv import load_dotenv
import time

load_dotenv()

class ContentAuthorityMapper:
    def __init__(self):
        self.dataforseo_login = os.getenv('DATAFORSEO_LOGIN')
        self.dataforseo_password = os.getenv('DATAFORSEO_PASSWORD')
        self.anthropic_client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.base_url = "https://api.dataforseo.com/v3"
    
    def get_dataforseo_auth(self):
        """Create Basic Authentication header for DataForSEO API"""
        credentials = f"{self.dataforseo_login}:{self.dataforseo_password}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return {
            "Authorization": f"Basic {encoded}",
            "Content-Type": "application/json"
        }
        
    def get_seed_keywords(self) -> List[str]:
        """Define seed keywords for io.net"""
        return [
            "decentralized gpu",
            "gpu computing",
            "distributed computing",
            "ai training infrastructure",
            "machine learning compute",
            "cloud gpu",
            "gpu cluster",
            "web3 infrastructure",
            "decentralized cloud",
            "ai compute network",
            "gpu marketplace",
            "blockchain computing",
            "depin gpu",
            "ai model training",
            "gpu rendering"
        ]
    
    def dataforseo_request(self, endpoint: str, data: List[Dict]) -> Dict:
        """Make authenticated request to DataForSEO"""
        url = f"{self.base_url}{endpoint}"
        response = requests.post(
            url,
            headers=self.get_dataforseo_auth(),
            json=data,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    
    def get_keyword_ideas(self, seed_keyword: str, location_code: int = 2840) -> List[Dict]:
        """Get keyword ideas from DataForSEO"""
        print(f"Fetching keyword ideas for: {seed_keyword}")
        
        endpoint = "/keywords_data/google_ads/search_volume/live"
        data = [{
            "keywords": [seed_keyword],
            "location_code": location_code,
            "language_code": "en"
        }]
        
        try:
            response = self.dataforseo_request(endpoint, data)
            time.sleep(1)  # Rate limiting
            
            if response['status_code'] == 20000:
                return response['tasks'][0]['result']
            return []
        except Exception as e:
            print(f"Error fetching keywords for {seed_keyword}: {e}")
            return []
    
    def get_related_keywords(self, seed_keyword: str) -> List[Dict]:
        """Get related keywords using Keywords Data endpoint"""
        print(f"Fetching related keywords for: {seed_keyword}")
        
        endpoint = "/keywords_data/google_ads/keywords_for_keywords/live"
        data = [{
            "keywords": [seed_keyword],
            "location_code": 2840,
            "language_code": "en",
            "search_partners": False,
            "include_adult_keywords": False
        }]
        
        try:
            response = self.dataforseo_request(endpoint, data)
            time.sleep(1)
            
            if response['status_code'] == 20000 and response['tasks'][0]['result']:
                return response['tasks'][0]['result'][0].get('keywords', [])
            return []
        except Exception as e:
            print(f"Error fetching related keywords: {e}")
            return []
    
    def get_serp_competitors(self, keyword: str, top_n: int = 10) -> List[Dict]:
        """Get SERP competitors for a keyword"""
        print(f"Analyzing SERP for: {keyword}")
        
        endpoint = "/serp/google/organic/live/advanced"
        data = [{
            "keyword": keyword,
            "location_code": 2840,
            "language_code": "en",
            "device": "desktop",
            "os": "windows",
            "depth": top_n
        }]
        
        try:
            response = self.dataforseo_request(endpoint, data)
            time.sleep(1)
            
            if response['status_code'] == 20000 and response['tasks'][0]['result']:
                items = response['tasks'][0]['result'][0].get('items', [])
                return [
                    {
                        'url': item.get('url'),
                        'domain': item.get('domain'),
                        'title': item.get('title'),
                        'rank': item.get('rank_absolute'),
                        'keyword': keyword
                    }
                    for item in items if item.get('type') == 'organic'
                ]
            return []
        except Exception as e:
            print(f"Error fetching SERP data: {e}")
            return []
    
    def check_domain_rankings(self, domain: str = "io.net") -> List[Dict]:
        """Check what keywords a domain ranks for"""
        print(f"Checking rankings for domain: {domain}")
        
        endpoint = "/dataforseo_labs/google/ranked_keywords/live"
        data = [{
            "target": domain,
            "location_code": 2840,
            "language_code": "en",
            "limit": 1000
        }]
        
        try:
            response = self.dataforseo_request(endpoint, data)
            time.sleep(1)
            
            if response['status_code'] == 20000 and response['tasks'][0]['result']:
                items = response['tasks'][0]['result'][0].get('items', [])
                return [
                    {
                        'keyword': item.get('keyword_data', {}).get('keyword'),
                        'position': item.get('ranked_serp_element', {}).get('serp_item', {}).get('rank_absolute'),
                        'search_volume': item.get('keyword_data', {}).get('keyword_info', {}).get('search_volume'),
                        'competition': item.get('keyword_data', {}).get('keyword_info', {}).get('competition')
                    }
                    for item in items
                ]
            return []
        except Exception as e:
            print(f"Error checking domain rankings: {e}")
            return []
    
    def build_keyword_dataset(self) -> pd.DataFrame:
        """Build comprehensive keyword dataset"""
        all_keywords = []
        seed_keywords = self.get_seed_keywords()
        
        print("\n=== Building Keyword Dataset ===\n")
        
        for seed in seed_keywords:
            # Get search volume data
            volume_data = self.get_keyword_ideas(seed)
            if volume_data:
                for item in volume_data:
                    all_keywords.append({
                        'keyword': item.get('keyword'),
                        'search_volume': item.get('search_volume'),
                        'competition': item.get('competition'),
                        'cpc': item.get('cpc'),
                        'seed_keyword': seed
                    })
            
            # Get related keywords
            related = self.get_related_keywords(seed)
            for item in related:
                all_keywords.append({
                    'keyword': item.get('keyword'),
                    'search_volume': item.get('search_volume'),
                    'competition': item.get('competition'),
                    'cpc': item.get('cpc'),
                    'seed_keyword': seed
                })
        
        df = pd.DataFrame(all_keywords)
        df = df.drop_duplicates(subset=['keyword'])
        df = df[df['search_volume'].notna() & (df['search_volume'] > 0)]
        
        print(f"\nCollected {len(df)} unique keywords")
        return df
    
    def create_topical_clusters(self, df: pd.DataFrame, n_clusters: int = 8) -> pd.DataFrame:
        """Create topical clusters using TF-IDF and K-Means"""
        print("\n=== Creating Topical Clusters ===\n")
        
        # TF-IDF vectorization
        vectorizer = TfidfVectorizer(
            max_features=100,
            ngram_range=(1, 3),
            stop_words='english'
        )
        
        X = vectorizer.fit_transform(df['keyword'])
        
        # K-Means clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        df['cluster'] = kmeans.fit_predict(X)
        
        # Analyze clusters using Claude
        cluster_analysis = self.analyze_clusters_with_claude(df)
        
        # Add cluster names
        df['cluster_name'] = df['cluster'].map(cluster_analysis)
        
        return df
    
    def analyze_clusters_with_claude(self, df: pd.DataFrame) -> Dict[int, str]:
        """Use Claude to name and analyze clusters"""
        print("Using Claude to analyze clusters...")
        
        cluster_keywords = {}
        for cluster_id in df['cluster'].unique():
            cluster_data = df[df['cluster'] == cluster_id].nlargest(20, 'search_volume')
            cluster_keywords[cluster_id] = cluster_data['keyword'].tolist()
        
        prompt = f"""Analyze these keyword clusters and provide:
1. A concise, descriptive name for each cluster (2-4 words)
2. The main topic/theme

Clusters:
{json.dumps(cluster_keywords, indent=2)}

Respond in JSON format:
{{
    "0": "Cluster Name",
    "1": "Cluster Name",
    ...
}}
"""
        
        message = self.anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        response_text = message.content[0].text
        # Extract JSON from markdown code blocks if present
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0]
        
        cluster_names = json.loads(response_text.strip())
        
        # Convert string keys to int
        return {int(k): v for k, v in cluster_names.items()}
    
    def assess_topical_authority(self, df: pd.DataFrame) -> pd.DataFrame:
        """Assess io.net's topical authority"""
        print("\n=== Assessing Topical Authority ===\n")
        
        # Get current rankings
        current_rankings = self.check_domain_rankings("io.net")
        ranking_df = pd.DataFrame(current_rankings)
        
        if not ranking_df.empty:
            # Merge with keyword data
            df = df.merge(
                ranking_df[['keyword', 'position']],
                on='keyword',
                how='left'
            )
            df['ranking_position'] = df['position']
            df.drop('position', axis=1, inplace=True)
        else:
            df['ranking_position'] = None
        
        # Calculate authority score
        def calculate_authority(row):
            if pd.isna(row['ranking_position']):
                return 0  # No ranking = no authority
            elif row['ranking_position'] <= 3:
                return 100
            elif row['ranking_position'] <= 10:
                return 70
            elif row['ranking_position'] <= 20:
                return 40
            else:
                return 20
        
        df['authority_score'] = df.apply(calculate_authority, axis=1)
        
        return df
    
    def identify_content_gaps(self, df: pd.DataFrame) -> pd.DataFrame:
        """Identify content gaps and opportunities"""
        print("\n=== Identifying Content Gaps ===\n")
        
        # High opportunity: high search volume, low competition, no ranking
        df['opportunity_score'] = (
            (df['search_volume'] / df['search_volume'].max() * 50) +
            ((1 - df['competition']) * 30) +
            ((100 - df['authority_score']) / 100 * 20)
        )
        
        # Categorize opportunities
        def categorize_opportunity(row):
            if row['authority_score'] >= 70:
                return 'Defend & Expand'
            elif row['authority_score'] >= 40:
                return 'Improve Ranking'
            elif row['search_volume'] >= 1000 and row['competition'] < 0.7:
                return 'High Priority Gap'
            elif row['search_volume'] >= 100:
                return 'Medium Priority Gap'
            else:
                return 'Low Priority'
        
        df['content_strategy'] = df.apply(categorize_opportunity, axis=1)
        
        return df
    
    def create_content_hubs(self, df: pd.DataFrame) -> Dict[str, Dict]:
        """Identify and structure content hubs"""
        print("\n=== Creating Content Hub Strategy ===\n")
        
        hubs = {}
        
        for cluster_id in df['cluster'].unique():
            cluster_data = df[df['cluster'] == cluster_id]
            cluster_name = cluster_data['cluster_name'].iloc[0]
            
            # Identify pillar content (highest volume/authority keywords)
            pillar = cluster_data.nlargest(1, 'search_volume').iloc[0]
            
            # Identify supporting content
            supporting = cluster_data.nlargest(10, 'opportunity_score')
            
            # Calculate hub metrics
            total_volume = cluster_data['search_volume'].sum()
            avg_authority = cluster_data['authority_score'].mean()
            gap_count = len(cluster_data[cluster_data['authority_score'] < 40])
            
            hubs[cluster_name] = {
                'pillar_keyword': pillar['keyword'],
                'pillar_volume': pillar['search_volume'],
                'supporting_keywords': supporting['keyword'].tolist(),
                'total_search_volume': total_volume,
                'current_authority': avg_authority,
                'content_gaps': gap_count,
                'priority_score': total_volume * (100 - avg_authority) / 100
            }
        
        return hubs
    
    def generate_content_calendar(self, df: pd.DataFrame, hubs: Dict) -> pd.DataFrame:
        """Generate 90-day content calendar"""
        print("\n=== Generating 90-Day Content Calendar ===\n")
        
        # Get Claude's help for content strategy
        calendar_items = self.generate_calendar_with_claude(df, hubs)
        
        return pd.DataFrame(calendar_items)
    
    def generate_calendar_with_claude(self, df: pd.DataFrame, hubs: Dict) -> List[Dict]:
        """Use Claude to create strategic content calendar"""
        print("Using Claude to create content calendar...")
        
        # Prepare data for Claude
        hub_summary = {
            name: {
                'pillar': data['pillar_keyword'],
                'gaps': data['content_gaps'],
                'priority': data['priority_score'],
                'authority': data['current_authority']
            }
            for name, data in hubs.items()
        }
        
        # Get top opportunities
        top_gaps = df[df['content_strategy'] == 'High Priority Gap'].nlargest(30, 'opportunity_score')
        
        prompt = f"""Create a strategic 90-day content calendar for io.net, a decentralized GPU computing platform.

Content Hubs Analysis:
{json.dumps(hub_summary, indent=2)}

Top Priority Content Gaps:
{top_gaps[['keyword', 'search_volume', 'competition', 'opportunity_score']].to_json(orient='records')}

Requirements:
1. Mix of pillar content (comprehensive guides), cluster content (topic-specific), and supporting content
2. Balance between thought leadership and SEO-driven content
3. Consider business priorities: developer adoption, network growth, AI/ML use cases
4. Include content types: blog posts, tutorials, case studies, technical docs
5. Prioritize high-opportunity keywords while building topical authority

Create 30 content pieces (roughly 2-3 per week) over 90 days.

Respond in JSON format as an array of objects:
[
    {{
        "week": 1,
        "title": "Content Title",
        "target_keyword": "primary keyword",
        "content_type": "blog|tutorial|guide|case_study|technical_doc",
        "hub": "Hub Name",
        "priority": "high|medium|low",
        "business_goal": "developer_adoption|network_growth|seo|thought_leadership",
        "estimated_impact": "Description of expected impact"
    }}
]
"""
        
        message = self.anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=8000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        response_text = message.content[0].text
        
        # Extract JSON from markdown code blocks if present
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0]
        
        calendar = json.loads(response_text.strip())
        
        # Add dates
        start_date = datetime.now()
        for item in calendar:
            week_offset = item['week'] - 1
            publish_date = start_date + timedelta(weeks=week_offset)
            item['publish_date'] = publish_date.strftime('%Y-%m-%d')
        
        return calendar
    
    def generate_report(self, df: pd.DataFrame, hubs: Dict, calendar: pd.DataFrame):
        """Generate comprehensive reports"""
        print("\n=== Generating Reports ===\n")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 1. Full keyword data with clusters and authority
        excel_path = f'ionet_content_strategy_{timestamp}.xlsx'
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            # Keywords sheet
            df_export = df[[
                'keyword', 'search_volume', 'competition', 'cpc',
                'cluster_name', 'ranking_position', 'authority_score',
                'opportunity_score', 'content_strategy'
            ]].sort_values('opportunity_score', ascending=False)
            df_export.to_excel(writer, sheet_name='Keywords', index=False)
            
            # Clusters summary
            cluster_summary = df.groupby('cluster_name').agg({
                'keyword': 'count',
                'search_volume': 'sum',
                'authority_score': 'mean',
                'opportunity_score': 'mean'
            }).round(2)
            cluster_summary.columns = ['Keyword Count', 'Total Volume', 'Avg Authority', 'Avg Opportunity']
            cluster_summary.to_excel(writer, sheet_name='Cluster Summary')
            
            # Content calendar
            calendar.to_excel(writer, sheet_name='Content Calendar', index=False)
            
            # Content hubs
            hubs_df = pd.DataFrame([
                {
                    'Hub': name,
                    'Pillar Keyword': data['pillar_keyword'],
                    'Pillar Volume': data['pillar_volume'],
                    'Total Volume': data['total_search_volume'],
                    'Current Authority': round(data['current_authority'], 2),
                    'Content Gaps': data['content_gaps'],
                    'Priority Score': round(data['priority_score'], 2)
                }
                for name, data in hubs.items()
            ]).sort_values('Priority Score', ascending=False)
            hubs_df.to_excel(writer, sheet_name='Content Hubs', index=False)
        
        print(f"\n✅ Excel report saved: {excel_path}")
        
        # 2. Executive summary using Claude
        self.generate_executive_summary(df, hubs, calendar, timestamp)
        
        # 3. JSON export for programmatic use
        json_path = f'ionet_data_{timestamp}.json'
        export_data = {
            'generated_at': datetime.now().isoformat(),
            'keywords': df.to_dict('records'),
            'content_hubs': hubs,
            'content_calendar': calendar.to_dict('records')
        }
        with open(json_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"✅ JSON data saved: {json_path}")
        
        return excel_path
    
    def generate_executive_summary(self, df: pd.DataFrame, hubs: Dict, calendar: pd.DataFrame, timestamp: str):
        """Generate executive summary using Claude"""
        print("Generating executive summary with Claude...")
        
        # Prepare statistics
        stats = {
            'total_keywords': len(df),
            'total_search_volume': int(df['search_volume'].sum()),
            'avg_authority': round(df['authority_score'].mean(), 2),
            'high_priority_gaps': len(df[df['content_strategy'] == 'High Priority Gap']),
            'keywords_ranking': len(df[df['authority_score'] > 0]),
            'top_3_rankings': len(df[df['ranking_position'] <= 3]),
            'content_hubs': len(hubs),
            'calendar_items': len(calendar)
        }
        
        top_opportunities = df.nlargest(10, 'opportunity_score')[
            ['keyword', 'search_volume', 'competition', 'authority_score', 'content_strategy']
        ].to_dict('records')
        
        prompt = f"""Create an executive summary for io.net's content strategy and topical authority analysis.

Key Statistics:
{json.dumps(stats, indent=2)}

Top Opportunities:
{json.dumps(top_opportunities, indent=2)}

Content Hubs:
{json.dumps({k: {'priority': v['priority_score'], 'authority': v['current_authority'], 'gaps': v['content_gaps']} for k, v in hubs.items()}, indent=2)}

Create a concise executive summary covering:
1. Current State Assessment (authority position, strengths, weaknesses)
2. Key Opportunities (biggest content gaps and why they matter)
3. Strategic Recommendations (what to prioritize and why)
4. Expected Impact (what success looks like in 90 days)

Format as markdown with clear sections and bullet points.
"""
        
        message = self.anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        summary = message.content[0].text
        
        # Save summary
        summary_path = f'ionet_executive_summary_{timestamp}.md'
        with open(summary_path, 'w') as f:
            f.write(f"# io.net Content Strategy & Topical Authority Analysis\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            f.write(summary)
        
        print(f"✅ Executive summary saved: {summary_path}")
        
        return summary_path
    
    def run_full_analysis(self):
        """Run complete analysis pipeline"""
        print("\n" + "="*60)
        print("IO.NET CONTENT STRATEGY & TOPICAL AUTHORITY MAPPER")
        print("="*60 + "\n")
        
        try:
            # Step 1: Build keyword dataset
            df = self.build_keyword_dataset()
            
            # Step 2: Create topical clusters
            df = self.create_topical_clusters(df)
            
            # Step 3: Assess topical authority
            df = self.assess_topical_authority(df)
            
            # Step 4: Identify content gaps
            df = self.identify_content_gaps(df)
            
            # Step 5: Create content hubs
            hubs = self.create_content_hubs(df)
            
            # Step 6: Generate content calendar
            calendar = self.generate_content_calendar(df, hubs)
            
            # Step 7: Generate reports
            report_path = self.generate_report(df, hubs, calendar)
            
            print("\n" + "="*60)
            print("✅ ANALYSIS COMPLETE!")
            print("="*60)
            print(f"\nMain report: {report_path}")
            print("\nKey Insights:")
            print(f"  • Total keywords analyzed: {len(df)}")
            print(f"  • Content hubs identified: {len(hubs)}")
            print(f"  • High-priority gaps: {len(df[df['content_strategy'] == 'High Priority Gap'])}")
            print(f"  • 90-day content pieces: {len(calendar)}")
            
            return df, hubs, calendar
            
        except Exception as e:
            print(f"\n❌ Error during analysis: {e}")
            raise

def main():
    mapper = ContentAuthorityMapper()
    df, hubs, calendar = mapper.run_full_analysis()
    return mapper, df, hubs, calendar

if __name__ == "__main__":
    main()

