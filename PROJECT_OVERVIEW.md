# PDF Table Extractor Web Application

A complete Python-based web application for extracting tables from PDF files and converting them to CSV format.

## 🎯 Project Overview

This web application provides a user-friendly interface for uploading PDF files and automatically extracting any tables found within them. The extracted tables are converted to CSV format and made available for download.

## 📁 Project Structure

```
python-pdf-table-to-csv-webapp/
├── app.py                    # Main Flask application
├── run.py                    # Application launcher with checks
├── setup.py                  # Automated setup and installation script
├── test_app.py              # Comprehensive test suite
├── requirements.txt          # Python dependencies
├── README.md                # Detailed documentation
├── .gitignore               # Git ignore rules
├── templates/
│   └── index.html           # Web interface template
└── file_sample/             # Sample PDF files for testing
    ├── BNI.pdf              # Sample bank document (1.78 MB)
    ├── Mutation - BCA (EVERBEST).pdf    # Sample mutation document (1.10 MB)
    └── Mutation - Mandiri (LIGHTHOUSE).pdf  # Sample document (0.44 MB)
```

## 🚀 Quick Start

1. **Navigate to the project directory:**
   ```bash
   cd python-pdf-table-to-csv-webapp
   ```

2. **Run the automated setup:**
   ```bash
   python3 setup.py
   ```

3. **Start the application:**
   ```bash
   python3 run.py
   ```

4. **Open your browser to:**
   ```
   http://localhost:5001
   ```

## ✨ Features

- **Modern Web Interface**: Beautiful, responsive design with drag-and-drop file upload
- **PDF Table Detection**: Automatic detection and extraction of tables using tabula-py
- **Multiple Table Support**: Handles PDFs with multiple tables (returns ZIP file)
- **CSV Export**: Clean, properly formatted CSV files
- **Error Handling**: Graceful handling of PDFs without extractable tables
- **File Validation**: Security measures and file type validation
- **Real-time Feedback**: Loading indicators and progress updates

## 🧪 Testing

The project includes comprehensive testing capabilities:

- **Unit Tests**: Run `python3 test_app.py`
- **Sample Files**: Three real PDF files in `file_sample/` directory
- **Integration Tests**: Full end-to-end testing with sample files

## 📋 Requirements

- **Python 3.7+**
- **Java** (required for tabula-py PDF processing)
- **Dependencies**: Listed in `requirements.txt`

## 🔧 Technical Details

- **Backend**: Flask web framework
- **PDF Processing**: tabula-py with Java integration
- **Data Handling**: pandas for CSV generation
- **Frontend**: HTML5, CSS3, JavaScript
- **File Handling**: Secure upload and temporary file management

## 📊 Test Results

Successfully tested with sample files:
- ✅ BNI.pdf → Multiple tables extracted (42KB ZIP)
- ✅ Mutation - BCA (EVERBEST).pdf → Multiple tables extracted (713KB ZIP)
- ⚠️ Mutation - Mandiri (LIGHTHOUSE).pdf → No extractable tables (properly handled)

## 🛠️ Development

The application is production-ready with:
- Comprehensive error handling
- Security measures
- Clean code structure
- Extensive documentation
- Test coverage

## 📝 License

This project is open source and available under the MIT License.