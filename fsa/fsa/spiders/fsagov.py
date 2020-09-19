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

    FIELDS = (
        'id',
        'nameStatus',
        'regNumber',
        'applicantInn',
        'applicantFullName',
        'nameType',
        'fullName',
        'address',
        # НЧЕР
        'nameTypeActivity',
        'oaDescription'
    )

    DETAIL_FIELDS = (

    )

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer eyJhbGciOiJIUzUxMiJ9.eyJpc3MiOiIwOWY0Y2E0ZC0zNjFjLTRiZTUtOTgxMS1jYzU4Yzk5YTc1NzYiLCJzdWIiOiJhbm9ueW1vdXMiLCJleHAiOjE2MDEzODA3OTl9.CN962eiNK3GyYV6MmPSKNLS_5ZjYCheLFxz1CGfMJs6S61MkMDjXbg-mmCtaq5pDC6WaMDK8z0wG3OXuWmj1XQ',
        'Cookie': 'JSESSIONID=node01b89b3pga2h0y1krxg0f5mth3o33672.node0'
    }

    def start_requests(self):
        url = "https://pub.fsa.gov.ru/api/v1/ral/common/showcases/get"
        page = 0
        limit = 100

        payload = {
            "columns": [
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
        r_json = json.loads(response.text.encode('utf8'))
        total = r_json['total']
        total_pages = ceil(total / limit)

        for page in range(0, total_pages):
            new_payload = {
                "columns": [
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
                'Authorization': 'Bearer eyJhbGciOiJIUzUxMiJ9.eyJpc3MiOiIwOWY0Y2E0ZC0zNjFjLTRiZTUtOTgxMS1jYzU4Yzk5YTc1NzYiLCJzdWIiOiJhbm9ueW1vdXMiLCJleHAiOjE2MDEzODA3OTl9.CN962eiNK3GyYV6MmPSKNLS_5ZjYCheLFxz1CGfMJs6S61MkMDjXbg-mmCtaq5pDC6WaMDK8z0wG3OXuWmj1XQ',
                'Cookie': 'JSESSIONID=node01b89b3pga2h0y1krxg0f5mth3o33672.node0',
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

        # gu_one.update(decisionNumber)
        # gu_two =
        # gu_three =
        # item['gu_three'] = gu_three
        # print(item)
        yield item
