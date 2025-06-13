# PDF Table Extractor Web App

A Python-based web application that extracts tables from PDF files and converts them to CSV format. Features a clean, user-friendly interface with drag-and-drop file upload functionality.

## Features

- 📊 Extract all tables from PDF files automatically
- 📁 Convert tables to CSV format for easy data analysis
- 🗂️ Handle multiple tables - get a ZIP file with all CSVs
- 🎨 Modern, responsive web interface
- ⚡ Fast and secure processing
- 📱 Mobile-friendly design

## Prerequisites

Before running this application, you need to have Java installed on your system as `tabula-py` requires it for PDF processing.

### Install Java

**macOS:**
```bash
brew install openjdk
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install default-jdk
```

**Windows:**
Download and install Java from [Oracle's website](https://www.oracle.com/java/technologies/downloads/) or use OpenJDK.

## Installation

1. **Clone or download this project**
   ```bash
   git clone <repository-url>
   cd pdf-table-extractor
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   
   # Activate virtual environment
   # On macOS/Linux:
   source venv/bin/activate
   
   # On Windows:
   venv\Scripts\activate
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Start the web application**
   ```bash
   python app.py
   ```

2. **Open your web browser and navigate to:**
   ```
   http://localhost:5000
   ```

3. **Upload and process PDF files:**
   - Click "Choose PDF File" to select a PDF from your computer
   - The app will automatically extract all tables found in the PDF
   - Download the resulting CSV file(s)
   - If multiple tables are found, you'll get a ZIP file containing all CSVs

## How It Works

1. **File Upload**: Users upload PDF files through the web interface
2. **Table Detection**: The app uses `tabula-py` to automatically detect and extract tables
3. **CSV Conversion**: Extracted tables are converted to CSV format using pandas
4. **Download**: Users can download individual CSV files or a ZIP archive for multiple tables

## File Structure

```
pdf-table-extractor/
├── app.py                 # Main Flask application
├── templates/
│   └── index.html         # Web interface template
├── requirements.txt       # Python dependencies
├── uploads/              # Temporary storage for uploaded PDFs
├── outputs/              # Temporary storage for generated CSVs
└── README.md             # This file
```

## Configuration

The application includes several configurable settings in `app.py`:

- `MAX_CONTENT_LENGTH`: Maximum file upload size (default: 16MB)
- `UPLOAD_FOLDER`: Directory for temporary PDF storage
- `OUTPUT_FOLDER`: Directory for temporary CSV storage
- `ALLOWED_EXTENSIONS`: Allowed file types (currently only PDF)

## Troubleshooting

### Common Issues

1. **Java not found error**
   - Make sure Java is installed and accessible in your PATH
   - Try running `java -version` to verify installation

2. **No tables found in PDF**
   - The PDF might contain images of tables rather than actual table data
   - Try using a different PDF or ensure the tables are text-based

3. **Memory issues with large PDFs**
   - The app processes PDFs in memory, so very large files might cause issues
   - Consider splitting large PDFs into smaller chunks

### Dependencies

- **Flask**: Web framework for the application
- **pandas**: Data manipulation and CSV generation
- **tabula-py**: PDF table extraction (requires Java)
- **Werkzeug**: WSGI utilities for Flask

## Security Notes

- Files are temporarily stored on the server during processing
- Uploaded files and generated CSVs are automatically cleaned up after download
- The app includes basic file type validation
- Consider adding authentication for production use

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve this application.

## License

This project is open source and available under the MIT License.