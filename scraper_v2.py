import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import time
import random
import pandas as pd
from datetime import datetime
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv
import logging

# Load environment variables from the .env file
load_dotenv()

# Retrieve the database credentials from environment variables
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")
dbname = os.getenv("DB_NAME")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")

# Validate environment variables
if not all([host, port, dbname, user, password]):
    raise ValueError("Database credentials are not fully configured. Please check your .env file.")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the session with retries
session = requests.Session()
retry = Retry(
    total=5,  # Total number of retries
    backoff_factor=5,  # Increase delay between retries
    status_forcelist=[500, 502, 503, 504]  # Retry on these HTTP status codes
)
adapter = HTTPAdapter(max_retries=retry)
session.mount("http://", adapter)
session.mount("https://", adapter)

# Set headers to mimic a browser request
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive"
}

# URL to scrape
url = "https://www.amazon.com/s?k=samsung+s24+renewed&rh=n%3A2335752011%2Cp_n_condition-type%3A16907722011&dc&ds=v1%3AdxKxZIQvEDC7xrfMik9Ys7%2B0MAowB3ytQ7i9IeDzSSk&crid=1CF8VMPT9HM8M&qid=1723641736&rnid=6503239011&sprefix=samsung+s24+renewed%2Caps%2C130&ref=sr_rib_d_web_fi_0_5_a_16907722011_1"

try:
    # Random delay to reduce the chance of getting blocked
    time.sleep(random.uniform(2, 5))

    # Send a GET request to the URL
    response = session.get(url, headers=headers)
    response.raise_for_status()  # Check if the request was successful
    logger.info(f"Connection successful: {response.status_code}")  # Log the HTTP status code

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all div elements with the class 'sg-col-inner'
    div_elements = soup.find_all('div', class_="sg-col-inner")

    logger.info(f"Number of div elements found: {len(div_elements)}")

    # Prepare a list to store the data
    data = []

    # Loop through each div element found
    for index, div in enumerate(div_elements, start=1):
        # Find the anchor tag within the current div
        anchor = div.find('a', class_="a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal")
        anchor_text = anchor.get_text(strip=True) if anchor else "N/A"
        
        # Find the span with the class 'a-price' within the current div
        span = div.find('span', class_="a-offscreen")
        span_text = span.get_text(strip=True) if span else "N/A"
        
        # Convert anchor_text to lowercase for case-insensitive comparison
        anchor_text_lower = anchor_text.lower()

        # Check for 'Samsung', 'S24', and 'Renewed' (with or without parentheses)
        contains_keywords = all(word in anchor_text_lower for word in ["samsung", "s24"])
        contains_renewed = "renewed" in anchor_text_lower or "(renewed)" in anchor_text_lower
        contains_exclusions = any(exclusion in anchor_text_lower for exclusion in ["plus", "ultra"])

        if contains_keywords and contains_renewed and not contains_exclusions:
            # Only add unique entries
            if [datetime.today().strftime('%Y-%m-%d'), anchor_text, span_text] not in data:
                # Append the results to the data list
                data.append([datetime.today().strftime('%Y-%m-%d'), anchor_text, span_text])
                logger.info(f"Added: {anchor_text} - {span_text}")  # Log each addition

    # Convert the list to a DataFrame if not empty
    if data:
        df = pd.DataFrame(data, columns=['date', 'anchor_text', 'price'])

        # Clean the 'Price' column to remove the dollar sign and convert it to a float
        df['price'] = df['price'].replace('[\$,]', '', regex=True).astype(float)

        logger.info("\n" + df.to_string(index=False))  # Log the DataFrame content

        # Establish a connection to the database using a context manager
        engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{dbname}')
        with engine.connect() as connection:
            # Write the DataFrame to the samsung_prices table
            df.to_sql('samsung_prices', connection, if_exists='append', index=False)
        logger.info("Data written to the database successfully.")
    else:
        logger.info("No matching elements found.")

except requests.exceptions.RequestException as e:
    logger.error(f"Connection failed: {e}")

except Exception as e:
    logger.error(f"An error occurred: {e}")