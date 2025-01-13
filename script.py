import fitz  # PyMuPDF
import re
from datetime import datetime
import os
import tabula

# Open the PDF files
pdf_one = fitz.open("one.pdf")
pdf_two = fitz.open("two.pdf")

# Get the PDF filenames
pdf_one_name = os.path.basename(pdf_one.name)
pdf_two_name = os.path.basename(pdf_two.name)

# Extract text from the first page (or the page with the date)
page_one = pdf_one.load_page(0)  # Page 0 is the first page
text_one = page_one.get_text("text")

page_two = pdf_two.load_page(0)  # Page 0 is the first page
text_two = page_two.get_text("text")

# Regex pattern to match the date format
date_pattern = r"Date:\s*(\d{1,2}\s\w+\s\d{4}\s\d{1,2}:\d{2}\s[APM]{2})"

# Search for the date in the extracted text
match_one = re.search(date_pattern, text_one)
match_two = re.search(date_pattern, text_two)

# Function to convert date string to datetime object
def convert_to_datetime(date_str):
    return datetime.strptime(date_str, "%d %B %Y %I:%M %p")

# Extract and compare the dates
if match_one:
    date_one = match_one.group(0).strip().replace("Date:", "").strip()
    print(f"Extracted Date from {pdf_one_name}: {date_one}")
else:
    print(f"Date not found in {pdf_one_name}.")

if match_two:
    date_two = match_two.group(0).strip().replace("Date:", "").strip()
    print(f"Extracted Date from {pdf_two_name}: {date_two}")
else:
    print(f"Date not found in {pdf_two_name}.")

# Read PDF into a list of DataFrames
dfs_one = tabula.read_pdf("one.pdf", pages='all', lattice=True)
dfs_two = tabula.read_pdf("two.pdf", pages='all', lattice=True)

# Initialize an empty list to store IDs from all pages
all_ids_one = []
all_ids_two = []

# Loop through all DataFrames (one for each page/table)
for df in dfs_one:
    if 'Roll' in df.columns:  # Check if 'ID' column exists in the DataFrame
        all_ids_one.extend(df['Roll'].tolist())  # Add the IDs to the list

for df in dfs_two:
    if 'Roll' in df.columns:  # Check if 'ID' column exists in the DataFrame
        all_ids_two.extend(df['Roll'].tolist())  # Add the IDs to the list

# Separate mismatch IDs from dfs one
misMatchIDs_one = [id for id in all_ids_one if id not in all_ids_two]
# Separate mismatch IDs from dfs two
misMatchIDs_two = [id for id in all_ids_two if id not in all_ids_one]

# # Debugging: print the mismatch IDs lists
# print(f"Mismatch IDs in {pdf_one_name}: {misMatchIDs_one}")
# print(f"Mismatch IDs in {pdf_two_name}: {misMatchIDs_two}")

# Compare dates if both are found
if match_one and match_two:
    date_one_obj = convert_to_datetime(date_one)
    date_two_obj = convert_to_datetime(date_two)

    if date_one_obj < date_two_obj:
        print(f"The date in {pdf_one_name} is earlier.(Need to remove) ", misMatchIDs_two)
        print(f"The date in {pdf_two_name} is later. (Need to add)", misMatchIDs_one)
    elif date_one_obj > date_two_obj:
        print(f"The date in {pdf_two_name} is earlier. (Need to remove)", misMatchIDs_one)
        print(f"The date in {pdf_one_name} is later. (Need to add)", misMatchIDs_two)
    else:
        print("Both dates are the same.")
