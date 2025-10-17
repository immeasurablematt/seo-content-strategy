#!/usr/bin/env python3
"""
SEO Content Strategy Tool - Authority Analysis

This script runs the comprehensive content authority analysis
for your website, including keyword research, competitor analysis,
and content calendar generation.

Usage:
    python run_analysis.py
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from quick_start import main as analysis_main

def main():
    """Main entry point for the content authority analysis"""
    print("📊 Content Authority Analysis")
    print("=" * 50)
    print()
    print("This tool will analyze your website's content authority and")
    print("generate a comprehensive content strategy with:")
    print("• Keyword research and clustering")
    print("• Authority assessment")
    print("• Content gap identification")
    print("• 90-day content calendar")
    print("• Excel and markdown reports")
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
        # Run the main analysis
        analysis_main()
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
