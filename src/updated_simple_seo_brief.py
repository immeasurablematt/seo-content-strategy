#!/usr/bin/env python3
"""
Updated Simple SEO Brief Generator with Live Sitemap Integration

This script updates the existing simple_seo_brief.py to use live sitemap data
instead of static CSV files for internal linking recommendations.
"""

import os
import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import the live sitemap linker
from live_sitemap_internal_links import LiveSitemapInternalLinker

def load_internal_pages_from_sitemap():
    """Load internal pages from live sitemap instead of CSV"""
    print("🌐 Loading internal pages from live sitemap...")
    
    linker = LiveSitemapInternalLinker()
    pages = linker.fetch_live_sitemap()
    
    if pages:
        # Convert to the format expected by the existing brief generator
        formatted_pages = []
        for page in pages:
            formatted_pages.append({
                'title': page['title'],
                'url': page['url'],
                'description': f"Category: {page['category']}, Priority: {page['priority']}",
                'keywords': page['keywords']
            })
        
        print(f"✅ Loaded {len(formatted_pages)} internal pages from live sitemap")
        return formatted_pages
    else:
        print("⚠️ Failed to load pages from sitemap, falling back to CSV")
        return load_internal_pages_from_csv()

def load_internal_pages_from_csv():
    """Fallback to CSV if sitemap fails"""
    import pandas as pd
    
    csv_paths = [
        "data/Internal-Links-Oct-10- 2025.csv",
        "Internal-Links-Oct-10- 2025.csv",
        "io_net_pages.csv"
    ]
    
    for csv_path in csv_paths:
        if os.path.exists(csv_path):
            try:
                df = pd.read_csv(csv_path)
                pages = []
                for _, row in df.iterrows():
                    pages.append({
                        'title': row.get('Page Title', ''),
                        'url': row.get('URL', ''),
                        'description': row.get('Description', ''),
                        'keywords': row.get('Keywords', '')
                    })
                print(f"✅ Loaded {len(pages)} internal pages from CSV: {csv_path}")
                return pages
            except Exception as e:
                print(f"⚠️ Error loading CSV {csv_path}: {e}")
                continue
    
    print("❌ No internal pages loaded")
    return []

def find_relevant_internal_links_with_sitemap(primary_keyword, target_audience, content_goal, num_links=5):
    """Enhanced internal link finding using live sitemap data"""
    print(f"\n🔗 Finding relevant internal links for '{primary_keyword}' using live sitemap...")
    
    linker = LiveSitemapInternalLinker()
    recommendations = linker.get_relevant_internal_links(
        primary_keyword=primary_keyword,
        target_audience=target_audience,
        content_goal=content_goal,
        num_links=num_links
    )
    
    if recommendations:
        print(f"✅ Found {len(recommendations)} relevant internal links from live sitemap")
        return recommendations
    else:
        print("⚠️ No recommendations from sitemap, falling back to basic analysis")
        return []

def run_enhanced_brief_with_sitemap(primary_keyword, target_audience=None, content_goal=None, your_domain="io.net"):
    """Run the brief generation with live sitemap integration"""
    
    print("🚀 Enhanced SEO Brief Generator with Live Sitemap Integration")
    print("=" * 70)
    print(f"🎯 Primary Keyword: {primary_keyword}")
    print(f"👥 Target Audience: {target_audience or 'Auto-detected'}")
    print(f"🎯 Content Goal: {content_goal or 'Auto-detected'}")
    print(f"🌐 Domain: {your_domain}")
    print()
    
    # Step 1: Show sitemap statistics
    linker = LiveSitemapInternalLinker()
    stats = linker.get_sitemap_statistics()
    
    print("📊 Live Sitemap Statistics:")
    print(f"Total Pages: {stats['total_pages']}")
    print(f"Last Fetch: {stats['last_fetch']}")
    print(f"Recent Pages (Oct 2025): {stats['recent_pages']}")
    print(f"Categories: {', '.join(stats['categories'].keys())}")
    print()
    
    # Step 2: Run the standard brief generation
    print("Step 1: Generating standard content brief...")
    print("⏳ This may take 5-10 minutes due to API calls...")
    
    try:
        # Import and run the main function from simple_seo_brief
        from simple_seo_brief import main as simple_seo_main
        simple_seo_main(
            primary_keyword=primary_keyword,
            target_audience=target_audience,
            content_goal=content_goal,
            your_domain=your_domain
        )
        print("✅ Standard brief generation completed")
    except KeyboardInterrupt:
        print("\n⚠️ Brief generation interrupted by user")
        print("Continuing with live sitemap analysis...")
    except Exception as e:
        print(f"⚠️ Standard brief generation failed: {e}")
        print("Continuing with live sitemap analysis...")
    
    # Step 3: Generate enhanced internal linking analysis
    print("\nStep 2: Generating enhanced internal linking analysis with live sitemap...")
    
    recommendations = find_relevant_internal_links_with_sitemap(
        primary_keyword=primary_keyword,
        target_audience=target_audience or "Technical decision-makers",
        content_goal=content_goal or "Educational and commercial"
    )
    
    # Step 4: Update the main brief file with live sitemap recommendations
    if recommendations:
        update_main_brief_with_sitemap(primary_keyword, recommendations, stats)
    
    print(f"\n✅ Enhanced brief generation with live sitemap complete!")
    print(f"📄 Check the main brief file for comprehensive content with live sitemap recommendations")
    
    return recommendations

def update_main_brief_with_sitemap(keyword, recommendations, sitemap_stats):
    """Update the main brief file with live sitemap recommendations"""
    
    safe_keyword = keyword.lower().replace(" ", "-")
    main_brief_filename = f"{safe_keyword}-brief.md"
    
    # Check if the main brief file exists
    if not os.path.exists(main_brief_filename):
        print(f"⚠️ Main brief file not found: {main_brief_filename}")
        return
    
    # Read the existing brief
    with open(main_brief_filename, 'r', encoding='utf-8') as f:
        brief_content = f.read()
    
    # Create the live sitemap section
    sitemap_section = f"""

---

## 🌐 Live Sitemap Internal Linking Recommendations

*These recommendations are based on the most current sitemap data from io.net*

**Sitemap Last Updated:** {sitemap_stats['last_fetch']}
**Total Pages Available:** {sitemap_stats['total_pages']}
**Recent Pages (Oct 2025):** {sitemap_stats['recent_pages']}

### 🔗 Strategic Internal Links

"""
    
    if recommendations:
        for i, link in enumerate(recommendations, 1):
            sitemap_section += f"""#### {i}. {link.get('title', 'N/A')}

- **URL:** {link.get('url', 'N/A')}
- **Anchor Text:** "{link.get('anchor_text', 'N/A')}"
- **Category:** {link.get('category', 'N/A')}
- **Priority:** {link.get('priority', 'N/A')}
- **Last Modified:** {link.get('last_modified', 'N/A')}
- **Strategic Reason:** {link.get('strategic_reason', 'N/A')}

"""
    else:
        sitemap_section += "No internal link recommendations found.\n\n"
    
    sitemap_section += f"""### 📊 Live Sitemap Statistics

**Categories Available:**
"""
    
    for category, count in sitemap_stats['categories'].items():
        sitemap_section += f"- **{category}:** {count} pages\n"
    
    sitemap_section += f"""

**Priority Distribution:**
"""
    
    for priority, count in sitemap_stats['priorities'].items():
        sitemap_section += f"- **Priority {priority}:** {count} pages\n"
    
    sitemap_section += f"""

### 🎯 Implementation Strategy

1. **Use Live Data:** These recommendations are based on the most current sitemap
2. **Prioritize Recent Content:** Focus on pages with recent last_modified dates  
3. **High Priority Pages:** Give preference to pages with high priority scores
4. **Category Relevance:** Match page categories with your content type
5. **Strategic Placement:** Use the strategic reasons to guide link placement

### 📋 Implementation Checklist

- [ ] Implement live sitemap recommendations above
- [ ] Prioritize high-priority, recently updated pages
- [ ] Use strategic anchor text suggestions
- [ ] Monitor internal link performance
- [ ] Refresh sitemap data weekly for new content

### 🔄 Keeping Recommendations Current

This brief uses live sitemap data that includes:
- **{sitemap_stats['total_pages']} total pages** from io.net
- **{sitemap_stats['recent_pages']} recently updated pages** (October 2025)
- **Real-time priority scores** and modification dates
- **Automatic updates** when new content is published

To keep recommendations current, re-run this analysis weekly or before major content campaigns.

---

*Live sitemap integration powered by the io.net Content Strategy Tool.*
"""
    
    # Append the sitemap section to the existing brief
    updated_brief_content = brief_content + sitemap_section
    
    # Write the updated brief back to the file
    with open(main_brief_filename, 'w', encoding='utf-8') as f:
        f.write(updated_brief_content)
    
    print(f"✅ Updated main brief with live sitemap recommendations: {main_brief_filename}")
    
    return main_brief_filename

def main():
    """Main function to run enhanced brief generation with live sitemap"""
    print("🌐 Enhanced SEO Brief Generator with Live Sitemap Integration")
    print("=" * 70)
    
    # Use default keyword for automated execution
    keyword = "gpu vs cpu for ai"
    print(f"🎯 Using keyword: {keyword}")
    
    # Generate enhanced brief with live sitemap
    recommendations = run_enhanced_brief_with_sitemap(
        primary_keyword=keyword,
        target_audience="Technical decision-makers and developers",
        content_goal="Educational and commercial"
    )
    
    print(f"\n🎉 Enhanced brief generation with live sitemap complete!")
    print(f"📄 Check the generated files for your comprehensive brief with current internal linking")

if __name__ == "__main__":
    main()
