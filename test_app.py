#!/usr/bin/env python3
"""
Test script for PDF Table Extractor Web App
This script performs basic tests to ensure the application is working correctly.
"""

import unittest
import tempfile
import os
import sys
from io import BytesIO
from unittest.mock import patch, MagicMock

# Add the current directory to the path so we can import our app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import app, allowed_file, extract_tables_from_pdf, save_tables_as_csv
    import pandas as pd
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please make sure all dependencies are installed:")
    print("pip install -r requirements.txt")
    sys.exit(1)

class TestPDFTableExtractor(unittest.TestCase):
    """Test cases for the PDF Table Extractor application"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.app = app.test_client()
        self.app.testing = True
        
        # Create temporary directories for testing
        self.temp_dir = tempfile.mkdtemp()
        app.config['UPLOAD_FOLDER'] = os.path.join(self.temp_dir, 'uploads')
        app.config['OUTPUT_FOLDER'] = os.path.join(self.temp_dir, 'outputs')
        
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_index_page(self):
        """Test that the main page loads correctly"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'PDF Table Extractor', response.data)
        self.assertIn(b'Choose PDF File', response.data)
    
    def test_health_check(self):
        """Test the health check endpoint"""
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['status'], 'healthy')
    
    def test_allowed_file_function(self):
        """Test the allowed_file function"""
        # Test valid PDF files
        self.assertTrue(allowed_file('document.pdf'))
        self.assertTrue(allowed_file('test.PDF'))
        self.assertTrue(allowed_file('my_file.pdf'))
        
        # Test invalid files
        self.assertFalse(allowed_file('document.txt'))
        self.assertFalse(allowed_file('image.jpg'))
        self.assertFalse(allowed_file('spreadsheet.xlsx'))
        self.assertFalse(allowed_file('no_extension'))
    
    def test_upload_no_file(self):
        """Test upload endpoint with no file"""
        response = self.app.post('/upload', data={})
        self.assertEqual(response.status_code, 302)  # Redirect
    
    def test_upload_empty_filename(self):
        """Test upload endpoint with empty filename"""
        data = {'file': (BytesIO(b''), '')}
        response = self.app.post('/upload', data=data)
        self.assertEqual(response.status_code, 302)  # Redirect
    
    def test_upload_invalid_file_type(self):
        """Test upload endpoint with invalid file type"""
        data = {'file': (BytesIO(b'test content'), 'test.txt')}
        response = self.app.post('/upload', data=data)
        self.assertEqual(response.status_code, 302)  # Redirect
    
    @patch('app.extract_tables_from_pdf')
    def test_upload_valid_pdf_no_tables(self, mock_extract):
        """Test upload with valid PDF but no tables found"""
        mock_extract.return_value = []
        
        data = {'file': (BytesIO(b'fake pdf content'), 'test.pdf')}
        response = self.app.post('/upload', data=data)
        self.assertEqual(response.status_code, 302)  # Redirect due to no tables
    
    @patch('app.extract_tables_from_pdf')
    @patch('app.save_tables_as_csv')
    def test_upload_valid_pdf_single_table(self, mock_save, mock_extract):
        """Test upload with valid PDF containing one table"""
        # Mock a single table
        mock_table = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
        mock_extract.return_value = [mock_table]
        
        # Mock CSV file creation
        csv_path = os.path.join(app.config['OUTPUT_FOLDER'], 'test_table_1.csv')
        mock_save.return_value = [csv_path]
        
        # Create the mock CSV file
        mock_table.to_csv(csv_path, index=False)
        
        data = {'file': (BytesIO(b'fake pdf content'), 'test.pdf')}
        response = self.app.post('/upload', data=data)
        
        # Should return the CSV file
        self.assertEqual(response.status_code, 200)
    
    def test_save_tables_as_csv(self):
        """Test the save_tables_as_csv function"""
        # Create test tables
        table1 = pd.DataFrame({'Name': ['Alice', 'Bob'], 'Age': [25, 30]})
        table2 = pd.DataFrame({'Product': ['A', 'B'], 'Price': [10, 20]})
        tables = [table1, table2]
        
        # Save tables
        csv_files = save_tables_as_csv(tables, app.config['OUTPUT_FOLDER'], 'test')
        
        # Check that files were created
        self.assertEqual(len(csv_files), 2)
        for csv_file in csv_files:
            self.assertTrue(os.path.exists(csv_file))
            self.assertTrue(csv_file.endswith('.csv'))
        
        # Clean up
        for csv_file in csv_files:
            os.remove(csv_file)

class TestApplicationIntegration(unittest.TestCase):
    """Integration tests for the complete application"""
    
    def test_app_startup(self):
        """Test that the application can start without errors"""
        with app.test_client() as client:
            response = client.get('/')
            self.assertEqual(response.status_code, 200)
    
    def test_static_content(self):
        """Test that static content is served correctly"""
        with app.test_client() as client:
            response = client.get('/')
            # Check for key elements in the HTML
            self.assertIn(b'PDF Table Extractor', response.data)
            self.assertIn(b'Choose PDF File', response.data)
            self.assertIn(b'Extract Tables', response.data)

def run_tests():
    """Run all tests and display results"""
    print("🧪 Running PDF Table Extractor Tests")
    print("=" * 40)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestPDFTableExtractor))
    suite.addTests(loader.loadTestsFromTestCase(TestApplicationIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 40)
    if result.wasSuccessful():
        print("✅ All tests passed!")
        print(f"Ran {result.testsRun} tests successfully")
    else:
        print("❌ Some tests failed!")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_tests()
    if not success:
        sys.exit(1)