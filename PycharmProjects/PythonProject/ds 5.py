from faker import Faker
from openpyxl import Workbook
import pandas as pd
import matplotlib.pyplot as plt
import os

# ------------------------------------
# STEP 1: Generate Fake Student Records
# ------------------------------------

fake = Faker('en_IN')

wb = Workbook()
ws = wb.active
ws.title = "Student Records"

# Column Headers
ws.append([
    "ID",
    "Name",
    "Age",
    "Gender",
    "Marks",
    "Attendance"
])

# Generate 50 student records
for i in range(1, 51):
    ws.append([
        i,
        fake.name(),
        fake.random_int(min=18, max=23),
        fake.random_element(["Male", "Female"]),
        fake.random_int(min=35, max=100),
        fake.random_int(min=60, max=100)
    ])

# Save Excel File
filename = "Student_Records.xlsx"
wb.save(filename)

print("Student records created successfully!")
print("Saved at:", os.path.abspath(filename))

# ------------------------------------
# STEP 2: Load Excel File
# ------------------------------------

df = pd.read_excel(filename)

print("\n========== FIRST 10 RECORDS ==========")
print(df.head(10))

print("\n========== DATA INFO ==========")
print(df.info())

print("\n========== SUMMARY ==========")
print(df.describe())

# ------------------------------------
# STEP 3: Analysis
# ------------------------------------

print("\nAverage Marks:", round(df["Marks"].mean(), 2))
print("Average Attendance:", round(df["Attendance"].mean(), 2))

print("\nHighest Scorer")
print(df.loc[df["Marks"].idxmax()])

print("\nLowest Scorer")
print(df.loc[df["Marks"].idxmin()])

print("\nGender Count")
print(df["Gender"].value_counts())

# ------------------------------------
# STEP 4: Graph 1 - Student Marks
# ------------------------------------

plt.figure(figsize=(14,6))
plt.bar(df["Name"], df["Marks"])

plt.title("Student Marks")
plt.xlabel("Student Name")
plt.ylabel("Marks")

plt.xticks(rotation=90)
plt.tight_layout()
plt.show()

# ------------------------------------
# STEP 5: Graph 2 - Attendance
# ------------------------------------

plt.figure(figsize=(14,6))
plt.plot(df["Name"], df["Attendance"], marker='o')

plt.title("Student Attendance")
plt.xlabel("Student Name")
plt.ylabel("Attendance (%)")

plt.xticks(rotation=90)
plt.grid(True)
plt.tight_layout()
plt.show()

# ------------------------------------
# STEP 6: Graph 3 - Gender Distribution
# ------------------------------------

plt.figure(figsize=(6,6))

df["Gender"].value_counts().plot(
    kind="pie",
    autopct="%1.1f%%"
)

plt.ylabel("")
plt.title("Gender Distribution")
plt.show()

# ------------------------------------
# STEP 7: Graph 4 - Age Distribution
# ------------------------------------

plt.figure(figsize=(8,5))

plt.hist(df["Age"], bins=6)

plt.title("Age Distribution")
plt.xlabel("Age")
plt.ylabel("Number of Students")

plt.grid(True)
plt.show()

# ------------------------------------
# STEP 8: Scatter Plot
# ------------------------------------

plt.figure(figsize=(8,5))

plt.scatter(df["Attendance"], df["Marks"])

plt.title("Attendance vs Marks")
plt.xlabel("Attendance (%)")
plt.ylabel("Marks")

plt.grid(True)
plt.show()

# ------------------------------------
# STEP 9: Final Observations
# ------------------------------------

print("\n========== OBSERVATIONS ==========")
print("1. Total Students :", len(df))
print("2. Average Marks :", round(df["Marks"].mean(), 2))
print("3. Average Attendance :", round(df["Attendance"].mean(), 2))
print("4. Highest Marks :", df["Marks"].max())
print("5. Lowest Marks :", df["Marks"].min())
print("6. Student marks are shown in the bar chart.")
print("7. Attendance trend is shown in the line graph.")
print("8. Gender distribution is shown using the pie chart.")
print("9. Age distribution is shown using the histogram.")
print("10. Scatter plot shows the relationship between attendance and marks.")