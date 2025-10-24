#!/usr/bin/env python3
"""
Simple test script to verify live sitemap functionality
"""

import os
import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from live_sitemap_internal_links import LiveSitemapInternalLinker

def test_live_sitemap():
    """Test the live sitemap functionality"""
    print("🧪 Testing Live Sitemap Functionality")
    print("=" * 50)
    
    # Initialize the linker
    linker = LiveSitemapInternalLinker()
    
    # Test 1: Fetch sitemap
    print("Test 1: Fetching live sitemap...")
    pages = linker.fetch_live_sitemap()
    
    if pages:
        print(f"✅ Successfully fetched {len(pages)} pages")
        
        # Show sample pages
        print("\nSample pages:")
        for i, page in enumerate(pages[:5]):
            print(f"{i+1}. {page['title']} - {page['url']}")
        
        # Test 2: Get statistics
        print("\nTest 2: Getting sitemap statistics...")
        stats = linker.get_sitemap_statistics()
        print(f"✅ Statistics: {stats['total_pages']} pages, {stats['recent_pages']} recent")
        
        # Test 3: Get internal link recommendations
        print("\nTest 3: Getting internal link recommendations...")
        recommendations = linker.get_relevant_internal_links(
            primary_keyword="gpu vs cpu for ai",
            target_audience="Technical decision-makers",
            content_goal="Educational comparison",
            num_links=3
        )
        
        if recommendations:
            print(f"✅ Found {len(recommendations)} recommendations:")
            for i, rec in enumerate(recommendations, 1):
                print(f"{i}. {rec['title']}")
                print(f"   URL: {rec['url']}")
                print(f"   Anchor: \"{rec['anchor_text']}\"")
        else:
            print("❌ No recommendations found")
        
        print("\n🎉 Live sitemap test completed successfully!")
        
    else:
        print("❌ Failed to fetch sitemap")

if __name__ == "__main__":
    test_live_sitemap()
