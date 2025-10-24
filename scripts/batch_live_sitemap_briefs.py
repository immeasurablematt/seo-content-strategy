#!/usr/bin/env python3
"""
Batch Live Sitemap Brief Generator for io.net Priority Keywords

This script generates enhanced content briefs with live sitemap integration
for all priority keywords from your cluster analysis.
"""

import os
import sys
import time
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from updated_simple_seo_brief import run_enhanced_brief_with_sitemap
from live_sitemap_internal_links import LiveSitemapInternalLinker

class BatchLiveSitemapBriefGenerator:
    def __init__(self):
        self.sitemap_linker = LiveSitemapInternalLinker()
        
        # Priority keywords from your cluster analysis (Phase 1 & 2)
        self.priority_keywords = [
            # Phase 1: Quick Wins (Weeks 1-4)
            {
                "keyword": "gpu vs cpu for ai",
                "cluster": "CLUSTER 1: GPU FOR AI FUNDAMENTALS",
                "priority": "HIGHEST",
                "target_audience": "Technical decision-makers exploring AI infrastructure",
                "content_goal": "Educational comparison and decision-making guide",
                "expected_impact": "Quick ranking potential - lowest KD"
            },
            {
                "keyword": "cloud computing and ai",
                "cluster": "CLUSTER 5: AI CLOUD COMPUTING ECOSYSTEM", 
                "priority": "HIGH",
                "target_audience": "Enterprise architects and CIOs",
                "content_goal": "Integration guide and strategic overview",
                "expected_impact": "Low KD + commercial intent"
            },
            {
                "keyword": "best ai apis",
                "cluster": "CLUSTER 7: BEST AI/CLOUD TOOLS & APIS",
                "priority": "HIGH",
                "target_audience": "Developers and technical founders",
                "content_goal": "Comprehensive API comparison and evaluation",
                "expected_impact": "Developer-focused, moderate difficulty"
            },
            {
                "keyword": "why does ai use gpu instead of cpu",
                "cluster": "CLUSTER 1: GPU FOR AI FUNDAMENTALS",
                "priority": "HIGH",
                "target_audience": "Technical decision-makers and developers",
                "content_goal": "Educational explanation of GPU advantages",
                "expected_impact": "Supporting content for pillar article"
            },
            {
                "keyword": "why does ai need gpu",
                "cluster": "CLUSTER 1: GPU FOR AI FUNDAMENTALS",
                "priority": "MEDIUM",
                "target_audience": "Technical decision-makers and developers",
                "content_goal": "Educational guide explaining GPU requirements",
                "expected_impact": "Supporting content for pillar article"
            },
            {
                "keyword": "ai accelerator vs gpu",
                "cluster": "CLUSTER 1: GPU FOR AI FUNDAMENTALS",
                "priority": "MEDIUM",
                "target_audience": "Technical decision-makers and developers",
                "content_goal": "Technical comparison and evaluation guide",
                "expected_impact": "Supporting content for pillar article"
            },
            # Phase 2: Volume Opportunities (Weeks 5-8)
            {
                "keyword": "cloud ai",
                "cluster": "CLUSTER 6: AI CLOUD SERVICES & PLATFORMS",
                "priority": "HIGHEST",
                "target_audience": "Platform evaluators and solution architects",
                "content_goal": "Comprehensive platform guide and comparison",
                "expected_impact": "MASSIVE OPPORTUNITY - highest volume"
            },
            {
                "keyword": "ai cloud",
                "cluster": "CLUSTER 6: AI CLOUD SERVICES & PLATFORMS",
                "priority": "HIGH",
                "target_audience": "Platform evaluators and solution architects", 
                "content_goal": "Overview and platform comparison",
                "expected_impact": "High volume opportunity"
            },
            {
                "keyword": "gpu cloud providers",
                "cluster": "CLUSTER 3: GPU CLOUD PROVIDERS & SERVICES",
                "priority": "HIGH",
                "target_audience": "CTOs and infrastructure teams",
                "content_goal": "Provider comparison and evaluation",
                "expected_impact": "Commercial intent - high CPC potential"
            },
            {
                "keyword": "ai cloud services",
                "cluster": "CLUSTER 6: AI CLOUD SERVICES & PLATFORMS",
                "priority": "MEDIUM",
                "target_audience": "Platform evaluators and solution architects",
                "content_goal": "Services directory and comparison",
                "expected_impact": "Commercial intent content"
            }
        ]
    
    def generate_all_live_sitemap_briefs(self, start_from: int = 0, max_keywords: int = None):
        """Generate enhanced briefs for all priority keywords using live sitemap"""
        
        print("🌐 Batch Live Sitemap Brief Generator for io.net")
        print("=" * 70)
        print(f"📊 Total keywords to process: {len(self.priority_keywords)}")
        print(f"🎯 Starting from keyword {start_from + 1}")
        
        if max_keywords:
            keywords_to_process = self.priority_keywords[start_from:start_from + max_keywords]
        else:
            keywords_to_process = self.priority_keywords[start_from:]
        
        print(f"📝 Processing {len(keywords_to_process)} keywords...")
        print()
        
        # Step 1: Fetch live sitemap once for all keywords
        print("🌐 Fetching live sitemap data...")
        sitemap_stats = self.sitemap_linker.get_sitemap_statistics()
        print(f"✅ Sitemap loaded: {sitemap_stats['total_pages']} pages, {sitemap_stats['recent_pages']} recent")
        print()
        
        results = []
        
        for i, keyword_data in enumerate(keywords_to_process, start_from + 1):
            keyword = keyword_data["keyword"]
            cluster = keyword_data["cluster"]
            priority = keyword_data["priority"]
            
            print(f"📄 Processing {i}/{len(self.priority_keywords)}: {keyword}")
            print(f"   Cluster: {cluster}")
            print(f"   Priority: {priority}")
            print(f"   Expected Impact: {keyword_data['expected_impact']}")
            print("-" * 50)
            
            try:
                # Generate enhanced brief with live sitemap
                recommendations = run_enhanced_brief_with_sitemap(
                    primary_keyword=keyword,
                    target_audience=keyword_data["target_audience"],
                    content_goal=keyword_data["content_goal"]
                )
                
                results.append({
                    "keyword": keyword,
                    "cluster": cluster,
                    "priority": priority,
                    "status": "SUCCESS",
                    "recommendations_count": len(recommendations) if recommendations else 0,
                    "sitemap_stats": sitemap_stats
                })
                
                print(f"✅ Successfully generated brief for: {keyword}")
                if recommendations:
                    print(f"   Found {len(recommendations)} internal link recommendations")
                
                # Add delay to avoid rate limiting
                if i < len(self.priority_keywords):
                    print("⏳ Waiting 30 seconds before next keyword...")
                    time.sleep(30)
                
            except Exception as e:
                print(f"❌ Error generating brief for {keyword}: {str(e)}")
                results.append({
                    "keyword": keyword,
                    "cluster": cluster,
                    "priority": priority,
                    "status": "ERROR",
                    "error": str(e)
                })
            
            print()
        
        # Generate summary report
        self.generate_live_sitemap_summary_report(results, sitemap_stats)
        
        return results
    
    def generate_live_sitemap_summary_report(self, results: list, sitemap_stats: dict):
        """Generate a summary report of all live sitemap brief generations"""
        
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_filename = f'batch_live_sitemap_report_{timestamp}.md'
        
        successful = [r for r in results if r["status"] == "SUCCESS"]
        failed = [r for r in results if r["status"] == "ERROR"]
        
        report_content = f"""# Batch Live Sitemap Brief Generation Report

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Sitemap Last Updated:** {sitemap_stats['last_fetch']}
**Total Pages Available:** {sitemap_stats['total_pages']}
**Recent Pages (Oct 2025):** {sitemap_stats['recent_pages']}

---

## 📊 Summary Statistics

- **Success Rate:** {(len(successful) / len(results) * 100):.1f}%
- **Total Briefs Generated:** {len(successful)}
- **Keywords Failed:** {len(failed)}
- **Average Internal Links per Brief:** {sum(r.get('recommendations_count', 0) for r in successful) / len(successful) if successful else 0:.1f}

---

## 🌐 Live Sitemap Data Used

### Categories Available:
"""
        
        for category, count in sitemap_stats['categories'].items():
            report_content += f"- **{category}:** {count} pages\n"
        
        report_content += f"""

### Priority Distribution:
"""
        
        for priority, count in sitemap_stats['priorities'].items():
            report_content += f"- **Priority {priority}:** {count} pages\n"
        
        report_content += f"""

---

## ✅ Successfully Generated Briefs

"""
        
        for result in successful:
            report_content += f"""### {result['keyword']}
- **Cluster:** {result['cluster']}
- **Priority:** {result['priority']}
- **Status:** ✅ SUCCESS
- **Internal Links Found:** {result.get('recommendations_count', 0)}
- **Files Generated:** 
  - `{result['keyword'].lower().replace(' ', '-')}-brief.md`
  - `{result['keyword'].lower().replace(' ', '-')}-live-sitemap-brief.md`

"""
        
        if failed:
            report_content += """---

## ❌ Failed Brief Generations

"""
            for result in failed:
                report_content += f"""### {result['keyword']}
- **Cluster:** {result['cluster']}
- **Priority:** {result['priority']}
- **Status:** ❌ ERROR
- **Error:** {result.get('error', 'Unknown error')}

"""
        
        report_content += """---

## 🎯 Next Steps

1. **Review Generated Briefs:** Check all successfully generated brief files
2. **Implement Live Sitemap Recommendations:** Use the most current internal linking data
3. **Prioritize Recent Content:** Focus on pages with recent last_modified dates
4. **Monitor Performance:** Track rankings and traffic for each keyword
5. **Refresh Weekly:** Re-run analysis weekly for new content opportunities

---

## 📁 Generated Files

Each successful brief generation creates two files:
- `{keyword}-brief.md` - Standard SEO content brief
- `{keyword}-live-sitemap-brief.md` - Enhanced brief with live sitemap internal linking

---

## 🔄 Keeping Recommendations Current

This batch generation used live sitemap data that includes:
- **Real-time page inventory** from io.net
- **Current priority scores** and modification dates
- **Automatic updates** when new content is published
- **Recent content prioritization** for better internal linking

To keep recommendations current, re-run this batch analysis weekly or before major content campaigns.

---

*This report was generated by the io.net Content Strategy Tool with live sitemap integration.*
"""
        
        # Save report
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"📊 Live sitemap summary report saved: {report_filename}")
        
        return report_filename

def main():
    """Main function to run batch live sitemap brief generation"""
    batch_generator = BatchLiveSitemapBriefGenerator()
    
    print("🌐 Batch Live Sitemap Brief Generator")
    print("=" * 50)
    print("This will generate enhanced briefs with live sitemap integration")
    print("for all priority keywords from your cluster analysis.")
    print()
    
    # Ask user for preferences
    start_from = input("Start from keyword number (default 0): ").strip()
    start_from = int(start_from) if start_from.isdigit() else 0
    
    max_keywords = input("Maximum keywords to process (default all): ").strip()
    max_keywords = int(max_keywords) if max_keywords.isdigit() else None
    
    print(f"\n🚀 Starting batch generation with live sitemap...")
    print(f"📊 Processing keywords {start_from + 1} to {start_from + (max_keywords or len(batch_generator.priority_keywords))}")
    print()
    
    # Confirm before starting
    confirm = input("Proceed with batch generation? (y/N): ").strip().lower()
    if confirm != 'y':
        print("❌ Batch generation cancelled.")
        return
    
    # Run batch generation
    results = batch_generator.generate_all_live_sitemap_briefs(
        start_from=start_from,
        max_keywords=max_keywords
    )
    
    print(f"\n🎉 Batch generation with live sitemap complete!")
    print(f"📊 Check the generated report for details")

if __name__ == "__main__":
    main()
