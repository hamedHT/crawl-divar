import scrapy
import json


class DivarSpider(scrapy.Spider):
    name = 'divar'

    def start_requests(self):
        with open('./tokens.txt', 'r', encoding='utf8') as f:
            tokens = f.read().split(',')

        for token in tokens:
            url = f"https://api.divar.ir/v8/posts-v2/web/{token.strip()}"
            yield scrapy.Request(
                url=url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
                    "Referer": "https://divar.ir/",
                },
                callback=self.parse,
                meta={'token': token.strip()}
            )

    def parse(self, response):
        data = json.loads(response.text)
        token = response.meta['token']

        result = {
            'Area': None, 'Construction': None, 'Room': None,
            'Warehouse': None, 'Parking': None, 'Elevator': None,
            'Address': None, 'Total_Price': None,
            'Floor': None
        }

        for section in data.get('sections', []):
            section_name = section.get('section_name')
            widgets = section.get('widgets', [])

            if section_name == 'TITLE':
                for widget in widgets:
                    if widget.get('widget_type') == 'LEGEND_TITLE_ROW':
                        subtitle = widget['data'].get('subtitle', '')
                        if ' در ' in subtitle:
                            result['Address'] = subtitle.split(' در ')[-1].strip()

            # elif section_name == 'DESCRIPTION':
            #     for widget in widgets:
            #         if widget.get('widget_type') == 'DESCRIPTION_ROW':
            #             result['Description'] = widget['data'].get('text')

            elif section_name == 'LIST_DATA':
                for widget in widgets:
                    wtype = widget.get('widget_type')
                    wdata = widget.get('data', {})

                    if wtype == 'GROUP_INFO_ROW':
                        for item in wdata.get('items', []):
                            title = item.get('title')
                            value = item.get('value', '').replace('،', '').replace('\u200f', '').strip()
                            if title == 'متراژ':
                                result['Area'] = value
                            elif title == 'ساخت':
                                result['Construction'] = value
                            elif title == 'اتاق':
                                result['Room'] = value

                    elif wtype == 'UNEXPANDABLE_ROW':
                        title = wdata.get('title')
                        value = wdata.get('value', '').replace('،', '').replace('\u200f', '').strip()
                        if title == 'قیمت کل':
                            result['Total_Price'] = value
                        elif title == 'طبقه':
                            result['Floor'] = value

                    elif wtype == 'GROUP_FEATURE_ROW':
                        for item in wdata.get('items', []):
                            title = item.get('title', '')
                            available = item.get('available', False)
                            if 'آسانسور' in title:
                                result['Elevator'] = available
                            elif 'پارکینگ' in title:
                                result['Parking'] = available
                            elif 'انباری' in title:
                                result['Warehouse'] = 'ندارد' not in title

        yield result
