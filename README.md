[![Video Title](http://img.youtube.com/vi/VIDEO_ID/0.jpg)](https://www.youtube.com/watch?v=SXu2jICh01w")


Check the outcome of this project here: https://lookerstudio.google.com/u/8/reporting/1c962069-a7c8-447c-8533-d07b54ecfd96/page/p_byo2h9rlhd


# Organisation Information Scraper

This Python script automates the process of extracting organisation information from a publicly available registry of recognized sponsors for regular labour and highly skilled migrants. The script fetches data from specific URLs, processes the information, and saves it into a CSV file for easy access and manipulation.

## Features

- Fetch and parse HTML content from the web.
- Extract specific data fields: Organisation names, KvK (Chamber of Commerce) numbers, URLs, and company descriptions.
- Extract additional information: City names, industry descriptions, and founding dates.
- Save extracted data into a CSV format.
- Error handling for network requests and data extraction.

## Prerequisites

Before you can run this script, you need to install the required Python libraries. Ensure Python 3.x is installed on your system.

## Installation

Clone this repository to your local machine:

```bash
git clone https://github.com/yourusername/organisation-scraper.git
cd organisation-scraper

##Install the required Python packages:
pip install requests beautifulsoup4 pandas lxml

