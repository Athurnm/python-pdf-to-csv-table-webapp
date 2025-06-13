#!/usr/bin/env python3
"""
Run script for PDF Table Extractor Web App
This script provides an easy way to start the application with proper configuration.
"""

import os
import sys
import subprocess
import webbrowser
import time
from threading import Timer

def check_dependencies():
    """Check if all required dependencies are installed"""
    try:
        import flask
        import pandas
        import tabula
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_java():
    """Check if Java is available"""
    try:
        result = subprocess.run(['java', '-version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Java is available")
            return True
        else:
            print("❌ Java is not available")
            return False
    except FileNotFoundError:
        print("❌ Java is not installed or not in PATH")
        print("Please install Java to use tabula-py for PDF processing")
        return False

def create_directories():
    """Create necessary directories if they don't exist"""
    directories = ['uploads', 'outputs', 'templates']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"📁 Created directory: {directory}")

def open_browser():
    """Open the web browser to the application URL"""
    url = "http://localhost:5001"
    print(f"🌐 Opening browser to {url}")
    webbrowser.open(url)

def main():
    """Main function to run the application"""
    print("🚀 Starting PDF Table Extractor Web App")
    print("=" * 45)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check Java
    if not check_java():
        print("\n⚠️  Warning: Java is required for PDF table extraction")
        print("The app will start but may not work properly without Java")
        response = input("Continue anyway? (y/N): ").lower()
        if response != 'y':
            sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Import and run the app
    try:
        from app import app
        
        print("\n🎯 Application Configuration:")
        print(f"   • Host: 0.0.0.0")
        print(f"   • Port: 5001")
        print(f"   • Debug: True")
        print(f"   • URL: http://localhost:5001")
        
        print("\n📋 Instructions:")
        print("   1. The browser will open automatically")
        print("   2. Upload a PDF file using the file picker")
        print("   3. Click 'Extract Tables' to process the PDF")
        print("   4. Download the resulting CSV file(s)")
        print("   5. Press Ctrl+C to stop the server")
        
        # Schedule browser opening after a short delay
        Timer(2.0, open_browser).start()
        
        print("\n🔄 Starting server...")
        print("-" * 45)
        
        # Run the Flask app
        app.run(
            debug=True,
            host='0.0.0.0',
            port=5001,
            use_reloader=False  # Disable reloader to prevent double browser opening
        )
        
    except ImportError as e:
        print(f"❌ Error importing application: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down the server...")
        print("Thank you for using PDF Table Extractor!")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()