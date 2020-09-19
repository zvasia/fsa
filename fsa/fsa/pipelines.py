# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

FIELDS_CSV = {
    'id', 'nameStatus', 'regNumber', 'applicantInn', 'applicantFullName', 'nameType', 'fullName',
    'address', 'nameTypeActivity', 'oaDescription', 'gu1', 'extend'
}
filename = 'result.csv'


class FsaPipeline:
    def process_item(self, item, spider):
        return item
