# GST Reconciliation Dashboard

A modern web application for GST reconciliation between books and GSTR-2A data. This application provides an intuitive interface for matching and analyzing GST transactions with advanced features like fuzzy matching, tax discrepancy analysis, and detailed reporting.

## Features

- **Modern Web Interface**: Built with Streamlit for a clean, responsive user experience
- **Advanced Matching**: Multiple levels of matching (exact, partial, fuzzy)
- **Tax Discrepancy Analysis**: Detailed analysis of IGST, CGST, and SGST differences
- **Interactive Visualizations**: Pie charts and metrics for quick insights
- **Export Capabilities**: Export results to Excel for further analysis
- **Data Validation**: Built-in validation for GSTIN, invoice numbers, and tax amounts

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/gst-reconciliation.git
cd gst-reconciliation
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the application:
```bash
streamlit run app.py
```

2. Open your web browser and navigate to `http://localhost:8501`

3. Upload your Excel file containing books and GSTR-2A data

4. View the reconciliation results and export as needed

## Input Data Format

The application expects an Excel file with the following columns:

- Source Name (BOOKS/GSTR-2A)
- Supplier GSTIN
- Supplier Legal Name
- Supplier Trade Name
- Invoice Date
- Books Date
- Invoice Number
- Total Taxable Value
- Total Tax Value
- Total IGST Amount
- Total CGST Amount
- Total SGST Amount
- Total Invoice Value

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Deployment & Local Testing Instructions

### 1. Streamlit Community Cloud Deployment
- Ensure your repository contains the following files:
  - `streamlit_app.py` (main entrypoint, see below)
  - `requirements.txt` (with pinned versions, no python-Levenshtein)
  - `runtime.txt` (with `python-3.11`)
  - `packages.txt` (with `build-essential` and `python3-dev`)
- In Streamlit Cloud, set the main file as `streamlit_app.py`.
- If your main file is `app.py`, rename or copy it to `streamlit_app.py`.
- Push all changes to your public GitHub repository.
- Restart the app from the Streamlit Cloud dashboard if needed.

### 2. Local Testing (Python 3.11)
- Create a virtual environment with Python 3.11:
  ```sh
  python3.11 -m venv venv
  source venv/bin/activate  # On Windows: venv\Scripts\activate
  pip install -r requirements.txt
  streamlit run app.py  # or streamlit_app.py
  ```

### 3. Local Testing with Docker
- Use the following Dockerfile to simulate the Streamlit Cloud environment:
  ```dockerfile
  FROM python:3.11-slim
  RUN apt-get update && apt-get install -y build-essential python3-dev
  WORKDIR /app
  COPY . .
  RUN pip install -r requirements.txt
  CMD ["streamlit", "run", "streamlit_app.py"]
  ```
- Build and run:
  ```sh
  docker build -t gst-recon .
  docker run -p 8501:8501 gst-recon
  ```

### 4. Performance & Logging
- The reconciliation process is optimized to run in under 60 seconds for large files.
- Logging is enabled for error tracking and performance monitoring.
- All tax amounts are formatted in Indian currency (₹1,00,000 style).

### 5. Troubleshooting
- If you see dependency installation errors for `python-Levenshtein`, it has been removed from requirements to ensure successful deployment. `fuzzywuzzy` will still work for all matching operations, just slightly slower.
- If you see other errors, check the deployment logs for missing system packages or version conflicts.
- Ensure all required files are present and the entrypoint is correct.

---

For more details, see the code comments and the documentation in the `README_SETTINGS.md` and `README_UNIQUE_GST_REPORT.md` files. 