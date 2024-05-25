# This code has been written by Rowan Jacobs for a project to get more familiar writing code and build a project which solves a real problem.
# You could see the outcome of the data of this code on this url: https://lookerstudio.google.com/u/8/reporting/1c962069-a7c8-447c-8533-d07b54ecfd96/page/p_byo2h9rlhd
# If you have any recommendations or want to ask something, reach out to me on contact@rowanjacobs.nl
import requests
from bs4 import BeautifulSoup
import csv
import time

def save_data_to_csv(data, file_path):
    # Write the data to a CSV file
    with open(file_path, mode='w', newline='', encoding='utf-8') as csv_file:
        fieldnames = ['Organisation', 'KvK number', 'KvK info URL', 'Company URL', 'Company Info']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        writer.writeheader()
        for entry in data:
            writer.writerow(entry)

    print(f'Data has been written to {file_path}')

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

# URL of the main page
url = 'https://ind.nl/en/public-register-recognised-sponsors/public-register-regular-labour-and-highly-skilled-migrants'

# Request to fetch the page
print("Fetching main page...")
response = requests.get(url)
response.raise_for_status()  # Check if the request was successful

# HTML content of the page
soup = BeautifulSoup(response.text, 'lxml')
print("Main page fetched and parsed.")

# Find tables
table = soup.find('table')

# Lists to store organisations, KvK numbers, and KvK info URLs
organisations = []
kvk_numbers = []
kvk_info_urls = []

# Find rows in the table
rows = table.find_all('tr')

for row in rows:
    # Find organisation name
    org_cell = row.find('th', scope='row')
    if org_cell:
        organisation = org_cell.text.strip()
        organisations.append(organisation)

        # Find KvK number
        kvk_cell = row.find('td')
        if kvk_cell:
            kvk_number = kvk_cell.text.strip()
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
        bekijk_bedrijf_button = soup.select_one('a[href*="company/id"]')
        if bekijk_bedrijf_button:
            company_url = bekijk_bedrijf_button['href']
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
        data = [{'Organisation': org, 'KvK number': kvk, 'KvK info URL': info_url, 'Company URL': company_url,
                 'Company Info': company_info}
                for org, kvk, info_url, company_url, company_info in
                zip(organisations[:iteration_count], kvk_numbers[:iteration_count], kvk_info_urls[:iteration_count],
                    company_urls, company_infos)]
        save_data_to_csv(data, 'organisations_kvk_intermediate.csv')

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
