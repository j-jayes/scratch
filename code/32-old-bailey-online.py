## Purpose
# Explore the Old Bailey API
import requests
import pandas as pd

# URL of the API endpoint
url = "https://www.dhi.ac.uk/api/data/oldbailey_record?text=theft&from=20&size=10"

# Make the HTTP GET request to the API
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    data = response.json()  # Parse JSON response
    total_hits = data['hits']['total']  # Get the total number of results
    records = data['hits']['hits']  # Extract the relevant part of the JSON

    # Display the total number of results
    print(f"Total number of results: {total_hits}")

    # Initialize an empty list to store each record as a dictionary
    rows = []

    # Loop through each record and gather the necessary data
    for record in records:
        # Extract necessary fields from each record
        row = {
            'id': record['_id'],
            'index': record['_index'],
            'type': record['_type'],
            'idkey': record['_source']['idkey'],
            'text': record['_source']['text'],
            'title': record['_source']['title'],
            'images': record['_source']['images']
        }
        rows.append(row)

    # Create a DataFrame from the list of dictionaries
    df = pd.DataFrame(rows)

    # Display the DataFrame
    print(df)
else:
    print(f"Failed to retrieve data: {response.status_code}")



df.to_excel('old-bailey-mountain.xlsx', index=False)