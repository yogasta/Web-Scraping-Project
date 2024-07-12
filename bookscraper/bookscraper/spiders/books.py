import scrapy
from scrapy.exceptions import CloseSpider

class BooksSpider(scrapy.Spider):
    name = 'books'
    allowed_domains = ['books.toscrape.com']
    
    def __init__(self, start_page=1, num_books=None, *args, **kwargs):
        super(BooksSpider, self).__init__(*args, **kwargs)
        self.start_page = int(start_page)
        self.num_books = int(num_books) if num_books else None
        self.books_scraped = 0
        self.start_urls = [f'http://books.toscrape.com/catalogue/page-{self.start_page}.html']

    def parse(self, response):
        books = response.css('article.product_pod')
        
        for book in books:
            if self.num_books and self.books_scraped >= self.num_books:
                raise CloseSpider(f'Reached the desired number of books: {self.num_books}')
            
            book_url = book.css('h3 a::attr(href)').get()
            yield response.follow(book_url, callback=self.parse_book)

        next_page = response.css('li.next a::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response):
        self.books_scraped += 1
        table_rows = response.css('table.table-striped tr')
        
        yield {
            'title': response.css('h1::text').get(),
            'upc': table_rows[0].css('td::text').get(),
            'product_type': table_rows[1].css('td::text').get(),
            'price_excl_tax': table_rows[2].css('td::text').get(),
            'price_incl_tax': table_rows[3].css('td::text').get(),
            'tax': table_rows[4].css('td::text').get(),
            'availability': table_rows[5].css('td::text').get().strip(),
            'num_reviews': table_rows[6].css('td::text').get()
        }
    
# To run this spider, use:
# scrapy crawl books -a start_page=1 -a num_books=50 -o books_scrapy.csv
# High chance of overshooting the targeted amount of books due to scrapy being asynchronous.
