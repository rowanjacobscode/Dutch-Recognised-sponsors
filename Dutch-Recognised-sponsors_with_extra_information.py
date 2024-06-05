import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import time

# Function to extract city names from description
def extract_city_names(description):
    if isinstance(description, str):
        match = re.search(r'gevestigd op.*?,\s*[0-9]{4}\s*[A-Z]{0,2},?\s*([^,\n]+)(\.|$)', description, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return ''

# Function to extract industry description from description
def extract_industry_description(description):
    if isinstance(description, str):
        match = re.search(r'binnen de industrie(.*?)(\.|$)', description)
        if match:
            return match.group(1).strip()
    return ''

# Function to extract founding date from description
def extract_founding_date(description):
    if isinstance(description, str):
        match = re.search(r'Het bedrijf is opgericht in (\d{4})(\.|$)', description)
        if match:
            return match.group(1).strip()
    return ''

def get_company_info(company_url):
    try:
        print(f"Fetching company info from {company_url}...")
        response = requests.get(company_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')
        # Use the correct CSS selector for the company information
        company_info_element = soup.select_one('#info > div > div.w-full.md\\:w-3\\/4.lg\\:w-7\\/12 > div > div')
        return company_info_element.text.strip() if company_info_element else 'N/A'
    except Exception as e:
        print(f'Error fetching company info from {company_url}: {e}')
        return 'N/A'

def save_data_to_csv(data, file_path):
    # Convert data to DataFrame
    df = pd.DataFrame(data)
    # Extract additional information
    df['City Names'] = df['Company Info'].apply(extract_city_names)
    df['Industry Description'] = df['Company Info'].apply(extract_industry_description)
    df['Founding Date'] = df['Company Info'].apply(extract_founding_date)
    # Write the data to a CSV file
    df.to_csv(file_path, index=False, mode='a', header=not pd.io.common.file_exists(file_path))
    print(f'Data has been written to {file_path}')

# URL of the main page
url = 'https://ind.nl/en/public-register-recognised-sponsors/public-register-regular-labour-and-highly-skilled-migrants'

# Request to fetch the page
print("Fetching main page...")
response = requests.get(url)
response.raise_for_status()  # Check if the request was successful

# HTML content of the page
soup = BeautifulSoup(response.text, 'lxml')
print("Main page fetched and parsed.")

# Find the table
table = soup.find('table')

# Lists to store organisations, KvK numbers, and KvK info URLs
organisations = []
kvk_numbers = []
kvk_info_urls = []

# Find rows in the table
rows = table.find_all('tr')

for row in rows:
    # Find organisation name and KvK number in the 'td' elements
    cells = row.find_all('td')
    if len(cells) == 2:
        organisation = cells[0].text.strip()
        organisations.append(organisation)

        kvk_number = cells[1].text.strip()
        kvk_numbers.append(kvk_number)

        # Generate KvK info URL
        kvk_info_url = f'https://www.creditsafe.com/business-index/nl-nl/search?searchQuery=&number={kvk_number}'
        kvk_info_urls.append(kvk_info_url)

print(f"Found {len(organisations)} organisations.")

# List to store the company information URLs and descriptions
company_urls = []
company_infos = []

# Variable to keep track of progress
iteration_count = 0
max_iterations = 10  # Number of iterations for intermediate saving

for kvk_info_url in kvk_info_urls:
    iteration_count += 1
    print(f"Fetching company page {iteration_count}/{len(kvk_info_urls)}: {kvk_info_url}...")
    try:
        response = requests.get(kvk_info_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')

        # Find the 'View company' button and retrieve the URL
        view_company_button = soup.select_one('a[href*="company/id"]')
        if view_company_button:
            company_url = view_company_button['href']
            if not company_url.startswith('https://'):
                company_url = 'https://www.creditsafe.com' + company_url
            print(f"Company URL found: {company_url}")
            company_urls.append(company_url)

            # Retrieve the company information
            company_info = get_company_info(company_url)
            company_infos.append(company_info)
        else:
            print(f"No 'View company' button found for {kvk_info_url}")
            company_urls.append('N/A')
            company_infos.append('N/A')
    except requests.exceptions.RequestException as e:
        print(f'Error fetching {kvk_info_url}: {e}')
        company_urls.append('N/A')
        company_infos.append('N/A')

    # Save data intermittently after every max_iterations iterations
    if iteration_count % max_iterations == 0:
        print(f"Saving intermediate data at iteration {iteration_count}...")
        # Combine all data into a list of dictionaries
        data = [{'Organisation': org, 'KvK number': kvk, 'KvK info URL': info_url, 'Company URL': company_url, 'Company Info': company_info}
                for org, kvk, info_url, company_url, company_info in
                zip(organisations[:iteration_count], kvk_numbers[:iteration_count], kvk_info_urls[:iteration_count], company_urls, company_infos)]
        save_data_to_csv(data, 'organisations_kvk.csv')

# Combine all data into a list of dictionaries
data = [{'Organisation': org, 'KvK number': kvk, 'KvK info URL': info_url, 'Company URL': company_url,
         'Company Info': company_info}
        for org, kvk, info_url, company_url, company_info in
        zip(organisations, kvk_numbers, kvk_info_urls, company_urls, company_infos)]

# CSV file path
csv_file_path = 'organisations_kvk.csv'

# Write the data to a CSV file
print("Saving final data to CSV...")
save_data_to_csv(data, csv_file_path)
print("Script completed successfully.")
