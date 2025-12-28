# PDF Table Extractor - Command Line Interface

A powerful command-line tool to extract tables from PDF files and convert them to CSV or Excel format.

## Features

- 📊 Extract tables from text-based PDF files
- 📄 Convert tables to CSV or Excel format
- 📑 Process specific pages or entire documents
- 📁 Save tables as individual files or combined
- 🔍 Smart detection of image-based PDFs
- 🛠️ Advanced table detection using pdfplumber technology
- 📋 Support for complex table structures

## Installation

```bash
# Clone the repository
git clone https://github.com/Athurnm/python-pdf-to-csv-table-webapp.git
cd python-pdf-to-csv-table-webapp

# Switch to CLI branch
git checkout cli-version

# Install dependencies
pip install -r requirements.txt
```

## Usage

Basic usage:

```bash
python pdf_table_extractor_cli.py input.pdf
```

This will extract all tables from `input.pdf` and save them as individual CSV files in the current directory.

### Command-line Options

```
Usage:
    python pdf_table_extractor_cli.py input.pdf [--output OUTPUT_DIR] [--format FORMAT]
    
Options:
    --output OUTPUT_DIR    Directory to save extracted tables (default: current directory)
    --format FORMAT        Output format: 'csv' or 'xlsx' (default: csv)
    --all                  Extract all tables into a single file (default: separate files)
    --pages PAGES          Specific pages to extract (e.g., "1,3,5-7")
    --verbose              Show detailed processing information
    --help                 Show this help message
```

### Examples

Extract tables and save as Excel files:

```bash
python pdf_table_extractor_cli.py document.pdf --format xlsx
```

Extract tables from specific pages:

```bash
python pdf_table_extractor_cli.py document.pdf --pages "1,3,5-7"
```

Combine all tables into a single file:

```bash
python pdf_table_extractor_cli.py document.pdf --all
```

Save output to a specific directory:

```bash
python pdf_table_extractor_cli.py document.pdf --output /path/to/output
```

Verbose output for debugging:

```bash
python pdf_table_extractor_cli.py document.pdf --verbose
```

## How It Works

1. **PDF Analysis**: The tool analyzes the PDF structure to detect tables
2. **Table Extraction**: Uses pdfplumber to extract tables from text-based PDFs
3. **Data Processing**: Cleans and formats the extracted table data
4. **Output Generation**: Saves tables as CSV or Excel files

## Requirements

- Python 3.7+
- pdfplumber
- pandas
- PyPDF2
- Pillow

## Limitations

- Only works with text-based PDFs (not scanned documents)
- Table detection accuracy depends on PDF structure
- Complex tables may not be extracted perfectly

## License

This project is open source and available under the MIT License.