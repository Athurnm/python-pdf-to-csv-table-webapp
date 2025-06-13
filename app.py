import os
import pandas as pd
from flask import Flask, request, render_template, send_file, flash, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
import pdfplumber
import PyPDF2
import tempfile
import zipfile
from io import BytesIO
from PIL import Image
import io
import csv

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'

# Configuration
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
ALLOWED_EXTENSIONS = {'pdf'}

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
        print(f"Error checking if PDF is image-based: {str(e)}")
        # If we can't determine, assume it's not image-based to allow processing
        return False

def extract_tables_from_pdf(pdf_path):
    """
    Extract tables from PDF using pdfplumber
    Returns list of pandas DataFrames
    """
    try:
        tables = []
        
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
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
                                    df.attrs['page'] = page_num + 1
                                    df.attrs['table'] = table_num + 1
                                    tables.append(df)
        
        return tables
        
    except Exception as e:
        print(f"Error extracting tables with pdfplumber: {str(e)}")
        return []

def save_tables_as_csv(tables, output_folder, base_filename):
    """Save extracted tables as CSV files"""
    csv_files = []
    
    for i, table in enumerate(tables):
        if not table.empty:
            # Include page and table info in filename if available
            page_info = ""
            if hasattr(table, 'attrs') and 'page' in table.attrs:
                page_info = f"_page{table.attrs['page']}"
            
            csv_filename = f"{base_filename}_table_{i+1}{page_info}.csv"
            csv_path = os.path.join(output_folder, csv_filename)
            table.to_csv(csv_path, index=False, quoting=csv.QUOTE_NONNUMERIC,
                      escapechar='\\', lineterminator='\n')
            csv_files.append(csv_path)
    
    return csv_files

@app.route('/')
def index():
    """Main page with file upload form"""
    return render_template('index.html')

@app.route('/clear-messages', methods=['POST'])
def clear_messages():
    """Clear flash messages"""
    # This will clear any existing flash messages
    return jsonify({'status': 'success'})

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and table extraction"""
    if 'file' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('index'))
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('index'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # First check if PDF is image-based
            if is_image_based_pdf(filepath):
                os.remove(filepath)  # Clean up uploaded file
                flash('This PDF appears to contain primarily images or scanned content. '
                      'We currently only support text-based PDFs with extractable tables. '
                      'Please try a PDF that contains text-based tables rather than scanned images.', 'error')
                return redirect(url_for('index'))
            
            # Extract tables from PDF
            tables = extract_tables_from_pdf(filepath)
            
            if not tables:
                flash('No tables found in the PDF file. '
                      'Please ensure your PDF contains properly formatted tables with text content.', 'warning')
                os.remove(filepath)  # Clean up uploaded file
                return redirect(url_for('index'))
            
            # Save tables as CSV files
            base_filename = os.path.splitext(filename)[0]
            csv_files = save_tables_as_csv(tables, app.config['OUTPUT_FOLDER'], base_filename)
            
            if len(csv_files) == 1:
                # Single table - return the CSV file directly
                csv_file = csv_files[0]
                
                def remove_file_after_send():
                    try:
                        os.remove(filepath)
                        os.remove(csv_file)
                    except:
                        pass
                
                response = send_file(csv_file, as_attachment=True, download_name=f"{base_filename}.csv")
                # Schedule cleanup after response
                response.call_on_close(remove_file_after_send)
                return response
                
            else:
                # Multiple tables - create a ZIP file
                zip_buffer = BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    for csv_file in csv_files:
                        zip_file.write(csv_file, os.path.basename(csv_file))
                
                zip_buffer.seek(0)
                
                # Clean up files
                os.remove(filepath)
                for csv_file in csv_files:
                    os.remove(csv_file)
                
                return send_file(
                    zip_buffer,
                    mimetype='application/zip',
                    as_attachment=True,
                    download_name=f"{base_filename}_tables.zip"
                )
                
        except Exception as e:
            error_msg = f'Error processing PDF: {str(e)}'
            print(error_msg)
            flash('An error occurred while processing your PDF. '
                  'Please ensure the file is not corrupted and try again.', 'error')
            if os.path.exists(filepath):
                os.remove(filepath)
            return redirect(url_for('index'))
    
    else:
        flash('Invalid file type. Please upload a PDF file.', 'error')
        return redirect(url_for('index'))

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return {'status': 'healthy', 'message': 'PDF Table Extractor is running'}

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)