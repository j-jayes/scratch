import pandas as pd
import requests
from bs4 import BeautifulSoup

def get_website_name(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx and 5xx)
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.title.string.strip() if soup.title else 'No title found'
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"

# Load the Excel file
file_path = 'data/list_of_ministries_and_names.xlsx'  # Replace with your file path
data = pd.read_excel(file_path)

# Define a pattern to identify file URLs
file_url_pattern = r'^file:///'

# Filter out file URLs
filtered_data = data[~data['domain'].str.contains(file_url_pattern, na=False)]

# Initialize an empty list to store the results
results = []

# Iterate over the filtered URLs and get the website names
for index, row in filtered_data.iterrows():
    url = f"http://{row['domain'].strip()}"  # Ensure the URL is well-formed
    website_name = get_website_name(url)
    results.append({'country': row['country'], 'domain': row['domain'], 'website_name': website_name})

# Convert the results into a DataFrame
results_df = pd.DataFrame(results)

# Save the results to a new Excel file
output_file_path = 'data/cabri_website_names.xlsx'  # Replace with your desired output path
results_df.to_excel(output_file_path, index=False)

print(f"Website names have been extracted and saved to {output_file_path}")
