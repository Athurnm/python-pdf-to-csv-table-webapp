#!/usr/bin/env python3
"""
PDF Table Extractor - Command Line Interface
Extract tables from PDF files and convert them to CSV format.

Usage:
    python pdf_table_extractor_cli.py input.pdf [--output OUTPUT_DIR] [--format FORMAT]
    
Options:
    --output OUTPUT_DIR    Directory to save extracted tables (default: current directory)
    --format FORMAT        Output format: 'csv' or 'xlsx' (default: csv)
    --all                  Extract all tables into a single file (default: separate files)
    --pages PAGES          Specific pages to extract (e.g., "1,3,5-7")
    --verbose              Show detailed processing information
    --help                 Show this help message
"""

import os
import sys
import argparse
import pandas as pd
import pdfplumber
import PyPDF2
from PIL import Image
import zipfile
from datetime import datetime
import logging
import csv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('pdf_table_extractor')

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Extract tables from PDF files and convert them to CSV format.',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('input_pdf', help='Path to the input PDF file')
    parser.add_argument('--output', '-o', help='Directory to save extracted tables (default: current directory)')
    parser.add_argument('--format', '-f', choices=['csv', 'xlsx'], default='csv',
                        help='Output format: csv or xlsx (default: csv)')
    parser.add_argument('--all', '-a', action='store_true',
                        help='Extract all tables into a single file (default: separate files)')
    parser.add_argument('--pages', '-p', help='Specific pages to extract (e.g., "1,3,5-7")')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show detailed processing information')
    
    return parser.parse_args()

def is_image_based_pdf(pdf_path):
    """
    Check if PDF is primarily image-based by analyzing text content and images
    Returns True if the PDF appears to be image-based
    """
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            total_pages = len(pdf_reader.pages)
            
            if total_pages == 0:
                return False
            
            # Sample first few pages to determine if image-based
            pages_to_check = min(3, total_pages)
            text_content_ratio = 0
            image_count = 0
            
            with pdfplumber.open(pdf_path) as pdf:
                for i in range(pages_to_check):
                    page = pdf.pages[i]
                    
                    # Check text content
                    text = page.extract_text()
                    if text and len(text.strip()) > 50:  # Meaningful text content
                        text_content_ratio += 1
                    
                    # Check for images
                    if hasattr(page, 'images') and page.images:
                        image_count += len(page.images)
            
            # Determine if image-based
            # If most pages have little text and many images, consider it image-based
            text_ratio = text_content_ratio / pages_to_check
            avg_images_per_page = image_count / pages_to_check
            
            # Heuristic: if less than 30% of pages have meaningful text 
            # and there are many images, it's likely image-based
            is_image_based = text_ratio < 0.3 and avg_images_per_page > 0.5
            
            return is_image_based
            
    except Exception as e:
        logger.error(f"Error checking if PDF is image-based: {str(e)}")
        # If we can't determine, assume it's not image-based to allow processing
        return False

def parse_page_ranges(page_str, max_pages):
    """Parse page ranges like "1,3,5-7" into a list of page numbers"""
    if not page_str:
        return list(range(1, max_pages + 1))
    
    pages = set()
    parts = page_str.split(',')
    
    for part in parts:
        if '-' in part:
            start, end = map(int, part.split('-'))
            pages.update(range(start, end + 1))
        else:
            pages.add(int(part))
    
    # Ensure pages are within range and sorted
    return sorted([p for p in pages if 1 <= p <= max_pages])

def extract_tables_from_pdf(pdf_path, page_numbers=None):
    """
    Extract tables from PDF using pdfplumber
    Returns list of pandas DataFrames
    """
    try:
        tables = []
        
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            
            # If no page numbers specified, extract from all pages
            if page_numbers is None:
                page_numbers = list(range(1, total_pages + 1))
            else:
                # Ensure page numbers are within range
                page_numbers = [p for p in page_numbers if 1 <= p <= total_pages]
            
            for page_num in page_numbers:
                # pdfplumber uses 0-based indexing
                page = pdf.pages[page_num - 1]
                
                # Extract tables from the page
                page_tables = page.extract_tables()
                
                if page_tables:
                    for table_num, table in enumerate(page_tables):
                        if table and len(table) > 1:  # Must have at least header + 1 row
                            # Convert table to DataFrame
                            # First row as header, rest as data
                            headers = table[0]
                            data = table[1:]
                            
                            # Clean headers - remove None values and empty strings
                            clean_headers = []
                            for i, header in enumerate(headers):
                                if header is None or header == '':
                                    clean_headers.append(f'Column_{i+1}')
                                else:
                                    clean_headers.append(str(header).strip())
                            
                            # Process data - replace actual newlines with \n escape sequences
                            clean_data = []
                            for row in data:
                                clean_row = []
                                for cell in row:
                                    if cell is None:
                                        clean_row.append('')
                                    else:
                                        # Replace actual newlines with \n escape sequences
                                        clean_row.append(str(cell).replace('\n', '\\n'))
                                clean_data.append(clean_row)
                            
                            # Create DataFrame
                            if clean_data:  # Make sure we have data rows
                                df = pd.DataFrame(clean_data, columns=clean_headers)
                                
                                # Clean the data - remove completely empty rows
                                df = df.dropna(how='all')
                                
                                # Remove rows where all values are empty strings
                                df = df[~(df.astype(str).eq('').all(axis=1))]
                                
                                if not df.empty and len(df) > 0:
                                    # Add metadata
                                    df.attrs['page'] = page_num
                                    df.attrs['table'] = table_num + 1
                                    tables.append(df)
        
        return tables
        
    except Exception as e:
        logger.error(f"Error extracting tables with pdfplumber: {str(e)}")
        return []

def save_tables(tables, output_dir, base_filename, output_format='csv', combine_tables=False):
    """Save extracted tables as CSV or Excel files"""
    if not tables:
        logger.warning("No tables found to save")
        return []
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    output_files = []
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if combine_tables:
        # Combine all tables into a single file
        if output_format == 'csv':
            # For CSV, we need to create a ZIP file with all tables
            zip_filename = os.path.join(output_dir, f"{base_filename}_{timestamp}_all_tables.zip")
            
            with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for i, table in enumerate(tables):
                    # Include page and table info in filename
                    page_info = ""
                    if hasattr(table, 'attrs') and 'page' in table.attrs:
                        page_info = f"_page{table.attrs['page']}"
                    
                    csv_filename = f"{base_filename}_table_{i+1}{page_info}.csv"
                    csv_path = os.path.join(output_dir, csv_filename)
                    
                    # Save to temporary CSV file with proper quoting and escaping
                    table.to_csv(csv_path, index=False, quoting=csv.QUOTE_NONNUMERIC,
                              escapechar='\\', lineterminator='\n')
                    
                    # Add to ZIP file
                    zip_file.write(csv_path, csv_filename)
                    output_files.append(csv_path)
                    
                    # Remove temporary CSV file
                    os.remove(csv_path)
            
            # Return the ZIP file path
            output_files = [zip_filename]
            
        elif output_format == 'xlsx':
            # For Excel, we can save all tables as sheets in one file
            excel_filename = os.path.join(output_dir, f"{base_filename}_{timestamp}_all_tables.xlsx")
            
            with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
                for i, table in enumerate(tables):
                    # Include page and table info in sheet name
                    page_info = ""
                    if hasattr(table, 'attrs') and 'page' in table.attrs:
                        page_info = f"_p{table.attrs['page']}"
                    
                    sheet_name = f"Table_{i+1}{page_info}"
                    # Excel sheet names have a 31 character limit
                    if len(sheet_name) > 31:
                        sheet_name = sheet_name[:31]
                    
                    table.to_excel(writer, sheet_name=sheet_name, index=False)
            
            output_files = [excel_filename]
    else:
        # Save each table as a separate file
        for i, table in enumerate(tables):
            # Include page and table info in filename
            page_info = ""
            if hasattr(table, 'attrs') and 'page' in table.attrs:
                page_info = f"_page{table.attrs['page']}"
            
            if output_format == 'csv':
                file_path = os.path.join(output_dir, f"{base_filename}_table_{i+1}{page_info}.csv")
                table.to_csv(file_path, index=False, quoting=csv.QUOTE_NONNUMERIC,
                          escapechar='\\', lineterminator='\n')
            elif output_format == 'xlsx':
                file_path = os.path.join(output_dir, f"{base_filename}_table_{i+1}{page_info}.xlsx")
                table.to_excel(file_path, index=False)
            
            output_files.append(file_path)
    
    return output_files

def main():
    """Main function to extract tables from PDF"""
    args = parse_arguments()
    
    # Set logging level based on verbose flag
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Validate input file
    if not os.path.exists(args.input_pdf):
        logger.error(f"Input file not found: {args.input_pdf}")
        sys.exit(1)
    
    if not args.input_pdf.lower().endswith('.pdf'):
        logger.error(f"Input file is not a PDF: {args.input_pdf}")
        sys.exit(1)
    
    # Set output directory
    output_dir = args.output if args.output else os.getcwd()
    
    # Get base filename without extension
    base_filename = os.path.splitext(os.path.basename(args.input_pdf))[0]
    
    logger.info(f"Processing PDF: {args.input_pdf}")
    
    # Check if PDF is image-based
    if is_image_based_pdf(args.input_pdf):
        logger.error("This PDF appears to contain primarily images or scanned content.")
        logger.error("We currently only support text-based PDFs with extractable tables.")
        sys.exit(1)
    
    # Parse page ranges if specified
    page_numbers = None
    if args.pages:
        with pdfplumber.open(args.input_pdf) as pdf:
            total_pages = len(pdf.pages)
            page_numbers = parse_page_ranges(args.pages, total_pages)
            logger.info(f"Extracting tables from pages: {page_numbers}")
    
    # Extract tables from PDF
    logger.info("Extracting tables...")
    tables = extract_tables_from_pdf(args.input_pdf, page_numbers)
    
    if not tables:
        logger.warning("No tables found in the PDF file.")
        sys.exit(0)
    
    logger.info(f"Found {len(tables)} tables in the PDF")
    
    # Save tables
    logger.info(f"Saving tables in {args.format.upper()} format...")
    output_files = save_tables(
        tables, 
        output_dir, 
        base_filename, 
        output_format=args.format, 
        combine_tables=args.all
    )
    
    # Print summary
    logger.info("Table extraction completed successfully!")
    logger.info(f"Output format: {args.format.upper()}")
    
    if args.all:
        logger.info(f"All tables saved to: {output_files[0]}")
    else:
        logger.info(f"Tables saved to {len(output_files)} files in: {output_dir}")
        if args.verbose:
            for file in output_files:
                logger.info(f"  - {os.path.basename(file)}")

if __name__ == "__main__":
    main()