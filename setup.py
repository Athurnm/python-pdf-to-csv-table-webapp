#!/usr/bin/env python3
"""
Setup script for PDF Table Extractor Web App
This script helps with the initial setup and dependency installation.
"""

import subprocess
import sys
import os
import platform

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during {description}:")
        print(f"Command: {command}")
        print(f"Error: {e.stderr}")
        return False

def check_java():
    """Check if Java is installed"""
    print("\n🔍 Checking Java installation...")
    try:
        result = subprocess.run(['java', '-version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Java is installed")
            return True
        else:
            print("❌ Java is not installed or not in PATH")
            return False
    except FileNotFoundError:
        print("❌ Java is not installed or not in PATH")
        return False

def install_java_instructions():
    """Provide Java installation instructions based on OS"""
    system = platform.system().lower()
    print("\n📋 Java Installation Instructions:")
    print("=" * 50)
    
    if system == "darwin":  # macOS
        print("For macOS:")
        print("1. Install Homebrew if you haven't: https://brew.sh/")
        print("2. Run: brew install openjdk")
        print("3. Or download from: https://www.oracle.com/java/technologies/downloads/")
    
    elif system == "linux":
        print("For Linux (Ubuntu/Debian):")
        print("1. Run: sudo apt update")
        print("2. Run: sudo apt install default-jdk")
        print("\nFor Linux (CentOS/RHEL):")
        print("1. Run: sudo yum install java-11-openjdk-devel")
    
    elif system == "windows":
        print("For Windows:")
        print("1. Download Java from: https://www.oracle.com/java/technologies/downloads/")
        print("2. Or download OpenJDK from: https://adoptium.net/")
        print("3. Install and make sure Java is added to your PATH")
    
    else:
        print("Please install Java for your operating system")
        print("Visit: https://www.oracle.com/java/technologies/downloads/")

def create_directories():
    """Create necessary directories"""
    directories = ['uploads', 'outputs']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ Created directory: {directory}")
        else:
            print(f"📁 Directory already exists: {directory}")

def main():
    """Main setup function"""
    print("🚀 PDF Table Extractor Web App Setup")
    print("=" * 40)
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 7):
        print("❌ Python 3.7 or higher is required")
        print(f"Current version: {python_version.major}.{python_version.minor}")
        sys.exit(1)
    else:
        print(f"✅ Python version: {python_version.major}.{python_version.minor}")
    
    # Check Java installation
    if not check_java():
        install_java_instructions()
        print("\n⚠️  Please install Java and run this setup script again.")
        return False
    
    # Create necessary directories
    print("\n📁 Creating directories...")
    create_directories()
    
    # Install Python dependencies
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        print("\n💡 Try using: python -m pip install -r requirements.txt")
        return False
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Run: python app.py")
    print("2. Open your browser to: http://localhost:5000")
    print("3. Upload a PDF file and extract tables!")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)