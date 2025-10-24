#!/usr/bin/env python3
"""
Simple Live Sitemap Brief Generator

This script generates a brief with live sitemap internal linking without
the full DataForSEO API integration to avoid long processing times.
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from live_sitemap_internal_links import LiveSitemapInternalLinker

def generate_simple_live_sitemap_brief(primary_keyword, target_audience="Technical decision-makers", content_goal="Educational"):
    """Generate a simple brief with live sitemap integration"""
    
    print(f"🚀 Generating Simple Brief with Live Sitemap for: {primary_keyword}")
    print("=" * 70)
    
    # Initialize the linker
    linker = LiveSitemapInternalLinker()
    
    # Get sitemap statistics
    print("📊 Fetching live sitemap data...")
    stats = linker.get_sitemap_statistics()
    print(f"✅ Sitemap loaded: {stats['total_pages']} pages, {stats['recent_pages']} recent")
    
    # Get internal link recommendations
    print(f"\n🔗 Finding relevant internal links for '{primary_keyword}'...")
    recommendations = linker.get_relevant_internal_links(
        primary_keyword=primary_keyword,
        target_audience=target_audience,
        content_goal=content_goal,
        num_links=5
    )
    
    # Create the brief
    safe_keyword = primary_keyword.lower().replace(" ", "-")
    brief_filename = f"{safe_keyword}-live-sitemap-brief.md"
    
    brief_content = f"""# SEO Content Brief: {primary_keyword}

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Target Audience:** {target_audience}
**Content Goal:** {content_goal}

---

## 🌐 Live Sitemap Data

**Sitemap Last Updated:** {stats['last_fetch']}
**Total Pages Available:** {stats['total_pages']}
**Recent Pages (Oct 2025):** {stats['recent_pages']}

### Categories Available:
"""
    
    for category, count in stats['categories'].items():
        brief_content += f"- **{category}:** {count} pages\n"
    
    brief_content += f"""

---

## 🔗 Recommended Internal Links

*Based on live sitemap data from io.net*

"""
    
    if recommendations:
        for i, link in enumerate(recommendations, 1):
            brief_content += f"""### {i}. {link.get('title', 'N/A')}

- **URL:** {link.get('url', 'N/A')}
- **Anchor Text:** "{link.get('anchor_text', 'N/A')}"
- **Category:** {link.get('category', 'N/A')}
- **Priority:** {link.get('priority', 'N/A')}
- **Last Modified:** {link.get('last_modified', 'N/A')}
- **Strategic Reason:** {link.get('strategic_reason', 'N/A')}

"""
    else:
        brief_content += "No internal link recommendations found.\n\n"
    
    brief_content += f"""---

## 📋 Content Strategy

### Primary Keyword: {primary_keyword}
- **Target Audience:** {target_audience}
- **Content Goal:** {content_goal}
- **Internal Links Available:** {len(recommendations) if recommendations else 0}

### Recommended Content Structure:
1. **Introduction** - Define the topic and its importance
2. **Main Comparison/Analysis** - Core content addressing the keyword
3. **Supporting Sections** - Use internal links to provide additional context
4. **Conclusion** - Summarize key points and next steps

### Internal Linking Strategy:
- Use the recommended anchor texts naturally within the content
- Place links contextually where they add value
- Prioritize high-priority, recently updated pages
- Ensure links support the user journey and content goal

---

## 🎯 Next Steps

1. **Review Internal Links:** Check all recommended pages for relevance
2. **Plan Content Structure:** Organize content around the internal links
3. **Write Content:** Create high-quality content using the recommendations
4. **Monitor Performance:** Track rankings and internal link performance

---

*This brief was generated using live sitemap data from io.net for the most current internal linking opportunities.*
"""
    
    # Save the brief
    with open(brief_filename, 'w', encoding='utf-8') as f:
        f.write(brief_content)
    
    print(f"✅ Brief saved: {brief_filename}")
    print(f"📄 Internal links found: {len(recommendations) if recommendations else 0}")
    
    return brief_filename, recommendations

def main():
    """Main function"""
    print("🌐 Simple Live Sitemap Brief Generator")
    print("=" * 50)
    
    # Use the specified keyword
    keyword = "gpu vs cpu for ai"
    print(f"🎯 Generating brief for: {keyword}")
    
    # Generate the brief
    brief_file, recommendations = generate_simple_live_sitemap_brief(
        primary_keyword=keyword,
        target_audience="Technical decision-makers and developers",
        content_goal="Educational comparison and decision-making guide"
    )
    
    print(f"\n🎉 Brief generation complete!")
    print(f"📄 Brief file: {brief_file}")
    if recommendations:
        print(f"🔗 Internal links: {len(recommendations)} recommendations")
        print("\nTop recommendations:")
        for i, rec in enumerate(recommendations[:3], 1):
            print(f"{i}. {rec['title']}")

if __name__ == "__main__":
    main()
