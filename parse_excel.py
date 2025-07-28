#!/usr/bin/env python3
"""Parse Excel file and convert to products_vendors.json format"""
import json
import os

# Since we can't install openpyxl, let's create a manual entry form
print("Since I cannot directly read the Excel file, please provide the information:")
print("\nPlease share what columns are in your Excel file and I'll help you format it.")
print("For example:")
print("- Product Name")
print("- Vendor Name") 
print("- Category")
print("- Description")
print("\nYou can either:")
print("1. Copy and paste a few rows from the Excel as text")
print("2. Save the Excel as CSV and I can read that")
print("3. Tell me the structure and I'll create a template for you to fill")