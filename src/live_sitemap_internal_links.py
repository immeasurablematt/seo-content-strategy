#!/usr/bin/env python3
"""
Live Sitemap Internal Link Analyzer for io.net

This script fetches the live sitemap from io.net/sitemap.xml and uses it
to provide current, up-to-date internal linking recommendations.
"""

import os
import json
import xml.etree.ElementTree as ET
import requests
from typing import List, Dict, Any
from urllib.parse import urlparse
from anthropic import Anthropic
from dotenv import load_dotenv
from datetime import datetime
import time

load_dotenv()

class LiveSitemapInternalLinker:
    def __init__(self):
        self.anthropic_client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.sitemap_url = "http://io.net/sitemap.xml"
        self.internal_pages = []
        self.last_fetch_time = None
        
    def fetch_live_sitemap(self) -> List[Dict]:
        """Fetch and parse the live sitemap from io.net"""
        print(f"🌐 Fetching live sitemap from {self.sitemap_url}...")
        
        try:
            response = requests.get(self.sitemap_url, timeout=10)
            response.raise_for_status()
            
            # Parse XML sitemap
            root = ET.fromstring(response.content)
            
            # Define namespace
            ns = {'sitemap': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            
            pages = []
            for url_elem in root.findall('.//sitemap:url', ns):
                loc_elem = url_elem.find('sitemap:loc', ns)
                lastmod_elem = url_elem.find('sitemap:lastmod', ns)
                changefreq_elem = url_elem.find('sitemap:changefreq', ns)
                priority_elem = url_elem.find('sitemap:priority', ns)
                
                if loc_elem is not None:
                    url = loc_elem.text
                    parsed_url = urlparse(url)
                    
                    # Only include io.net pages
                    if 'io.net' in parsed_url.netloc:
                        page_data = {
                            'url': url,
                            'title': self.extract_title_from_url(url),
                            'last_modified': lastmod_elem.text if lastmod_elem is not None else None,
                            'change_frequency': changefreq_elem.text if changefreq_elem is not None else 'unknown',
                            'priority': priority_elem.text if priority_elem is not None else '0.5',
                            'category': self.categorize_page_by_url(url),
                            'keywords': self.extract_keywords_from_url(url)
                        }
                        pages.append(page_data)
            
            self.internal_pages = pages
            self.last_fetch_time = datetime.now()
            
            print(f"✅ Successfully fetched {len(pages)} pages from live sitemap")
            print(f"📅 Last updated: {self.last_fetch_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            return pages
            
        except requests.RequestException as e:
            print(f"❌ Error fetching sitemap: {e}")
            return []
        except ET.ParseError as e:
            print(f"❌ Error parsing XML: {e}")
            return []
    
    def extract_title_from_url(self, url: str) -> str:
        """Extract a readable title from the URL"""
        parsed = urlparse(url)
        path_parts = parsed.path.strip('/').split('/')
        
        # Remove common prefixes and format
        if path_parts[-1] in ['', 'index.html', 'index.php']:
            path_parts = path_parts[:-1]
        
        if not path_parts:
            return "Homepage"
        
        # Get the last meaningful part
        title_part = path_parts[-1]
        
        # Clean up the title
        title = title_part.replace('-', ' ').replace('_', ' ')
        title = ' '.join(word.capitalize() for word in title.split())
        
        return title
    
    def categorize_page_by_url(self, url: str) -> str:
        """Categorize page based on URL structure"""
        parsed = urlparse(url)
        path = parsed.path.lower()
        
        if path == '/' or path == '':
            return "Main"
        elif '/blog/' in path:
            return "Blog"
        elif '/docs/' in path:
            return "Docs"
        elif '/events/' in path:
            return "Events"
        elif '/cloud/' in path:
            return "App"
        elif '/explorer/' in path:
            return "Explorer"
        elif '/worker/' in path:
            return "App"
        elif '/ai/' in path:
            return "App"
        elif path in ['/about-us', '/team', '/careers', '/mission']:
            return "Main"
        elif path in ['/faq', '/contact-us', '/privacy-policy', '/terms-of-service']:
            return "Support"
        elif path in ['/hackathon', '/media-kit', '/brand-assets']:
            return "Community"
        else:
            return "Other"
    
    def extract_keywords_from_url(self, url: str) -> str:
        """Extract potential keywords from URL structure"""
        parsed = urlparse(url)
        path_parts = parsed.path.strip('/').split('/')
        
        # Filter out common words and extract meaningful terms
        meaningful_parts = []
        for part in path_parts:
            if part not in ['', 'index.html', 'index.php', 'blog', 'docs', 'events']:
                # Clean and add meaningful parts
                clean_part = part.replace('-', ' ').replace('_', ' ')
                meaningful_parts.append(clean_part)
        
        return ', '.join(meaningful_parts)
    
    def get_relevant_internal_links(self, primary_keyword: str, target_audience: str, 
                                   content_goal: str, num_links: int = 5) -> List[Dict]:
        """Get relevant internal links using live sitemap data"""
        print(f"\n🔗 Finding relevant internal links for '{primary_keyword}' using live sitemap...")
        
        # Ensure we have fresh sitemap data (fetch if older than 1 hour)
        if not self.internal_pages or self.should_refresh_sitemap():
            self.fetch_live_sitemap()
        
        if not self.internal_pages:
            print("⚠️ No internal pages available")
            return []
        
        # Prepare pages data for Claude
        pages_str = "\n".join([
            f"{i+1}. [{p['title']}]({p['url']}) - {p['category']} - Priority: {p['priority']} - Last Modified: {p['last_modified']}"
            for i, p in enumerate(self.internal_pages[:50])  # Limit to top 50 for performance
        ])
        
        prompt = f"""You are an SEO expert analyzing internal linking opportunities using live sitemap data.

PRIMARY KEYWORD: {primary_keyword}
TARGET AUDIENCE: {target_audience}
CONTENT GOAL: {content_goal}

LIVE SITEMAP PAGES (Top 50 by Priority):
{pages_str}

Task: Select the {num_links} MOST RELEVANT pages from the list above to internally link to from an article about "{primary_keyword}".

Consider:
1. **Recency**: Pages with recent last_modified dates are more valuable
2. **Priority**: Higher priority pages should be prioritized for internal linking
3. **Relevance**: Match page content with the target keyword and audience
4. **Category**: Prefer Blog, Docs, and App pages for content articles

For each selected page, provide:
1. The page title and URL (exactly as shown above)
2. Suggested anchor text (natural, contextual, includes relevant keywords)
3. Strategic reason for including this link

Return ONLY a JSON array in this exact format:
[
  {{
    "title": "Page Title",
    "url": "https://io.net/...",
    "anchor_text": "suggested anchor text",
    "strategic_reason": "why this link is valuable for SEO and user experience",
    "category": "Blog|Docs|App|Main|Support|Community",
    "priority": "0.9",
    "last_modified": "2025-10-22T13:01:45.781Z"
  }}
]

Focus on pages that:
- Are recently updated (high last_modified values)
- Have high priority scores
- Are relevant to the target keyword and audience
- Provide value to users reading about the topic"""

        try:
            response = self.anthropic_client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = response.content[0].text.strip()
            
            # Extract JSON from response
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            links = json.loads(response_text)
            print(f"✅ Found {len(links)} relevant internal links from live sitemap")
            return links
            
        except Exception as e:
            print(f"⚠️ Error finding internal links: {str(e)}")
            return []
    
    def should_refresh_sitemap(self) -> bool:
        """Check if sitemap should be refreshed (older than 1 hour)"""
        if not self.last_fetch_time:
            return True
        
        time_diff = datetime.now() - self.last_fetch_time
        return time_diff.total_seconds() > 3600  # 1 hour
    
    def get_sitemap_statistics(self) -> Dict:
        """Get statistics about the current sitemap"""
        if not self.internal_pages:
            self.fetch_live_sitemap()
        
        categories = {}
        priorities = {}
        
        for page in self.internal_pages:
            # Count by category
            category = page['category']
            categories[category] = categories.get(category, 0) + 1
            
            # Count by priority
            priority = page['priority']
            priorities[priority] = priorities.get(priority, 0) + 1
        
        return {
            'total_pages': len(self.internal_pages),
            'last_fetch': self.last_fetch_time.strftime('%Y-%m-%d %H:%M:%S') if self.last_fetch_time else 'Never',
            'categories': categories,
            'priorities': priorities,
            'recent_pages': len([p for p in self.internal_pages if p['last_modified'] and '2025-10' in p['last_modified']])
        }
    
    def save_sitemap_cache(self, filename: str = None):
        """Save current sitemap data to cache file"""
        if not filename:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'sitemap_cache_{timestamp}.json'
        
        cache_data = {
            'pages': self.internal_pages,
            'last_fetch': self.last_fetch_time.isoformat() if self.last_fetch_time else None,
            'sitemap_url': self.sitemap_url
        }
        
        with open(filename, 'w') as f:
            json.dump(cache_data, f, indent=2)
        
        print(f"✅ Sitemap cache saved to: {filename}")
        return filename

def main():
    """Main function to demonstrate live sitemap internal linking"""
    linker = LiveSitemapInternalLinker()
    
    print("🌐 Live Sitemap Internal Link Analyzer for io.net")
    print("=" * 60)
    
    # Fetch live sitemap
    pages = linker.fetch_live_sitemap()
    
    if pages:
        # Show statistics
        stats = linker.get_sitemap_statistics()
        print(f"\n📊 Sitemap Statistics:")
        print(f"Total Pages: {stats['total_pages']}")
        print(f"Last Fetch: {stats['last_fetch']}")
        print(f"Recent Pages (Oct 2025): {stats['recent_pages']}")
        print(f"\nCategories:")
        for category, count in stats['categories'].items():
            print(f"  {category}: {count}")
        
        # Test internal link recommendations
        test_keyword = "gpu vs cpu for ai"
        print(f"\n🔗 Testing internal link recommendations for: {test_keyword}")
        
        recommendations = linker.get_relevant_internal_links(
            primary_keyword=test_keyword,
            target_audience="Technical decision-makers and developers",
            content_goal="Educational comparison and decision-making guide"
        )
        
        if recommendations:
            print(f"\n✅ Found {len(recommendations)} relevant internal links:")
            for i, link in enumerate(recommendations, 1):
                print(f"{i}. {link['title']}")
                print(f"   URL: {link['url']}")
                print(f"   Anchor: \"{link['anchor_text']}\"")
                print(f"   Category: {link['category']} (Priority: {link['priority']})")
                print(f"   Reason: {link['strategic_reason']}")
                print()
        
        # Save cache
        linker.save_sitemap_cache()
        
        print(f"\n🎉 Live sitemap analysis complete!")
        print(f"📄 Use this data for up-to-date internal linking recommendations")
    
    else:
        print("❌ Failed to fetch sitemap data")

if __name__ == "__main__":
    main()
