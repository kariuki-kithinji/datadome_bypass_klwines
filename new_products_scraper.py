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

params = {
    'filters': 'sv2_NewProductFeedYN$eq$1$True$ProductFeed$!dflt-stock-all',
    'orderBy': 'NewProductFeedDate desc',
    'limit': '50',
    'offset': '0'  # Will update this for pagination
}

# Set up logging
logging.basicConfig(filename='new_product_feed.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# CSV file setup and pandas DataFrame initialization
csv_file = "new_product_feed.csv"
data_columns = ["Date", "SKU", "Vintage", "Item Name", "List Price", "Quantity On Hand", "Allocation"]
df = pd.DataFrame(columns=data_columns)

# Pagination and saving setup
save_every_n_runs = 5  # Save data every n requests
runs_count = 0  # To track the number of requests

# Function to parse the HTML table and return a DataFrame
def parse_table_to_dataframe(html):
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table')  # Locate the table in the HTML
    if not table:
        return pd.DataFrame()  # Return empty DataFrame when no table is found

    tbody = table.find('tbody')
    rows = tbody.find_all('tr')

    # Prepare the data to write into DataFrame
    data = []
    for row in rows:
        cols = row.find_all('td')
        if len(cols) == 7:
            row_data = [col.get_text(strip=True) for col in cols]
            data.append(row_data)

    return pd.DataFrame(data, columns=data_columns)

# Pagination loop
offset = 0
while True:
    params['offset'] = str(offset)
    try:
        response = requests.get('https://www.klwines.com/p/Index', params=params, cookies=cookies, headers=headers)
        response.raise_for_status()  # Raise an error for bad HTTP responses
        logging.info(f"Successfully fetched data at offset {offset}")

        html = response.text
        page_df = parse_table_to_dataframe(html)

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
