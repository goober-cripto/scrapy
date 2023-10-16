import os
import random
import string
import atexit
import requests
import pandas as pd

from scrapy.http import  HtmlResponse
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

class GetProductSpider(CrawlSpider):
    name = "getProduct"
    allowed_domains = ["order-nn.ru"]
    start_urls = ["https://order-nn.ru/kmo/catalog/"]
    ajax_url = "https://order-nn.ru/local/ajax/kmo/getCharacterItems.php"

    rules = (
        Rule(LinkExtractor(allow=('5974','5966', '9460')), callback='parse_item',follow=True),
    )

    def __init__(self, **kwargs):
        self.df = pd.DataFrame(columns=['name', 'price', 'description', 'characteristics'])
        atexit.register(self.close_driver)
        super(GetProductSpider, self).__init__(**kwargs)

    def parse_item(self, response):
        response._url += '?count=60'
        product_links = response.xpath('//a[@itemprop="url"]/@href').getall()
        for link in product_links:
            yield response.follow(link, callback=self.parse_product_details)

        next_page = response.css('a[rel="canonical"] i.fa-angle-right').xpath('parent::a/@href').extract_first()
        if next_page:
            yield response.follow(next_page, callback=self.parse_item)

    def parse_product_details(self, response):
        name = response.xpath('//div[@class="block-1"]/div[@class="block-1-0"]/h1[@itemprop="name"]/text()').get()
        price = response.xpath('//div[@class="block-3-row element-current-price"]//span/text()').getall() or "Нет в наличии"
        description = response.xpath('//div[@id="block-description"]//text()').getall()
        cleaned_description = ' '.join(desc.strip() for desc in description if desc.strip())

        items = response._url.split('/')[-1]
        data = {
            'type': 'character',
            'style': 'element',
            'items': items
        }
        # используем Reqests чтобы обойти правило robot.txt
        req = requests.post(self.ajax_url, data=data)
        if req.status_code == 200:
            characteristics = {} 
            res = HtmlResponse(url=response._url,body=req.text, encoding='utf-8')
            for characteristic_row in res.xpath('//table//tr'):
                key = characteristic_row.xpath('.//td[@class="table-character-text"]/text()').get()
                value = characteristic_row.xpath('.//td[@class="table-character-value"]/text()').get()
                # очистка текста
                if key and value:
                    characteristics[key.strip()] = value.strip()

            self.df = self.df._append({'name': name, 'price': price,
                                    'description': cleaned_description, 'characteristics': characteristics},
                                    ignore_index=True)
        else:
            # Если запрос был неудачным, вы можете обработать ошибку
            print(f"Ошибка при выполнении запроса: {req.status_code}")


    def close_driver(self):
        # Генерируем случайное имя файла
        random_filename = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(8)) + ".csv"
        # Создаем папку 'data', если она не существует
        if not os.path.exists('data'):
            os.makedirs('data')
        # Сохраняем DataFrame в файл
        self.df.to_csv(os.path.join('data', random_filename), index=False)
        print(f"Имя файла с данными =============> {random_filename}")
