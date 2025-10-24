#!/usr/bin/env python3
"""
Batch Enhanced Brief Generator for io.net Priority Keywords

This script generates enhanced content briefs with strategic internal linking
for all priority keywords from your cluster analysis.
"""

import os
import sys
import time
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from improve_brief_generator import ImprovedBriefGenerator

class BatchEnhancedBriefGenerator:
    def __init__(self):
        self.generator = ImprovedBriefGenerator()
        
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
    
    def generate_all_enhanced_briefs(self, start_from: int = 0, max_keywords: int = None):
        """Generate enhanced briefs for all priority keywords"""
        
        print("🚀 Batch Enhanced Brief Generator for io.net")
        print("=" * 60)
        print(f"📊 Total keywords to process: {len(self.priority_keywords)}")
        print(f"🎯 Starting from keyword {start_from + 1}")
        
        if max_keywords:
            keywords_to_process = self.priority_keywords[start_from:start_from + max_keywords]
        else:
            keywords_to_process = self.priority_keywords[start_from:]
        
        print(f"📝 Processing {len(keywords_to_process)} keywords...")
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
                # Generate enhanced brief
                recommendations = self.generator.generate_enhanced_brief(
                    primary_keyword=keyword,
                    target_audience=keyword_data["target_audience"],
                    content_goal=keyword_data["content_goal"]
                )
                
                results.append({
                    "keyword": keyword,
                    "cluster": cluster,
                    "priority": priority,
                    "status": "SUCCESS",
                    "recommendations": recommendations
                })
                
                print(f"✅ Successfully generated brief for: {keyword}")
                
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
        self.generate_summary_report(results)
        
        return results
    
    def generate_summary_report(self, results: list):
        """Generate a summary report of all brief generations"""
        
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_filename = f'batch_brief_generation_report_{timestamp}.md'
        
        successful = [r for r in results if r["status"] == "SUCCESS"]
        failed = [r for r in results if r["status"] == "ERROR"]
        
        report_content = f"""# Batch Enhanced Brief Generation Report

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Total Keywords Processed:** {len(results)}
**Successful:** {len(successful)}
**Failed:** {len(failed)}

---

## 📊 Summary Statistics

- **Success Rate:** {(len(successful) / len(results) * 100):.1f}%
- **Total Briefs Generated:** {len(successful)}
- **Keywords Failed:** {len(failed)}

---

## ✅ Successfully Generated Briefs

"""
        
        for result in successful:
            report_content += f"""### {result['keyword']}
- **Cluster:** {result['cluster']}
- **Priority:** {result['priority']}
- **Status:** ✅ SUCCESS
- **Files Generated:** 
  - `{result['keyword'].lower().replace(' ', '-')}-brief.md`
  - `{result['keyword'].lower().replace(' ', '-')}-enhanced-brief.md`

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
2. **Implement Content Strategy:** Use the briefs to create high-quality content
3. **Strategic Internal Linking:** Follow the enhanced internal linking recommendations
4. **Monitor Performance:** Track rankings and traffic for each keyword
5. **Iterate and Improve:** Refine strategy based on results

---

## 📁 Generated Files

Each successful brief generation creates two files:
- `{keyword}-brief.md` - Standard SEO content brief
- `{keyword}-enhanced-brief.md` - Enhanced brief with strategic internal linking

---

*This report was generated by the io.net Content Strategy Tool.*
"""
        
        # Save report
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"📊 Summary report saved: {report_filename}")
        
        return report_filename

def main():
    """Main function to run batch brief generation"""
    batch_generator = BatchEnhancedBriefGenerator()
    
    print("🎯 Batch Enhanced Brief Generator")
    print("=" * 40)
    print("This will generate enhanced briefs with strategic internal linking")
    print("for all priority keywords from your cluster analysis.")
    print()
    
    # Ask user for preferences
    start_from = input("Start from keyword number (default 0): ").strip()
    start_from = int(start_from) if start_from.isdigit() else 0
    
    max_keywords = input("Maximum keywords to process (default all): ").strip()
    max_keywords = int(max_keywords) if max_keywords.isdigit() else None
    
    print(f"\n🚀 Starting batch generation...")
    print(f"📊 Processing keywords {start_from + 1} to {start_from + (max_keywords or len(batch_generator.priority_keywords))}")
    print()
    
    # Confirm before starting
    confirm = input("Proceed with batch generation? (y/N): ").strip().lower()
    if confirm != 'y':
        print("❌ Batch generation cancelled.")
        return
    
    # Run batch generation
    results = batch_generator.generate_all_enhanced_briefs(
        start_from=start_from,
        max_keywords=max_keywords
    )
    
    print(f"\n🎉 Batch generation complete!")
    print(f"📊 Check the generated report for details")

if __name__ == "__main__":
    main()
