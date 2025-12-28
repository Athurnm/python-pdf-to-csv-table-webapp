#!/usr/bin/env python3
"""
Test script for the PDF Table Extractor CLI
This script tests the CLI functionality with sample PDF files.
"""

import os
import subprocess
import sys
import time

def run_command(command):
    """Run a command and return the output"""
    print(f"Running: {command}")
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        universal_newlines=True
    )
    stdout, stderr = process.communicate()
    return process.returncode, stdout, stderr

def test_cli_functionality():
    """Test the CLI functionality with sample PDF files"""
    print("🧪 Testing PDF Table Extractor CLI")
    print("=" * 50)
    
    # Check if the CLI script exists
    if not os.path.exists("pdf_table_extractor_cli.py"):
        print("❌ CLI script not found: pdf_table_extractor_cli.py")
        return False
    
    # Find sample PDF files
    sample_dir = "file_sample"
    if not os.path.exists(sample_dir):
        print(f"❌ Sample directory not found: {sample_dir}")
        return False
    
    sample_files = [f for f in os.listdir(sample_dir) if f.lower().endswith('.pdf')]
    if not sample_files:
        print(f"❌ No PDF files found in {sample_dir}")
        return False
    
    print(f"📄 Found {len(sample_files)} sample PDF files:")
    for file in sample_files:
        print(f"  - {file}")
    
    # Create output directory for test results
    output_dir = "cli_test_output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Test basic functionality with each sample file
    successful_extractions = 0
    
    for i, filename in enumerate(sample_files, 1):
        pdf_path = os.path.join(sample_dir, filename)
        print(f"\n📄 Testing file {i}/{len(sample_files)}: {filename}")
        
        # Test 1: Basic extraction (CSV)
        print("\n🔍 Test 1: Basic extraction (CSV)")
        cmd = f"python pdf_table_extractor_cli.py {pdf_path} --output {output_dir} --verbose"
        returncode, stdout, stderr = run_command(cmd)
        
        if returncode == 0 and "Table extraction completed successfully" in stdout:
            print("✅ Basic CSV extraction successful")
            successful_extractions += 1
        elif "image-based" in stderr or "image-based" in stdout:
            print("⚠️ PDF detected as image-based (expected behavior)")
        else:
            print(f"❌ Basic extraction failed with return code {returncode}")
            print(f"Error: {stderr}")
        
        # Test 2: Excel format
        print("\n🔍 Test 2: Excel format extraction")
        cmd = f"python pdf_table_extractor_cli.py {pdf_path} --output {output_dir} --format xlsx --verbose"
        returncode, stdout, stderr = run_command(cmd)
        
        if returncode == 0 and "Table extraction completed successfully" in stdout:
            print("✅ Excel extraction successful")
        elif "image-based" in stderr or "image-based" in stdout:
            print("⚠️ PDF detected as image-based (expected behavior)")
        else:
            print(f"❌ Excel extraction failed with return code {returncode}")
            print(f"Error: {stderr}")
        
        # Test 3: Combined output
        print("\n🔍 Test 3: Combined output")
        cmd = f"python pdf_table_extractor_cli.py {pdf_path} --output {output_dir} --all --verbose"
        returncode, stdout, stderr = run_command(cmd)
        
        if returncode == 0 and "Table extraction completed successfully" in stdout:
            print("✅ Combined output extraction successful")
        elif "image-based" in stderr or "image-based" in stdout:
            print("⚠️ PDF detected as image-based (expected behavior)")
        else:
            print(f"❌ Combined output extraction failed with return code {returncode}")
            print(f"Error: {stderr}")
    
    # Check output directory
    output_files = os.listdir(output_dir)
    print(f"\n📁 Generated {len(output_files)} output files in {output_dir}/")
    
    # Print summary
    print("\n🎉 Test completed!")
    print("\n📊 Results Summary:")
    print("=" * 30)
    print(f"   • Files tested: {len(sample_files)}")
    print(f"   • Successful extractions: {successful_extractions}")
    print(f"   • Output files generated: {len(output_files)}")
    
    if successful_extractions > 0:
        print("✅ CLI functionality is working correctly")
        return True
    else:
        print("❌ No successful extractions")
        return False

if __name__ == "__main__":
    success = test_cli_functionality()
    if not success:
        sys.exit(1)