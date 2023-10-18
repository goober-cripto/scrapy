# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
import os
import scrapy
from scrapy.item import Item, Field
import pandas as pd

class Product(scrapy.Item):

    name = scrapy.Field()
    price = scrapy.Field()
    description = scrapy.Field()
    characteristics = scrapy.Field()

class MyPipeline:
    def __init__(self):
        self.output_file = 'piplane'
        self.checking_file()

    def checking_file(self):
        os.makedirs('data', exist_ok=True)
        # Проверяем наличие файла CSV и создаем его, если он не существует
        if not os.path.exists(os.path.join('data', f"{self.output_file}.csv")):
            df = pd.DataFrame(columns=['name', 'price', 'description', 'characteristics'])
            df.to_csv(os.path.join('data', f"{self.output_file}.csv"), index=False)
            print(f"Имя файла с данными: {self.output_file}")

    def process_item(self, item, spider):
        if isinstance(item, Product):
            # Здесь записываем элемент в файл CSV
            data = {
                'name': [item['name']],
                'price': [item['price']],
                'description': [item['description']],
                'characteristics': [item['characteristics']]
            }
            df = pd.DataFrame(data)
            df.to_csv(os.path.join('data', f"{self.output_file}.csv"), mode='a', header=False, index=False)
        return item
