from flask import Flask, request, render_template, redirect, url_for

import requests
from bs4 import BeautifulSoup
import psycopg2

app = Flask(__name__)

# PostgreSQL database credentials
DB_HOST = 'localhost'
DB_NAME = 'amazon2'
DB_USER = 'amazon2'
DB_PASSWORD = 'amazon2'


# Function to scrape product details from Amazon URL
def scrape_product_details(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
        "Accept-Encoding": "gzip, deflate",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "DNT": "1",
        "Connection": "close",
        "Upgrade-Insecure-Requests": "1"
    }

    try:
        payload = {'api_key': '3142121171b303719d9d5532639849d6', 'url': url}
        response = requests.get('https://api.scraperapi.com/', params=payload, headers=headers)
        response.raise_for_status()  # Raise HTTPError for bad responses

        soup = BeautifulSoup(response.content, "html5lib")

        # Extracting product title
        title_elem = soup.find("span", attrs={"id": 'productTitle'})
        title = title_elem.get_text().strip().replace(',', '') if title_elem else "NA"

        # Extracting product price
       # Extracting product price
        price_elem = soup.find("span", class_='a-offscreen')
        price = price_elem.get_text().strip().replace(',', '') if price_elem else "NA"

        # Extracting product rating
        rating_elem = soup.find("span", class_='a-icon-alt')
        rating = rating_elem.get_text().strip().replace(',', '') if rating_elem else "NA"


        # Extracting review count
        reviews_count_elem = soup.find("span", attrs={'id': 'acrCustomerReviewText'})
        reviews_count = reviews_count_elem.get_text().strip().replace(',', '') if reviews_count_elem else "NA"

        # Extracting availability status
        availability_elem = soup.find("div", attrs={'id': 'availability'})
        availability = availability_elem.find("span").get_text().strip().replace(',', '') if availability_elem else "NA"

        # Extracting product description
        description_elem = soup.find("div", attrs={'id': 'productDescription'})
        description = description_elem.find("p").get_text().strip().replace(',', '') if description_elem and description_elem.find("p") else "NA"


        # Extracting product images
        images = [img['src'] for img in soup.find_all('img', class_='a-dynamic-image')]

        # Extracting seller details
        seller_elem = soup.find("a", attrs={'id': 'sellerProfileTriggerId'})
        seller = seller_elem.get_text().strip().replace(',', '') if seller_elem else "NA"

        return {
            "title": title,
            "price": price,
            "rating": rating,
            "reviews_count": reviews_count,
            "availability": availability,
            "description": description,
            "images": images,
            "seller": seller
        }

    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

# Function to save product details to PostgreSQL database
def save_to_database(data):
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO products (title, price, rating, reviews_count, availability, description, images, seller)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (data['title'], data['price'], data['rating'], data['reviews_count'], data['availability'], data['description'], data['images'], data['seller']))
    conn.commit()
    cursor.close()
    conn.close()

# Route for home page
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        data = scrape_product_details(url)
        if data:
            save_to_database(data)
            return render_template('results.html', product=data)
        else:
            return "Error fetching product details. Please try again later."
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
