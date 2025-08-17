import pandas as pd
import os

# Define file paths
csv_file = 'uploads/40e49a31-0e55-41bd-bad9-8d0fe33b8839/sample-sales.csv'
metadata_file = 'uploads/40e49a31-0e55-41bd-bad9-8d0fe33b8839/metadata.txt'

# Ensure the directory exists
os.makedirs(os.path.dirname(metadata_file), exist_ok=True)

# Read the first 3 rows of the CSV
df = pd.read_csv(csv_file)
preview = df.head(3).to_string()

# Append the preview to the metadata file
with open(metadata_file, 'a') as f:
    f.write('CSV Preview:\n')
    f.write(preview + '\n')

print(f'Successfully wrote preview to {metadata_file}')
