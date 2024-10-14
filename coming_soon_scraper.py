import time
import requests
from bs4 import BeautifulSoup
import pandas as pd
import logging

# Function to generate cookie
from cookie import cookie_gen

# First, generate the cookie using the cookie_gen function
cookie_data = cookie_gen("https://www.klwines.com/", 'E75BA910209FD799C4CED89BDD05EB')
cookie_value = cookie_data['value']  # Get the cookie from the result

cookies = {
    'datadome': cookie_value,
}

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:131.0) Gecko/20100101 Firefox/131.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Referer': 'https://www.klwines.com/',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Priority': 'u=0, i',
}

# Parameters for the GET request
params = {
    'filters': 'sv2_47$eq$1$True$coming-soon$and,58$gt$0$True$$.and,57$le$0$True$$.and,48$eq$0$True$$!dflt-stock-all',
    'limit': '50',
    'offset': '0',  # Start at 0, we'll increment this for pagination
    'orderBy': '60 asc,search.score() desc',
    'searchText': '',
}

# Set up logging
logging.basicConfig(filename='coming_soon.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# CSV file setup and pandas DataFrame initialization
csv_file = "coming_soon.csv"
data_columns = ["Product Name", "SKU", "Price", "Description", "Image URL", "Link"]
df = pd.DataFrame(columns=data_columns)

# Pagination and saving setup
save_every_n_runs = 5  # Save data every n requests
runs_count = 0  # To track the number of requests

# Function to parse the HTML and return a DataFrame
def parse_page_to_dataframe(html):
    soup = BeautifulSoup(html, 'html.parser')
    product_divs = soup.find_all('div', class_='tf-product-content')

    # Prepare the data to write into DataFrame
    data = []
    for product in product_divs:
        try:
            # Extract product details
            product_name = product.find('a').text.strip()
            product_link = "https://www.klwines.com" + product.find('a')['href']
            description = product.find('div', class_='tf-product-description').text.strip()
            image_url = product.find('img')['src']

            # Extract product SKU (from the URL or embedded data)
            sku = product.find('a')['data-app-insights-track-search-doc-id']

            # Extract price (handle "Hidden" price scenario)
            price_div = product.find_next('div', class_='tf-price')
            price = price_div.find('span', class_='global-pop-color').text.strip() if price_div else "Hidden"

            # Append the data
            data.append([product_name, sku, price, description, image_url, product_link])

        except Exception as e:
            logging.error(f"Error parsing product: {e}")
            continue  # Skip this product if there's an error

    return pd.DataFrame(data, columns=data_columns)

# Pagination loop
offset = 0
while True:
    params['offset'] = str(offset)
    try:
        response = requests.get('https://www.klwines.com/Products', params=params, cookies=cookies, headers=headers)
        response.raise_for_status()  # Raise an error for bad HTTP responses
        logging.info(f"Successfully fetched data at offset {offset}")

        html = response.text
        page_df = parse_page_to_dataframe(html)

        if page_df.empty:
            logging.info(f"No more data found, ending pagination at offset {offset}")
            break  # Exit the loop if no data is found

        # Append the data from this page to the main DataFrame
        df = pd.concat([df, page_df], ignore_index=True)

        # Increment the request counter and save the DataFrame every n runs
        runs_count += 1
        if runs_count % save_every_n_runs == 0:
            df.to_csv(csv_file, index=False)
            logging.info(f"Data saved to {csv_file} after {runs_count} requests.")

        # Increment offset for the next page (next batch of 50 results)
        offset += 50

        # Delay to prevent overloading the server
        time.sleep(1)

    except requests.RequestException as e:
        logging.error(f"Request failed at offset {offset}: {e}")
        break

# Save any remaining data
if not df.empty:
    df.to_csv(csv_file, index=False)
    logging.info(f"Final data saved to {csv_file}.")
else:
    logging.info("No data to save.")

print("Data extraction completed.")
