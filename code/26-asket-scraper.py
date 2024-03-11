import pandas as pd
import requests
from bs4 import BeautifulSoup
import time

# Updated list of URLs
# List of URLs
urls = [
    "https://www.asket.com/se/mens/t-shirts",
    "https://www.asket.com/se/mens/shirts",
    "https://www.asket.com/se/mens/knitwear",
    "https://www.asket.com/se/mens/trousers",
    "https://www.asket.com/se/mens/outerwear",
    "https://www.asket.com/se/mens/sweatshirts",
    "https://www.asket.com/se/mens/underwear"
]

urls = [
    "https://www.asket.com/se/womens/t-shirts",
    "https://www.asket.com/se/womens/shirts",
    "https://www.asket.com/se/womens/knitwear",
    "https://www.asket.com/se/womens/denim",


]

def send_request(url):
    """
    Sends a GET request to the specified URL and returns the BeautifulSoup object if successful.
    
    Args:
    - url: URL to send the GET request to.
    
    Returns:
    - BeautifulSoup object of the page content.
    """
    try:
        with requests.Session() as session:
            response = session.get(url)
            response.raise_for_status()  # Raise an error for bad responses
            return BeautifulSoup(response.text, "html.parser")
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return None

def extract_product_links(url):
    """
    Extracts product links from the provided URL of a product listing page.
    """
    soup = send_request(url)
    if soup is None: return []

    product_links = [link['href'] for link in soup.find_all("a", href=True) if "/se/womens/" in link['href']]
    full_urls = [f"https://www.asket.com{href}" if not href.startswith("http") else href for href in set(product_links)]
    
    return full_urls

def extract_details(url, detail_type):
    """
    General function to extract details from a product page based on the type (cost, traceability, or impact), as well as the name.
    """
    soup = send_request(url)
    if soup is None: return {}

    if detail_type == "cost":
        return extract_all_cost_details(soup)
    elif detail_type == "traceability":
        return extract_traceability_details(soup)
    elif detail_type == "impact":
        return extract_climate_impact_details(soup)
    elif detail_type == "name":
        return extract_product_name(soup)
    else:
        return {}

def extract_all_cost_details(soup):
    # Extracting the general cost information (Landed Cost, Asket Price, Traditional Retail)
    general_costs_elements = soup.find_all(class_="progress-label-desktop")
    general_costs = {
        "Landed Cost": general_costs_elements[0].text.strip() if general_costs_elements else "",
        "Asket Price": general_costs_elements[1].text.strip() if len(general_costs_elements) > 1 else "",
        "Traditional Retail": general_costs_elements[2].text.strip() if len(general_costs_elements) > 2 else ""
    }
    # Extracting the detailed landed cost breakdown
    legends = soup.find_all(class_="legends-desktop")[0].find_all("li")
    detailed_costs = {}
    for legend in legends:
        category_cleaned = " ".join(legend.text.rsplit(' ', 1)[0].split()[:-1])
        # strip any numbers from category_cleaned and then strip any whitespace
        category_cleaned = ''.join([i for i in category_cleaned if not i.isdigit()]).strip()
        cost = legend.find("strong").text.strip()
        detailed_costs[category_cleaned] = cost
    
    # Combining both general and detailed costs into one dictionary
    all_cost_details = {**general_costs, **detailed_costs}
    
    return all_cost_details

def extract_traceability_details(soup):
    # Extraction logic for traceability details
    trace_sections = soup.find_all(class_="section-tabs")[0].find_all("button")
    traceability_details = {}
    
    for section in trace_sections:
        label = section.find(class_="label").text.strip()
        value = section.find(class_="progress-value").text.strip()
        traceability_details[label] = value
    
    # Extracting overall traceability percentage
    overall_traceability = soup.find(class_="overall-trace").text.strip()
    
    # Adding overall traceability to the details
    traceability_details['Overall Traceability'] = overall_traceability
    
    return traceability_details

def extract_climate_impact_details(soup):
    # Extraction logic for climate impact details
    impact_sections = soup.find_all(class_="impact-info")[0].find_all(class_="impact-item")
    climate_impact_details = {}
    
    for item in impact_sections:
        impact_name = item.find(class_="impact-name").text.strip()
        impact_value = item.find(class_="progress-value").text.strip()
        climate_impact_details[impact_name] = impact_value
    
    return climate_impact_details

def extract_product_name(soup):
    # Extraction logic for the product name
    print(f"Extracting product name from {soup.title.string}")
    return {"Name": soup.find(class_="name").text.strip()}

def main():
    all_data = []
    for url in urls:
        product_urls = extract_product_links(url)
        # filter the URLs so that there are enough parts to the URL, e.g. https://www.asket.com/se/mens/t-shirts/lightweight-t-shirt-dark-navy, not https://www.asket.com/se/mens/t-shirts
        product_urls = [product_url for product_url in product_urls if len(product_url.split("/")) > 6]
        for product_url in product_urls:
            product_details = {}
            product_details = {"Product URL": product_url}  # Initialize the dictionary with the product URL
            for detail_type in ["cost", "traceability", "impact", "name"]:
                product_details.update(extract_details(product_url, detail_type))
            # sleep for 1 second before the next request
            time.sleep(1)
            all_data.append(product_details)

    df_all_data = pd.DataFrame(all_data)
    df_all_data.to_csv('data/asket/asket_data_womens.csv', index=False)

    df_all_data.columns

if __name__ == "__main__":
    main()
