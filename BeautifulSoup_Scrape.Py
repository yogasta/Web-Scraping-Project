import requests
from bs4 import BeautifulSoup
import csv
import time

def scrape_with_beautifulsoup(start_page=1, num_books=None):
    base_url = "http://books.toscrape.com/catalogue/page-{}.html"
    books_data = []
    books_scraped = 0
    page_num = start_page

    while True:
        # Fetch the page
        response = requests.get(base_url.format(page_num))
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all book links on the page
        book_links = soup.select('article.product_pod h3 a')

        for link in book_links:
            if num_books and books_scraped >= num_books:
                break

            book_url = 'http://books.toscrape.com/catalogue/' + link['href']
            book_response = requests.get(book_url)
            book_soup = BeautifulSoup(book_response.content, 'html.parser')

            # Extract book details
            title = book_soup.select_one('h1').text.strip()
            table = book_soup.select_one('table.table-striped')
            rows = table.select('tr')

            book_data = {
                'title': title,
                'upc': rows[0].select_one('td').text.strip(),
                'product_type': rows[1].select_one('td').text.strip(),
                'price_excl_tax': rows[2].select_one('td').text.strip(),
                'price_incl_tax': rows[3].select_one('td').text.strip(),
                'tax': rows[4].select_one('td').text.strip(),
                'availability': rows[5].select_one('td').text.strip(),
                'num_reviews': rows[6].select_one('td').text.strip()
            }

            books_data.append(book_data)
            books_scraped += 1
            print(f"Scraped data for: {title} (Book {books_scraped})")

        if num_books and books_scraped >= num_books:
            break

        # Check for next page
        next_button = soup.select_one('li.next a')
        if next_button:
            page_num += 1
        else:
            print("Reached the last page. Ending scraping.")
            break

        time.sleep(1)  # Be polite to the server

    # Save data to CSV
    csv_filename = "Beautiful_Soup_Scrape.csv"
    with open(csv_filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["title", "upc", "product_type", "price_excl_tax", 
                                                  "price_incl_tax", "tax", "availability", "num_reviews"])
        writer.writeheader()
        writer.writerows(books_data)

    print(f"Scraping dengan BeautifulSoup selesai. {books_scraped} buku disimpan dalam '{csv_filename}'")

scrape_with_beautifulsoup(num_books=50)