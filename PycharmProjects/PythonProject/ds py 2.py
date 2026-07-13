import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the CSV file
df = pd.read_csv(r"C:\Users\Admin\Downloads\data.csv")   # Change the path if needed

# Display the first 5 rows
print(df.head())

# Select only numerical columns
numerical_columns = df.select_dtypes(include=['int64', 'float64']).columns

# Plot histogram for each numerical column
for column in numerical_columns:
    plt.figure(figsize=(6, 4))
    sns.histplot(df[column], bins=10, kde=True)
    plt.title(f"Histogram of {column}")
    plt.xlabel(column)
    plt.ylabel("Frequency")
    plt.grid(True)
    plt.show()