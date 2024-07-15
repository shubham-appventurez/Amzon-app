import requests
from bs4 import BeautifulSoup
import psycopg2

def store_data_in_postgresql(data, db_config):
    try:
        connection = psycopg2.connect(
            user=db_config['user'],
            password=db_config['password'],
            host=db_config['host'],
            port=db_config['port'],
            database=db_config['database']
        )
        cursor = connection.cursor()
        
        insert_query = """
        INSERT INTO products (title, price, rating, review_count, availability, description)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, data)
        connection.commit()

        print(f"Inserted data into PostgreSQL")

    except (Exception, psycopg2.Error) as error:
        print(f"Error while connecting to PostgreSQL: {error}")

    finally:
        if connection:
            cursor.close()
            connection.close()

def main(URL, db_config):
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0", 
        "Accept-Encoding": "gzip, deflate", 
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", 
        "DNT": "1", 
        "Connection": "close", 
        "Upgrade-Insecure-Requests": "1"
    }

    webpage = requests.get(URL, headers=HEADERS)
    soup = BeautifulSoup(webpage.content, "lxml")

    # retrieving product title
    try:
        title = soup.find("span", attrs={"id": 'productTitle'}).get_text().strip().replace(',', '')
    except AttributeError:
        title = "NA"
    print("Product Title =", title)

    # retrieving price
    price = "NA"
    try:
        price = soup.find("span", attrs={'class': 'a-price-whole'}).get_text().strip().replace(',', '')
        price_fraction = soup.find("span", attrs={'class': 'a-price-fraction'}).get_text().strip()
        price = price + price_fraction
    except AttributeError:
        try:
            price = soup.find("span", attrs={'id': 'priceblock_ourprice'}).get_text().strip().replace(',', '')
        except AttributeError:
            try:
                price = soup.find("span", attrs={'id': 'priceblock_dealprice'}).get_text().strip().replace(',', '')
            except AttributeError:
                price = "NA"
    print("Product Price =", price)

    # retrieving product rating
    try:
        rating = soup.find("i", attrs={'class': 'a-icon a-icon-star a-star-4-5'}).get_text().strip().replace(',', '')
    except AttributeError:
        try:
            rating = soup.find("span", attrs={'class': 'a-icon-alt'}).get_text().strip().replace(',', '')
        except AttributeError:
            rating = "NA"
    print("Overall Rating =", rating)

    # retrieving review count
    try:
        review_count = soup.find("span", attrs={'id': 'acrCustomerReviewText'}).get_text().strip().replace(',', '')
    except AttributeError:
        review_count = "NA"
    print("Total Reviews =", review_count)

    # retrieving availability status
    try:
        available = soup.find("div", attrs={'id': 'availability'}).find("span").get_text().strip().replace(',', '')
    except AttributeError:
        available = "NA"
    print("Availability =", available)

    # retrieving product description
    try:
        description = soup.find("div", attrs={'id': 'productDescription'}).find("p").get_text().strip().replace(',', '')
    except AttributeError:
        description = "NA"
    print("Product Description =", description)

    data = (title, price, rating, review_count, available, description)
    store_data_in_postgresql(data, db_config)

if __name__ == '__main__':
    db_config = {
        'host': 'localhost',
        'port': '5432',
        'user': 'shubham2',
        'password': 'shubham@2325',
        'database': 'amazon2'
    }

    with open("url.txt", "r") as file:
        for links in file.readlines():
            main(links.strip(), db_config)
