from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)

# Define Amazon URLs for different regions
amazon_urls = {
    'US': 'https://www.amazon.com/s?k={product_name}',
    'UK': 'https://www.amazon.co.uk/s?k={product_name}',
    'CA': 'https://www.amazon.ca/s?k={product_name}',
    'DE': 'https://www.amazon.de/s?k={product_name}',
    'FR': 'https://www.amazon.fr/s?k={product_name}',
    'ES': 'https://www.amazon.es/s?k={product_name}',
    'IT': 'https://www.amazon.it/s?k={product_name}',
    'JP': 'https://www.amazon.co.jp/s?k={product_name}',
    'IN': 'https://www.amazon.in/s?k={product_name}',
    'AU': 'https://www.amazon.com.au/s?k={product_name}'
    # Add more regions as needed
}

def clean_price(price_str):
    # Remove non-numeric characters and convert to float
    cleaned_price = re.sub(r'[^\d.]', '', price_str)
    return float(cleaned_price) if cleaned_price else 0.0

def search_amazon_product(product_name, region):
    all_results = []

    # Search in the selected region
    if region in amazon_urls:
        url = amazon_urls[region].format(product_name=product_name)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Connection": "keep-alive"
        }
        payloads = { 'api_key': '3142121171b303719d9d5532639849d6', 'url': url }

        # Send GET request to Amazon
        response = requests.get('https://api.scraperapi.com/',params=payloads, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            # Example: Extracting product details (name, price, rating, availability, link)
            product_details = []
            product_cards = soup.find_all('div', {'class': 's-result-item'})

            for card in product_cards:
                # Extracting product name
                name_element = card.find('span', {'class': 'a-size-medium a-color-base a-text-normal'})
                if name_element:
                    name = name_element.text.strip()
                else:
                    continue

                # Extracting product price
                price_element = card.find('span', {'class': 'a-offscreen'})
                if price_element:
                    price = price_element.text.strip()
                else:
                    price = 'Price not available'

                # Clean and convert product price
                cleaned_price = clean_price(price)

                # Extracting product rating
                rating_element = card.find('span', {'class': 'a-icon-alt'})
                if rating_element:
                    rating = rating_element.text.strip().split()[0]
                else:
                    rating = 'Rating not available'

                # Extracting product availability
                availability_element = card.find('span', {'class': 'a-size-base'})
                if availability_element:
                    availability = availability_element.text.strip()
                else:
                    availability = 'Availability not available'

                # Extracting product link
                link_element = card.find('a', {'class': 'a-link-normal'})
                if link_element:
                    link = 'https://www.amazon.com' + link_element.get('href')
                else:
                    link = 'Link not available'

                # Append product details to list
                product_details.append({
                    'Name': name,
                    'Price': price,
                    'CleanedPrice': cleaned_price,
                    'Rating': rating,
                    'Availability': availability,
                    'Link': link,
                    'Region': region
                })

            # Sort results by cleaned price in ascending order
            product_details.sort(key=lambda x: x['CleanedPrice'])

            # Append results for the current region to all_results
            all_results.extend(product_details)

        else:
            print(f"Failed to retrieve data from Amazon {region}. Status code: {response.status_code}")

    else:
        print(f"Region '{region}' is not supported.")

    # Collect results for all other regions
    for other_region, other_url in amazon_urls.items():
        if other_region != region:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                "Connection": "keep-alive"
            }
            payloads = { 'api_key': '3142121171b303719d9d5532639849d6', 'url': other_url }

            # Send GET request to Amazon
            response = requests.get('https://api.scraperapi.com/',params=payloads, headers=headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # Example: Extracting product details (name, price, rating, availability, link)
                product_cards = soup.find_all('div', {'class': 's-result-item'})

                for card in product_cards:
                    # Extracting product name
                    name_element = card.find('span', {'class': 'a-size-medium a-color-base a-text-normal'})
                    if name_element:
                        name = name_element.text.strip()
                    else:
                        continue

                    # Extracting product price
                    price_element = card.find('span', {'class': 'a-offscreen'})
                    if price_element:
                        price = price_element.text.strip()
                    else:
                        price = 'Price not available'

                    # Clean and convert product price
                    cleaned_price = clean_price(price)

                    # Extracting product rating
                    rating_element = card.find('span', {'class': 'a-icon-alt'})
                    if rating_element:
                        rating = rating_element.text.strip().split()[0]
                    else:
                        rating = 'Rating not available'

                    # Extracting product availability
                    availability_element = card.find('span', {'class': 'a-size-base'})
                    if availability_element:
                        availability = availability_element.text.strip()
                    else:
                        availability = 'Availability not available'

                    # Extracting product link
                    link_element = card.find('a', {'class': 'a-link-normal'})
                    if link_element:
                        link = link_element.get('href')
                    else:
                        link = 'Link not available'

                    # Append product details to list
                    all_results.append({
                        'Name': name,
                        'Price': price,
                        'CleanedPrice': cleaned_price,
                        'Rating': rating,
                        'Availability': availability,
                        'Link': link,
                        'Region': other_region
                    })

            else:
                print(f"Failed to retrieve data from Amazon {other_region}. Status code: {response.status_code}")

    return all_results

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        product_name = request.form['product_name']
        region = request.form['region'].upper()

        # Perform Amazon search in the specified region
        results = search_amazon_product(product_name, region)

        if results:
            # Sort results by cleaned price in ascending order
            sorted_results = sorted(results, key=lambda x: x['CleanedPrice'])

            # Render results template
            return render_template('results.html', results=sorted_results, product_name=product_name, region=region)
        else:
            return render_template('error.html', message="Failed to fetch data from Amazon.")

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
