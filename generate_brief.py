#!/usr/bin/env python3
"""
SEO Content Strategy Tool - Brief Generator

This is the main script you should run to generate SEO content briefs.
It's designed to be simple and user-friendly.

Usage:
    python generate_brief.py

The script will prompt you for:
1. Your primary keyword
2. Your target audience (optional - can auto-detect)
3. Your content goal (optional - can auto-detect)
4. Your domain (optional - defaults to io.net)
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from simple_seo_brief import main as generate_brief_main

def main():
    """Main entry point for the SEO brief generator"""
    print("🚀 SEO Content Brief Generator")
    print("=" * 50)
    print()
    print("This tool will help you create comprehensive SEO content briefs")
    print("using AI analysis of your competitors and keyword data.")
    print()
    
    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  No .env file found!")
        print("   Please copy config/env_template.txt to .env and add your API keys")
        print("   Run: cp config/env_template.txt .env")
        print("   Then edit .env with your actual API credentials")
        return
    
    try:
        # Run the main brief generation
        generate_brief_main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\n💡 Tips:")
        print("   - Make sure your .env file has valid API keys")
        print("   - Check your internet connection")
        print("   - Try running again")

if __name__ == "__main__":
    main()
