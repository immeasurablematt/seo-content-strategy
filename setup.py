#!/usr/bin/env python3
"""
Setup script for SEO Content Strategy Tool

This script helps you set up the SEO Content Strategy Tool for first-time use.
It will:
1. Check Python version
2. Install required packages
3. Set up environment file
4. Test the installation
"""

import sys
import subprocess
import os
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_requirements():
    """Install required packages"""
    print("\n📦 Installing required packages...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✅ All packages installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install packages: {e}")
        return False

def setup_environment():
    """Set up environment file"""
    print("\n🔧 Setting up environment configuration...")
    
    env_file = Path(".env")
    template_file = Path("config") / "env_template.txt"
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    if not template_file.exists():
        print("❌ Environment template not found")
        return False
    
    try:
        # Copy template to .env
        with open(template_file, 'r') as f:
            template_content = f.read()
        
        with open(env_file, 'w') as f:
            f.write(template_content)
        
        print("✅ Created .env file from template")
        print("⚠️  IMPORTANT: Please edit .env file and add your API keys:")
        print("   - ANTHROPIC_API_KEY (get from https://console.anthropic.com/)")
        print("   - DATAFORSEO_LOGIN (get from https://app.dataforseo.com/)")
        print("   - DATAFORSEO_PASSWORD (get from https://app.dataforseo.com/)")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def create_output_directory():
    """Create output directory"""
    print("\n📁 Creating output directory...")
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    print("✅ Output directory created")
    return True

def test_installation():
    """Test the installation"""
    print("\n🧪 Testing installation...")
    try:
        # Test imports
        sys.path.insert(0, str(Path("src")))
        from simple_seo_brief import get_keyword_metrics
        print("✅ Core modules import successfully")
        
        # Check environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        if os.getenv("ANTHROPIC_API_KEY"):
            print("✅ Anthropic API key found")
        else:
            print("⚠️  Anthropic API key not set in .env")
        
        if os.getenv("DATAFORSEO_LOGIN") and os.getenv("DATAFORSEO_PASSWORD"):
            print("✅ DataForSEO credentials found")
        else:
            print("⚠️  DataForSEO credentials not set in .env")
        
        return True
    except Exception as e:
        print(f"❌ Installation test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 SEO Content Strategy Tool Setup")
    print("=" * 50)
    print()
    
    success = True
    
    # Check Python version
    if not check_python_version():
        success = False
    
    # Install requirements
    if success and not install_requirements():
        success = False
    
    # Setup environment
    if success and not setup_environment():
        success = False
    
    # Create output directory
    if success and not create_output_directory():
        success = False
    
    # Test installation
    if success and not test_installation():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Setup completed successfully!")
        print()
        print("Next steps:")
        print("1. Edit .env file with your API keys")
        print("2. Run: python generate_brief.py")
        print("3. Or run: python start_web_app.py for web interface")
    else:
        print("❌ Setup failed. Please check the errors above.")
    
    return success

if __name__ == "__main__":
    main()
