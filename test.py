import fitz  # PyMuPDF
import re
from datetime import datetime
import os
import tabula

# Function to extract the date from a PDF's first page
def extract_date_from_pdf(pdf, date_pattern):
    page_text = pdf.load_page(0).get_text("text")
    match = re.search(date_pattern, page_text)
    return match.group(0).strip().replace("Date:", "").strip() if match else None

# Function to convert date string to datetime object
def convert_to_datetime(date_str):
    return datetime.strptime(date_str, "%d %B %Y %I:%M %p")

# Function to extract IDs from a PDF using tabula
def extract_ids_from_pdf(pdf_path):
    data_frames = tabula.read_pdf(pdf_path, pages='all', lattice=True)
    all_ids = []
    for df in data_frames:
        if 'Roll' in df.columns:
            all_ids.extend(df['Roll'].tolist())
    return all_ids

# File paths
pdf_one_path = "low_balance_report_Jan_20.pdf"
pdf_two_path = "low_balance_report_Jan_21.pdf"

# Open the PDF files
pdf_one = fitz.open(pdf_one_path)
pdf_two = fitz.open(pdf_two_path)

# Extract dates
DATE_PATTERN = r"Date:\s*(\d{1,2}\s\w+\s\d{4}\s\d{1,2}:\d{2}\s[APM]{2})"
date_one = extract_date_from_pdf(pdf_one, DATE_PATTERN)
date_two = extract_date_from_pdf(pdf_two, DATE_PATTERN)

# Display extracted dates
if not date_one:
    print(f"Date not found in {os.path.basename(pdf_one_path)}.")
if not date_two:
    print(f"Date not found in {os.path.basename(pdf_two_path)}.")

# Extract IDs
ids_one = extract_ids_from_pdf(pdf_one_path)
ids_two = extract_ids_from_pdf(pdf_two_path)

# Identify mismatched IDs
mismatch_ids_one = [id for id in ids_one if id not in ids_two]
mismatch_ids_two = [id for id in ids_two if id not in ids_one]

# Compare and display results if both dates are found
if date_one and date_two:
    date_one_obj = convert_to_datetime(date_one)
    date_two_obj = convert_to_datetime(date_two)

    if date_one_obj < date_two_obj:
        print(f"The date in {os.path.basename(pdf_one_path)} is earlier. (Need to remove): {mismatch_ids_two}")
        print(f"The date in {os.path.basename(pdf_two_path)} is later. (Need to add): {mismatch_ids_one}")
    elif date_one_obj > date_two_obj:
        print(f"The date in {os.path.basename(pdf_two_path)} is earlier. (Need to remove): {mismatch_ids_one}")
        print(f"The date in {os.path.basename(pdf_one_path)} is later. (Need to add): {mismatch_ids_two}")
    else:
        print("Both dates are the same.")
