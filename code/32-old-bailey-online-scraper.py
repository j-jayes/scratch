import pandas as pd
import requests

url = "https://www.oldbaileyonline.org/robots.txt"
response = requests.get(url)
print(response.text)

# this scraper collects results from the search pane.

import pandas as pd
from bs4 import BeautifulSoup

# Load the HTML file into BeautifulSoup
with open("data/Search _ Keyword _ The Proceedings of the Old Bailey.html", "r", encoding="utf-8") as file:
    soup = BeautifulSoup(file, "html.parser")

def get_result_links(soup):
    result_entries = soup.find_all('div', class_='row')

    results = []
    for entry in result_entries:
        a_tag = entry.find('a', class_='text-decoration-none text-black')
        if a_tag:
            href = a_tag['href']
            title = a_tag.find('h3', class_='hit-title').get_text(strip=True) if a_tag.find('h3', class_='hit-title') else 'No title found'
            text = entry.find('div', class_='hit-text').get_text(strip=True) if entry.find('div', class_='hit-text') else 'No text found'

            results.append({
                "title": title,
                "text": text,
                "href": href
            })

    return pd.DataFrame(results).drop_duplicates()

get_result_links(soup)

import pandas as pd
from bs4 import BeautifulSoup


# Since we have the HTML content, we don't need to make a request. Let's parse the HTML directly.
# I'll use the HTML content from the uploaded file.

# Load the HTML content from the uploaded file
file_path = 'data/t16750414-1 _ The Proceedings of the Old Bailey.html'
with open(file_path, 'r') as file:
    html_content = file.read()

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(html_content, 'html.parser')


# Extract the title
title = soup.find('h1', class_='display-7').text.strip()

# Extract the link to the gif file
gif_link_element = soup.find('figure', class_='figure mb-5 old-bailey-page-figure')
gif_link = gif_link_element.find('a')['href'] if gif_link_element else None

# extract paths that contain "www.dhi.ac.uk" and ".gif" from soup
gif_link = soup.find('img', src=lambda x: x and 'www.dhi.ac.uk' in x and x.endswith('.gif'))['src']

# find all img tags in the soup
img_tags = soup.find_all('img')
# filter for the img tags that contain "www.dhi.ac.uk" and ".gif" in their src attribute


# Create a dictionary to store the data, starting with the title and gif link
record_dict = {
    'Title': title,
    'GIF Link': gif_link,
}

# Extract the table contents and add them to the dictionary
table = soup.find('table', class_='table')
for row in table.find_all('tr'):
    header = row.find('th').get_text(strip=True)
    value = row.find('td').get_text(strip=True)
    # We will normalize the header names here
    header = ' '.join(header.split()).replace(' ', '_')
    record_dict[header] = value

# Extract the trial text and add it to the dictionary
trial_text_element = soup.find('div', class_='source-text')
trial_text = trial_text_element.get_text(strip=True) if trial_text_element else None
record_dict['Trial_Text'] = trial_text

# Create a DataFrame from the dictionary
final_df = pd.DataFrame([record_dict])

# The gif link needs to be corrected because it's a relative path, we assume it should be relative to the main domain of oldbaileyonline.org
final_df['GIF Link'] = final_df['GIF Link'].apply(lambda x: 'https://www.oldbaileyonline.org' + x if x else None)

# Display the resulting DataFrame
final_df

# pivot longer
final_df = final_df.melt(var_name='Column', value_name='Value')

# Display the resulting DataFrame
final_df