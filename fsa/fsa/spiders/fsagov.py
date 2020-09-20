from math import ceil

import requests
import scrapy
import json

from scrapy import Request

from fsa.items import FsaItem


class FsagovSpider(scrapy.Spider):
    name = 'fsagov'
    allowed_domains = ['pub.fsa.gov.ru']
    detail_url = "https://pub.fsa.gov.ru/api/v1/ral/common/companies/{id}"
    TOKEN = 'Bearer xxxxxxx'
    COOKIE = 'JSESSIONID=xxxxx.node0'

    FIELDS = (
        'id',
        'nameStatus',
        'regNumber',
        'applicantInn',
        'applicantFullName',
        'nameType',
        'fullName',
        'address',
        'nameTypeActivity',
        'oaDescription'
    )

    headers = {
        'Content-Type': 'application/json',
        'Authorization': TOKEN,
        'Cookie': COOKIE
    }

    def start_requests(self):
        url = "https://pub.fsa.gov.ru/api/v1/ral/common/showcases/get"
        page = 0
        limit = 100

        payload = {
            "columns": [
                {"name": "nameType",
                 "search": "ИЛ",
                 "type": 0},
                {"name": "oaDescription",
                 "search": "лифт",
                 "type": 0
                 }
            ],
            "sort": ["-id"],
            "limit": limit,
            "offset": page
        }

        response = requests.request("POST", url,
                                    headers=self.headers,
                                    data=json.dumps(payload),
                                    verify=False
                                    )
        r_json = json.loads(response.text)
        total = r_json['total']
        total_pages = ceil(total / limit)

        for page in range(0, total_pages):
            new_payload = {
                "columns": [
                    {"name": "nameType",
                     "search": "ИЛ",
                     "type": 0},
                    {"name": "oaDescription",
                     "search": "лифт",
                     "type": 0
                     }
                ],
                "sort": ["-id"],
                "limit": limit,
                "offset": page
            }
            print(new_payload)
            print(f'Page: {page}')
            yield Request(url, callback=self.parse,
                          method='POST',
                          headers=self.headers,
                          body=json.dumps(new_payload))

    def parse(self, response):
        data = json.loads(response.text)
        for row in data['items']:
            item = FsaItem()
            for field in self.FIELDS:
                if field in row:
                    item[field] = row[field]

            headers = {
                'Content-Type': 'application/json',
                'Authorization': self.TOKEN,
                'Cookie': self.COOKIE,
                'Referer': f'https://pub.fsa.gov.ru/ral/view/{item["id"]}/state-services'
            }

            yield Request(self.detail_url.format(id=item['id']), callback=self.parse_detail,
                          method='GET', headers=headers, meta={'item': item})

    def parse_detail(self, response):
        data = json.loads(response.text)
        item = response.meta['item']
        gu = data['confirmCompetenceChanges']
        extend = data['extendAccredScopeChanges']
        gu_list = []
        item['extend'] = []
        for row in gu:
            arr = []
            try:
                arr.append(
                    f'Номер решения о прохождении процедуры подтверждения компетентности: {row["decisionNumber"]}')
                arr.append(f'Дата решения о прохождении процедуры подтверждения компетентности: {row["decisionDate"]}')
                arr.append(f'ФИО эксперта по аккредитации: {row["expertGroup"]["expertFio"]}')
                arr.append(
                    f"Регистрационный номер записи в реестре экспертов по аккредитации: {row['expertGroup']['expertRegNumber']}")
                arr.append(f"Экспертная организация: {row['expertGroup']['expertOrganizationName']}")
            except:
                print('Not full GU in JSON')
            finally:
                gu_list.append(arr)
        try:
            item['one'] = gu_list[0]
            item['two'] = gu_list[1]
        except:
            pass
        for row in extend:
            arr = []
            try:
                arr.append(f'Номер решения о расширении области аккредитации: {row["decisionNumber"]}')
                arr.append(f'Дата решения о расширении области аккредитации: {row["decisionDate"]}')
                arr.append(
                    f'Описание области аккредитации: {row["accredScopeUnstructList"]["accredScopeUnstruct"][0]["oaDescription"]}')
                # arr.append(f"Технический регламент ЕАЭС: {row['expertGroup']['expertRegNumber']}")
                arr.append(f"Коды ТН ВЭД: {row['accredScopeUnstructList']['accredScopeUnstruct'][0]['codeTnVed']}")
                arr.append(f"Коды ОКП: {row['accredScopeUnstruct']['accredScopeUnstruct'][0]['codeOkp']}")
            except:
                print('Not full GU in JSON')
            finally:
                item['extend'] = arr
        yield item
