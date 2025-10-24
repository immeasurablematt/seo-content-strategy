#!/usr/bin/env python3
"""
SEO Content Strategy Tool - Web Interface

This script starts the Streamlit web application for generating
SEO content briefs through a user-friendly interface.

Usage:
    python start_web_app.py
"""

import sys
import os
import subprocess
from pathlib import Path

def main():
    """Main entry point for the web application"""
    print("🌐 Starting SEO Brief Generator Web App")
    print("=" * 50)
    print()
    print("This will start a web interface where you can:")
    print("• Generate SEO content briefs")
    print("• Analyze keyword competition")
    print("• Get AI-powered content recommendations")
    print()
    print("The app will open in your web browser automatically.")
    print("Press Ctrl+C to stop the server.")
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
        # Start the Streamlit app
        streamlit_script = Path("src") / "streamlit_app.py"
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            str(streamlit_script),
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
    except KeyboardInterrupt:
        print("\n\n👋 Web app stopped!")
    except FileNotFoundError:
        print("❌ Streamlit not found!")
        print("   Please install it with: pip install streamlit")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\n💡 Tips:")
        print("   - Make sure Streamlit is installed: pip install streamlit")
        print("   - Make sure your .env file has valid API keys")
        print("   - Check your internet connection")

if __name__ == "__main__":
    main()
