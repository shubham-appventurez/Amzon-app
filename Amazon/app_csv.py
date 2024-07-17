from flask import Flask, request, render_template, redirect, url_for
import requests
from bs4 import BeautifulSoup
import csv  
import os

app = Flask(__name__)

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
        price_elem = soup.find("span", class_='a-offscreen')
        price = price_elem.get_text().strip().replace(',', '') if price_elem else "NA"

        # Extracting product rating
        rating_elem = soup.find("i", class_='a-icon a-icon-star a-star-4-5')
        rating = rating_elem.get_text().strip().replace(',', '') if rating_elem else "NA"

        # Extracting review count
        reviews_count_elem = soup.find("span", attrs={'id': 'acrCustomerReviewText'})
        reviews_count = reviews_count_elem.get_text().strip().replace(',', '') if reviews_count_elem else "NA"

        # Extracting availability status
        availability_elem = soup.find("div", attrs={'id': 'availability'})
        availability = availability_elem.find("span").get_text().strip().replace(',', '') if availability_elem else "NA"

        # Extracting product description
        description_elem = soup.find("div", attrs={'id': 'productDescription'})
        description = description_elem.find("p").get_text().strip().replace(',', '') if description_elem else "NA"

         # Extracting product images
        images = [img['src'] for img in soup.find_all('img', class_='a-dynamic-image')]

        # Extracting images from input tags with class 'a-button-input'
        images = []
        vertical_images = soup.find_all('img', class_='a-dynamic-image a-stretch-vertical')
        horizontal_images = soup.find_all('img', class_='a-dynamic-image a-stretch-horizontal')
        
        for img in vertical_images:
            images.append(img['src'])
        
        for img in horizontal_images:
            images.append(img['src'])

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


# Function to save product details to CSV file with headers
def save_to_csv(data):
    csv_file = 'product_details.csv'
    file_exists = os.path.isfile(csv_file)  # Check if CSV file exists

    with open(csv_file, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        # Write headers if the file is newly created
        if not file_exists:
            writer.writerow([
                "Title",
                "Price",
                "Rating",
                "Reviews Count",
                "Availability",
                "Description",
                "Images",
                "Seller"
            ])

        # Write product data
        writer.writerow([
            data['title'],
            data['price'],
            data['rating'],
            data['reviews_count'],
            data['availability'],
            data['description'],
            ', '.join(data['images']),  # Convert images list to string for CSV
            data['seller']
        ])

# Route for home page
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        data = scrape_product_details(url)
        if data:
            save_to_csv(data)  # Save data to CSV file if scraping succeeded
            return render_template('results.html', product=data)
        else:
            return "Error fetching product details from URL."
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
