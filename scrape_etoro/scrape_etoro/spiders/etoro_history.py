import json
import scrapy
from time import localtime, strftime
import csv
from datetime import datetime
from dateutil.relativedelta import relativedelta


class EtoroHistorySpider(scrapy.Spider):
    name = 'etoro_history'
    today = f'output/Etoro History Records {strftime("%Y-%m-%d %H-%M-%S", localtime())}.csv'
    custom_settings = {
        'FEED_URI': today,
        'FEED_FORMAT': 'csv',
        'FEED_EXPORTERS': {'csv': 'scrapy.exporters.CsvItemExporter'},
        'CONCURRENT_REQUESTS': 1,
        'RETRY_TIMES ': 10
    }

    def __init__(self):
        super().__init__()

        self.scraper_api_link = 'http://api.scraperapi.com/?api_key=ccf0839c0af7f900333c7615bbe4a525&url={}'
        self.date = format(datetime.now() - relativedelta(years=1), '%Y-%m-%d')
        self.profiles = self.get_file_data()
        self.headers = {
            'authority': 'www.etoro.com',
            'sec-ch-ua': '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
            'accounttype': 'Real',
            'sec-ch-ua-mobile': '?0',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
            'accept': 'application/json, text/plain, */*',
            'applicationidentifier': 'ReToro',
            'applicationversion': '355.0.1',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'accept-language': 'en-US,en;q=0.9',
        }

    def start_requests(self):
        url = "https://api.etorostatic.com/sapi/instrumentsmetadata/V1.1/instruments/bulk?bulkNumber=1&totalBulks=1"
        yield scrapy.Request(url=self.scraper_api_link.format(url), callback=self.parse, headers=self.headers)

    def parse(self, response):
        response = json.loads(response.text)

        all_item_names = {}
        for item in response['InstrumentDisplayDatas']:
            all_item_names[item['InstrumentID']] = item['InstrumentDisplayName']
        for profile in self.profiles:
            url = f'https://www.etoro.com/api/logininfo/v1.1/users/{profile}'
            yield scrapy.Request(url=self.scraper_api_link.format(url), callback=self.parse_profile_id,
                                 headers=self.headers,
                                 meta={'items_name_dict': all_item_names,
                                       'Profile': profile})

    def parse_profile_id(self, response):
        profile = response.meta['Profile']
        all_item_names = response.meta['items_name_dict']
        response = json.loads(response.text)
        profile_id = response['realCID']

        url = f"https://www.etoro.com/sapi/trade-data-real/history/public/credit/flat?CID={profile_id}&ItemsPerPage=20000&PageNumber=1&StartTime={self.date}"
        yield scrapy.Request(url=self.scraper_api_link.format(url), callback=self.parse_record,
                             headers=self.headers,
                             meta={'items_name_dict': all_item_names,
                                   'Profile': profile})

    def parse_record(self, response):
        profile = response.meta['Profile']
        all_item_names = response.meta['items_name_dict']
        response = json.loads(response.text)
        for record in response['PublicHistoryPositions']:
            item = {
                'Action': 'Buy' if record['IsBuy'] else 'Sell',
                'Item': all_item_names[record['InstrumentID']],
                'Open Rate': record['OpenRate'],
                'Open Time': record['OpenDateTime'],
                'Close Rate': record['CloseRate'],
                'Close Time': record['CloseDateTime'],
                'Net Profit': record['NetProfit'],
                'Profile': profile
            }
            yield item

    def get_file_data(self):
        with open(f'input/input.csv', 'r', encoding="utf-8-sig") as input_file:
            return [x['Profiles'] for x in csv.DictReader(input_file)]
