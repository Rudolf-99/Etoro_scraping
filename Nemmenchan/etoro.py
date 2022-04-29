import json
import csv
from datetime import datetime
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from scrapy import Selector

# web_link = 'https://www.etoro.com/people/jeppekirkbonde/stats'
api_link = 'https://www.etoro.com/sapi/userstats/gain/cid/2988943/history?IncludeSimulation=true&client_request_id=178db88c-d27e-4e48-9ad7-4525c1bbf9ea'
options = webdriver.ChromeOptions()
options.headless = False
# prefs = {
#     "translate_whitelists": {"ur": "en"},
#     "translate": {"enabled": "true"}
# }
# options.add_experimental_option("prefs", prefs)
driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=options)


def get_data():
    driver.get(api_link)
    response = Selector(text=driver.page_source)
    data = json.loads(response.css('pre ::text').get(''))
    driver.close()
    clean_data(data)


def clean_data(data):
    for month_dict in data.get('monthly'):
        items = dict()
        total = 0
        year = month_dict.get('start').split('-')[0]
        years = get_year_from_file()
        if year not in years:
            for months in data.get('monthly'):
                items['Year'] = year
                if year == months.get('start').split('-')[0]:
                    month = months.get('start').split('-')[1]
                    if month == '01':
                        items['Jan'] = months.get('gain')
                    if month == '02':
                        items['Feb'] = months.get('gain')
                    if month == '03':
                        items['Mar'] = months.get('gain')
                    if month == '04':
                        items['Apr'] = months.get('gain')
                    if month == '05':
                        items['May'] = months.get('gain')
                    if month == '06':
                        items['Jun'] = months.get('gain')
                    if month == '07':
                        items['Jul'] = months.get('gain')
                    if month == '08':
                        items['Aug'] = months.get('gain')
                    if month == '09':
                        items['Sep'] = months.get('gain')
                    if month == '10':
                        items['Oct'] = months.get('gain')
                    if month == '11':
                        items['Nov'] = months.get('gain')
                    if month == '12':
                        items['Dec'] = months.get('gain')
            for year_data in data.get('yearly'):
                current_year = year_data.get('start').split('-')[0]
                if year == current_year:
                    items['Total'] = year_data.get('gain')
            write_to_file(item=items)


def get_year_from_file():
    with open(file_name, 'r') as output_file:
        return [x['Year'] for x in csv.DictReader(output_file)]


def write_to_file(item, mode='a'):
    with open(file_name, mode=mode, encoding='utf-8', newline='') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',')

        if mode == 'w':
            csv_writer.writerow(
                ['Year', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Total']
            )
            print('file created as : ', file_name)
        else:
            csv_writer.writerow(
                [item.get('Year'), item.get('Jan'), item.get('Feb'), item.get('Mar'), item.get('Apr'), item.get('May'),
                 item.get('Jun'), item.get('Jul'), item.get('Aug'), item.get('Sep'), item.get('Oct'), item.get('Nov'),
                 item.get('Dec'), item.get('Total')]
            )
            print(item)


if __name__ == '__main__':
    today = 'Outputs/output_' + datetime.now().strftime("%d_%m_%Y_%H_%M_%S") + '.csv'
    file_name = today
    write_to_file(item={}, mode='w')
    get_data()
