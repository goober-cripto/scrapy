# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.item import Item, Field
from orderP.items import Product
import pandas as pd
import os

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
