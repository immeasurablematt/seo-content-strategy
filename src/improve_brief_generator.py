#!/usr/bin/env python3
"""
Enhanced Brief Generator with Improved Internal Linking

This script enhances the existing brief generator to provide more strategic
internal linking recommendations based on topic clusters and content strategy.
"""

import os
import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from simple_seo_brief import run_with_parameters
from enhanced_internal_links import EnhancedInternalLinker

class ImprovedBriefGenerator:
    def __init__(self):
        self.internal_linker = EnhancedInternalLinker()
    
    def generate_enhanced_brief(self, primary_keyword: str, target_audience: str = None, 
                               content_goal: str = None, your_domain: str = "io.net"):
        """Generate an enhanced brief with strategic internal linking"""
        
        print(f"\n🚀 Generating enhanced brief for: {primary_keyword}")
        print("=" * 60)
        
        # Step 1: Generate the standard brief
        print("Step 1: Generating standard content brief...")
        run_with_parameters(
            primary_keyword=primary_keyword,
            target_audience=target_audience,
            content_goal=content_goal,
            your_domain=your_domain
        )
        
        # Step 2: Generate enhanced internal linking analysis
        print("\nStep 2: Generating enhanced internal linking analysis...")
        
        # Determine cluster for this keyword
        cluster = self.internal_linker.determine_cluster_for_keyword(primary_keyword)
        
        # Get strategic internal linking recommendations
        link_recommendations = self.internal_linker.analyze_cluster_links(
            primary_keyword, cluster, target_audience or "Technical decision-makers"
        )
        
        # Step 3: Create enhanced brief with strategic internal linking
        self.create_enhanced_brief_file(primary_keyword, link_recommendations, cluster)
        
        print(f"\n✅ Enhanced brief generation complete!")
        print(f"📄 Check the generated files for your comprehensive brief")
        
        return link_recommendations
    
    def create_enhanced_brief_file(self, keyword: str, link_recommendations: Dict, cluster: str):
        """Create an enhanced brief file with strategic internal linking"""
        
        safe_keyword = keyword.lower().replace(" ", "-")
        enhanced_filename = f"{safe_keyword}-enhanced-brief.md"
        
        # Create enhanced brief content
        enhanced_content = f"""# Enhanced SEO Brief: {keyword}

## 🎯 Strategic Internal Linking Analysis

**Cluster:** {cluster}
**Generated:** {__import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## 🔗 Strategic Internal Linking Recommendations

### Pillar Content Links
*These links help build topical authority and distribute link equity to your most important content.*

"""
        
        if "pillar_content" in link_recommendations:
            for link in link_recommendations["pillar_content"]:
                enhanced_content += f"""#### {link.get('title', 'N/A')}
- **URL:** {link.get('url', 'N/A')}
- **Anchor Text:** "{link.get('anchor_text', 'N/A')}"
- **Placement:** {link.get('placement', 'N/A')}
- **Strategic Purpose:** {link.get('strategic_purpose', 'N/A')}

"""
        
        enhanced_content += """### Supporting Content Links
*These links provide additional context and value to users.*

"""
        
        if "supporting_content" in link_recommendations:
            for link in link_recommendations["supporting_content"]:
                enhanced_content += f"""#### {link.get('title', 'N/A')}
- **URL:** {link.get('url', 'N/A')}
- **Anchor Text:** "{link.get('anchor_text', 'N/A')}"
- **Placement:** {link.get('placement', 'N/A')}
- **Strategic Purpose:** {link.get('strategic_purpose', 'N/A')}

"""
        
        enhanced_content += """### Product/Service Links
*These links drive users to relevant io.net products and services.*

"""
        
        if "product_service" in link_recommendations:
            for link in link_recommendations["product_service"]:
                enhanced_content += f"""#### {link.get('title', 'N/A')}
- **URL:** {link.get('url', 'N/A')}
- **Anchor Text:** "{link.get('anchor_text', 'N/A')}"
- **Placement:** {link.get('placement', 'N/A')}
- **Strategic Purpose:** {link.get('strategic_purpose', 'N/A')}

"""
        
        enhanced_content += """### Resource Links
*These links provide additional resources and documentation.*

"""
        
        if "resources" in link_recommendations:
            for link in link_recommendations["resources"]:
                enhanced_content += f"""#### {link.get('title', 'N/A')}
- **URL:** {link.get('url', 'N/A')}
- **Anchor Text:** "{link.get('anchor_text', 'N/A')}"
- **Placement:** {link.get('placement', 'N/A')}
- **Strategic Purpose:** {link.get('strategic_purpose', 'N/A')}

"""
        
        enhanced_content += f"""---

## 📊 Link Equity Strategy

{link_recommendations.get('link_equity_strategy', 'Strategic link equity distribution to build topical authority.')}

## 🎯 User Journey Optimization

{link_recommendations.get('user_journey_optimization', 'Optimized internal linking to guide users through the conversion funnel.')}

---

## 📋 Implementation Checklist

- [ ] Review standard brief: `{safe_keyword}-brief.md`
- [ ] Implement pillar content links in introduction and conclusion
- [ ] Add supporting content links throughout the body
- [ ] Include product/service links in relevant sections
- [ ] Add resource links where appropriate
- [ ] Monitor internal link performance
- [ ] Track user journey through linked pages

---

*This enhanced brief was generated using the io.net Content Strategy Tool with strategic internal linking analysis.*
"""
        
        # Save enhanced brief
        with open(enhanced_filename, 'w', encoding='utf-8') as f:
            f.write(enhanced_content)
        
        print(f"✅ Enhanced brief saved: {enhanced_filename}")
        
        return enhanced_filename

def main():
    """Main function to run enhanced brief generation"""
    generator = ImprovedBriefGenerator()
    
    # Example usage
    print("🎯 Enhanced Brief Generator for io.net")
    print("=" * 50)
    
    # Get keyword from user or use default
    keyword = input("Enter your primary keyword (or press Enter for 'gpu vs cpu for ai'): ").strip()
    if not keyword:
        keyword = "gpu vs cpu for ai"
    
    # Generate enhanced brief
    recommendations = generator.generate_enhanced_brief(
        primary_keyword=keyword,
        target_audience="Technical decision-makers and developers",
        content_goal="Educational and commercial"
    )
    
    print(f"\n🎉 Enhanced brief generation complete!")
    print(f"📄 Check the generated files for your comprehensive brief with strategic internal linking")

if __name__ == "__main__":
    main()
