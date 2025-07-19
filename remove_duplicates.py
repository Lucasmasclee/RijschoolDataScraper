import pandas as pd

# Read the CSV file
df = pd.read_csv('rijscholen_leads.csv')

# Get the original number of rows
original_count = len(df)
print(f"Original number of entries: {original_count}")

# Remove duplicates based on all columns
df_cleaned = df.drop_duplicates()

# Get the new number of rows
cleaned_count = len(df_cleaned)
print(f"Number of entries after removing duplicates: {cleaned_count}")
print(f"Removed {original_count - cleaned_count} duplicate entries")

# Save the cleaned data back to the file
df_cleaned.to_csv('rijscholen_leads_cleaned.csv', index=False)
print("Cleaned data saved to rijscholen_leads_cleaned.csv") 