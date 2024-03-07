import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# Base URL for fetching bank names and links
BASE_URL = "https://www.iban.co.za/"

def fetch_bank_links(base_url):
    """Fetches bank names and their links from the base URL."""
    response = requests.get(base_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    banks_with_links = [{
        'Bank Name': link.text,
        'Link': base_url + link['href']
    } for link in soup.find_all('a', class_='list-group-item')]
    return pd.DataFrame(banks_with_links)

def get_number_of_pages(url):
    """Determines the number of pagination pages for a given bank's URL."""
    print(f"Getting number of pages for {url}")
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    pages = soup.find('ul', class_='pagination')
    if pages:
        return len(pages.find_all('li')) - 1  # Adjusting for 'Next' button
    return 1

def construct_page_urls(bank_link, num_pages):
    """Constructs URLs for all pages of a bank's branch listing."""
    # Remove .html from the bank_link
    bank_link = bank_link.rsplit('.html', 1)[0]
    if num_pages > 1:
        return [f"{bank_link}-{i}.html" if i != 1 else f"{bank_link}.html" for i in range(1, num_pages + 1)]
    return [f"{bank_link}.html"]


def extract_branch_info_from_bank_page(url):
    """Extracts branch information from a bank's branch listing page."""
    # print the URL to keep track of the progress along with a message
    print(f"Extracting branch info from {url}")
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', class_='table table-hover table-bordered table-striped sortable')
    rows = table.find_all('tr')[1:]  # Skip header row

    branch_details = [{
        'branch_name': row.find_all('td')[0].text.strip(),
        'address': row.find_all('td')[1].text.strip(),
        'city': row.find_all('td')[2].text.strip(),
        'branch_code': row.find_all('td')[3].text.strip()
    } for row in rows if len(row.find_all('td')) == 4]

    return pd.DataFrame(branch_details)



def extract_branch_info_from_branch_code(url):
    """Extracts branch information from a bank's branch code page."""
    print(f"Extracting branch info from {url}")
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    branch_info = {
        'branch_code': '',
        'bic_code_swift': '',
        'bank_name': '',
        'bank_branch': '',
        'bank_branch_address': '',
        'city': '',
        'bank_phone': '',
        'bank_fax': ''
    }
    
    label_mapping = {
        'Branch Code:': 'branch_code',
        'BIC Code (Swift):': 'bic_code_swift',
        'Bank Name:': 'bank_name',
        'Bank Branch:': 'bank_branch',
        'Bank Branch Address:': 'bank_branch_address',
        'City:': 'city',
        'Bank Phone:': 'bank_phone',
        'Bank Fax:': 'bank_fax'
    }
    
    rows = soup.find('table', class_='table table-hover table-bordered table-striped').find_all('tr')
    
    for row in rows:
        cells = row.find_all('td')
        if len(cells) == 2:
            label_text = cells[0].get_text(strip=True)
            value_text = cells[1].get_text(strip=True)
            if label_text in label_mapping:
                dict_key = label_mapping[label_text]
                branch_info[dict_key] = value_text
    
    df = pd.DataFrame([branch_info])

    # sleep for 1 second to avoid being blocked
    time.sleep(1)
    
    return df



def main():
    banks_df = fetch_bank_links(BASE_URL)
    banks_df['Number of Pages'] = banks_df['Link'].apply(get_number_of_pages)
    banks_df['Page URLs'] = banks_df.apply(lambda row: construct_page_urls(row['Link'], row['Number of Pages']), axis=1)
    banks_df = banks_df.explode('Page URLs').reset_index(drop=True)
    # keep unique URLs
    banks_df = banks_df.drop_duplicates(subset='Page URLs')

    all_branches = pd.DataFrame()
    for url in banks_df['Page URLs']:
        branches = extract_branch_info_from_bank_page(url)
        all_branches = pd.concat([all_branches, branches], ignore_index=True)

    # save to a CSV file
    all_branches.to_csv('data/iban/branch_codes.csv', index=False)

    all_branches["branch_code_link"] = all_branches["branch_code"].apply(lambda x: f"https://www.iban.co.za/branch-code-{x}.html")

    # loop through the branch code links to get the branch details and save to a CSV file
    all_branch_details = pd.DataFrame()
    for url in all_branches["branch_code_link"]:
        branch_details = extract_branch_info_from_branch_code(url)
        all_branch_details = pd.concat([all_branch_details, branch_details], ignore_index=True)

    all_branch_details.to_csv('data/iban/branch_details.csv', index=False)

if __name__ == "__main__":
    main()


