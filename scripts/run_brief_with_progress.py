#!/usr/bin/env python3
"""
Run Brief Generator with Progress Tracking

This script runs the updated brief generator with progress tracking
and better error handling.
"""

import os
import sys
import time
import signal
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print('\n⚠️ Script interrupted by user')
    print('Continuing with live sitemap analysis...')
    return True

def run_brief_with_progress():
    """Run the brief generator with progress tracking"""
    
    print("🚀 Running Enhanced SEO Brief Generator")
    print("=" * 50)
    print("⏳ This process includes:")
    print("   1. Live sitemap fetching (30 seconds)")
    print("   2. DataForSEO API calls (3-5 minutes)")
    print("   3. Claude AI analysis (2-3 minutes)")
    print("   4. Content brief generation (1-2 minutes)")
    print("   5. Live sitemap internal linking (1 minute)")
    print()
    print("⏰ Total estimated time: 7-11 minutes")
    print("Press Ctrl+C to skip the full brief and go straight to live sitemap analysis")
    print()
    
    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Import and run the updated brief generator
        from updated_simple_seo_brief import run_enhanced_brief_with_sitemap
        
        print("🎯 Starting brief generation for: gpu vs cpu for ai")
        print("⏳ Beginning API calls...")
        
        # Run the brief generator
        recommendations = run_enhanced_brief_with_sitemap(
            primary_keyword="gpu vs cpu for ai",
            target_audience="Technical decision-makers and developers",
            content_goal="Educational comparison and decision-making guide"
        )
        
        print("\n🎉 Brief generation completed successfully!")
        if recommendations:
            print(f"📄 Generated brief with {len(recommendations)} internal link recommendations")
        
        return True
        
    except KeyboardInterrupt:
        print("\n⚠️ Full brief generation interrupted")
        print("🔄 Running live sitemap analysis only...")
        
        # Run just the live sitemap analysis
        from live_sitemap_internal_links import LiveSitemapInternalLinker
        
        linker = LiveSitemapInternalLinker()
        stats = linker.get_sitemap_statistics()
        
        print(f"📊 Live Sitemap Statistics:")
        print(f"Total Pages: {stats['total_pages']}")
        print(f"Recent Pages: {stats['recent_pages']}")
        
        recommendations = linker.get_relevant_internal_links(
            primary_keyword="gpu vs cpu for ai",
            target_audience="Technical decision-makers",
            content_goal="Educational comparison"
        )
        
        if recommendations:
            print(f"✅ Found {len(recommendations)} internal link recommendations")
            for i, rec in enumerate(recommendations[:3], 1):
                print(f"{i}. {rec['title']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error running brief generator: {e}")
        print("🔄 Trying live sitemap analysis only...")
        
        try:
            from live_sitemap_internal_links import LiveSitemapInternalLinker
            
            linker = LiveSitemapInternalLinker()
            recommendations = linker.get_relevant_internal_links(
                primary_keyword="gpu vs cpu for ai",
                target_audience="Technical decision-makers",
                content_goal="Educational comparison"
            )
            
            if recommendations:
                print(f"✅ Found {len(recommendations)} internal link recommendations")
            
            return True
            
        except Exception as e2:
            print(f"❌ Live sitemap analysis also failed: {e2}")
            return False

def main():
    """Main function"""
    success = run_brief_with_progress()
    
    if success:
        print("\n🎉 Process completed!")
        print("📄 Check the generated files for your brief and recommendations")
    else:
        print("\n❌ Process failed")
        print("Please check your API keys and network connection")

if __name__ == "__main__":
    main()
