import pandas as pd
import os

# =====================================
# Enter your CSV file path here
# =====================================
file_path = r"C:\Users\Admin\Downloads\data.csv"
# Change the above path according to where your CSV file is stored.

# Check if file exists
if os.path.exists(file_path):

    # Load CSV file
    df = pd.read_csv(file_path)

    # Display first 10 rows
    print("========== First 10 Rows ==========")
    print(df.head(10))

    # Display number of rows and columns
    print("\n========== Dataset Shape ==========")
    print("Number of Rows :", df.shape[0])
    print("Number of Columns :", df.shape[1])

    # Display column names
    print("\n========== Column Names ==========")
    print(df.columns.tolist())

    # Display data types
    print("\n========== Data Types ==========")
    print(df.dtypes)

    # Summary statistics for numerical columns
    print("\n========== Summary Statistics ==========")
    print(df.describe())

else:
    print("Error: CSV file not found!")
    print("Please check the file path.")