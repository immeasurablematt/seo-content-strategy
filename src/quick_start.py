"""
Quick Start Script for Content Authority Mapper

This script provides an easy way to run the content authority analysis
and access key insights from the results.
"""

from content_authority_mapper import ContentAuthorityMapper
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    """Run the content authority analysis and display key insights"""
    
    print("🚀 Starting io.net Content Authority Analysis...")
    print("=" * 60)
    
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
    
    # Initialize mapper
    mapper = ContentAuthorityMapper()
    
    # Run full analysis
    df, hubs, calendar = mapper.run_full_analysis()
    
    # Display key insights
    print("\n" + "=" * 60)
    print("📊 KEY INSIGHTS")
    print("=" * 60)
    
    # Top Content Gaps
    print("\n🎯 TOP CONTENT GAPS:")
    print("-" * 30)
    top_gaps = df[df['content_strategy'] == 'High Priority Gap'].nlargest(10, 'opportunity_score')
    for _, row in top_gaps.iterrows():
        print(f"• {row['keyword']} (Volume: {row['search_volume']:,}, Competition: {row['competition']:.2f})")
    
    # Content Hubs Priority
    print("\n🏗️ CONTENT HUBS (by Priority):")
    print("-" * 40)
    for name, data in sorted(hubs.items(), key=lambda x: x[1]['priority_score'], reverse=True):
        print(f"\n📁 {name}:")
        print(f"   Pillar: {data['pillar_keyword']}")
        print(f"   Total Volume: {data['total_search_volume']:,}")
        print(f"   Authority: {data['current_authority']:.1f}/100")
        print(f"   Content Gaps: {data['content_gaps']}")
        print(f"   Priority Score: {data['priority_score']:.1f}")
    
    # Next 30 Days Content
    print("\n📅 NEXT 30 DAYS CONTENT:")
    print("-" * 35)
    next_month = calendar[calendar['week'] <= 4]
    for _, row in next_month.iterrows():
        print(f"Week {row['week']}: {row['title']}")
        print(f"   Keyword: {row['target_keyword']}")
        print(f"   Type: {row['content_type']}")
        print(f"   Priority: {row['priority']}")
        print()
    
    # Summary Statistics
    print("\n📈 SUMMARY STATISTICS:")
    print("-" * 25)
    print(f"Total keywords analyzed: {len(df):,}")
    print(f"Total search volume: {df['search_volume'].sum():,}")
    print(f"Content hubs identified: {len(hubs)}")
    print(f"High-priority gaps: {len(df[df['content_strategy'] == 'High Priority Gap'])}")
    print(f"Keywords currently ranking: {len(df[df['authority_score'] > 0])}")
    print(f"90-day content pieces: {len(calendar)}")
    
    print("\n✅ Analysis complete! Check the generated Excel and markdown files for detailed reports.")
    
    return mapper, df, hubs, calendar

def analyze_specific_keyword(keyword: str):
    """Analyze a specific keyword in detail"""
    mapper = ContentAuthorityMapper()
    
    print(f"\n🔍 Analyzing keyword: {keyword}")
    print("-" * 40)
    
    # Get keyword data
    volume_data = mapper.get_keyword_ideas(keyword)
    if volume_data:
        data = volume_data[0]
        print(f"Search Volume: {data.get('search_volume', 'N/A')}")
        print(f"Competition: {data.get('competition', 'N/A')}")
        print(f"CPC: ${data.get('cpc', 'N/A')}")
    
    # Get SERP analysis
    serp_data = mapper.get_serp_competitors(keyword)
    print(f"\nSERP Analysis (Top 10):")
    for item in serp_data[:10]:
        print(f"{item['rank']}. {item['title']} - {item['domain']}")
    
    return volume_data, serp_data

def check_domain_authority(domain: str = "io.net"):
    """Check current domain authority for key terms"""
    mapper = ContentAuthorityMapper()
    
    print(f"\n🏆 Domain Authority Analysis: {domain}")
    print("-" * 50)
    
    rankings = mapper.check_domain_rankings(domain)
    if rankings:
        df = pd.DataFrame(rankings)
        df = df.sort_values('position')
        
        print(f"Total keywords ranking: {len(df)}")
        print(f"Top 3 positions: {len(df[df['position'] <= 3])}")
        print(f"Top 10 positions: {len(df[df['position'] <= 10])}")
        
        print("\nTop 20 Rankings:")
        for _, row in df.head(20).iterrows():
            print(f"{row['position']}. {row['keyword']} (Vol: {row['search_volume']:,})")
    else:
        print("No ranking data found for this domain.")
    
    return rankings

if __name__ == "__main__":
    # Run the main analysis
    mapper, df, hubs, calendar = main()
    
    # Example of additional analysis
    print("\n" + "=" * 60)
    print("🔍 ADDITIONAL ANALYSIS EXAMPLES")
    print("=" * 60)
    
    # Analyze a specific keyword
    analyze_specific_keyword("decentralized gpu")
    
    # Check domain authority
    check_domain_authority("io.net")

