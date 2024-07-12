from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import csv
import time

def scrape_with_selenium(start_page=1, num_books=None):
    # Setup Selenium
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Initialize list to store data
    books_data = []
    base_url = "http://books.toscrape.com/catalogue/page-{}.html"
    page_num = start_page
    books_scraped = 0

    while True:
        # Navigate to the catalogue page
        current_url = base_url.format(page_num)
        driver.get(current_url)

        # Wait for the book elements to load
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "article.product_pod"))
            )
        except TimeoutException:
            print(f"Timeout waiting for page {page_num} to load. Ending scraping.")
            break

        # Extract all book URLs from the current page
        book_urls = [element.get_attribute('href') for element in 
                     driver.find_elements(By.CSS_SELECTOR, "article.product_pod h3 a")]

        # Visit each book page and extract data
        for url in book_urls:
            if num_books is not None and books_scraped >= num_books:
                break

            driver.get(url)
            
            try:
                # Wait for the product information to load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "table.table-striped"))
                )

                # Extract detailed information
                title = driver.find_element(By.CSS_SELECTOR, "h1").text
                table = driver.find_element(By.CSS_SELECTOR, "table.table-striped")
                rows = table.find_elements(By.TAG_NAME, "tr")
                
                book_data = {
                    "title": title,
                    "upc": rows[0].find_element(By.TAG_NAME, "td").text,
                    "product_type": rows[1].find_element(By.TAG_NAME, "td").text,
                    "price_excl_tax": rows[2].find_element(By.TAG_NAME, "td").text,
                    "price_incl_tax": rows[3].find_element(By.TAG_NAME, "td").text,
                    "tax": rows[4].find_element(By.TAG_NAME, "td").text,
                    "availability": rows[5].find_element(By.TAG_NAME, "td").text.strip(),
                    "num_reviews": rows[6].find_element(By.TAG_NAME, "td").text
                }

                books_data.append(book_data)
                books_scraped += 1
                print(f"Scraped data for: {title} (Book {books_scraped})")

            except (TimeoutException, NoSuchElementException) as e:
                print(f"Error scraping book at {url}: {str(e)}")

        if num_books is not None and books_scraped >= num_books:
            print(f"Reached the desired number of books ({num_books}). Ending scraping.")
            break

        # Navigate back to the catalogue page
        driver.get(current_url)

        # Check if there's a next page
        try:
            next_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "li.next a"))
            )
            next_button.click()
            page_num += 1
            time.sleep(2)  # Wait for the next page to load
        except (TimeoutException, NoSuchElementException):
            print("Reached the last page. Ending scraping.")
            break

    # Close the browser
    driver.quit()

    # Save data to CSV
    csv_filename = f'Selenium_Scrape.csv'
    with open(csv_filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["title", "upc", "product_type", "price_excl_tax", 
                                                  "price_incl_tax", "tax", "availability", "num_reviews"])
        writer.writeheader()
        writer.writerows(books_data)

    print(f"Scraping dengan Selenium selesai. {books_scraped} buku disimpan dalam '{csv_filename}'")

scrape_with_selenium(num_books=50)