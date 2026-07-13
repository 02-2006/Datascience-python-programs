import pandas as pd
from sklearn.preprocessing import OneHotEncoder, MinMaxScaler

# Load dataset
df = pd.read_csv("customer.csv")

# Create Age Group feature
def age_group(age):
    if age < 18:
        return "Child"
    elif age < 60:
        return "Adult"
    else:
        return "Senior"

df["Age_Group"] = df["Age"].apply(age_group)

# One-Hot Encoding
categorical_cols = df.select_dtypes(include=['object', 'string']).columns

encoder = OneHotEncoder(sparse_output=False)

encoded = encoder.fit_transform(df[categorical_cols])

encoded_df = pd.DataFrame(
    encoded,
    columns=encoder.get_feature_names_out(categorical_cols)
)

# Remove original categorical columns
df = df.drop(columns=categorical_cols)

# Add encoded columns
df = pd.concat([df.reset_index(drop=True),
                encoded_df.reset_index(drop=True)], axis=1)

# Normalize numerical features
numerical_cols = df.select_dtypes(include=['int64', 'float64']).columns

scaler = MinMaxScaler()

df[numerical_cols] = scaler.fit_transform(df[numerical_cols])

# Save transformed dataset
df.to_csv("transformed_customer_data.csv", index=False)

print("Transformation Completed Successfully!")
print(df.head())