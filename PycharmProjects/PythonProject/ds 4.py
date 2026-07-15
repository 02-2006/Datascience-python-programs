from faker import Faker
from openpyxl import Workbook
import os

# Create Faker object (Indian data)
fake = Faker('en_IN')

# Create Excel workbook
wb = Workbook()
ws = wb.active
ws.title = "Fake Records"

# Add column headers
ws.append([
    "ID",
    "Name",
    "Age",
    "Gender",
    "Email",
    "Phone Number",
    "Address",
    "City",
    "State",
    "Company",
    "Job"
])

# Generate 50 fake records
for i in range(1, 51):
    ws.append([
        i,
        fake.name(),
        fake.random_int(min=18, max=60),
        fake.random_element(elements=("Male", "Female")),
        fake.email(),
        fake.phone_number(),
        fake.address().replace("\n", ", "),
        fake.city(),
        fake.state(),
        fake.company(),
        fake.job()
    ])

# Save the Excel file in the same folder as this Python script
file_name = "Fake_Records.xlsx"
wb.save(file_name)

# Print the exact location of the file
print("Excel file created successfully!")
print("File saved at:", os.path.abspath(file_name))