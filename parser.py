import json
import warnings

import requests
from bs4 import BeautifulSoup

warnings.filterwarnings("ignore")
class Parser():
    def __init__(self, proxy=None):
        self._base_url ='https://oto-register.autoins.ru'
        self.page_url = f'{self._base_url}/tables/oto/?pageNumber='
        first_page = requests.get(
            self.page_url+'1',
            verify=False,
            proxies=proxy
        )
        soup = BeautifulSoup(
            first_page.text,
            features="html.parser"
        )
        self.total_pages_ok = int(soup.select('.page-link')[-2:][0].text.strip(),0)
        self.total_els_ok = int(soup.select_one('.totalElements>strong').text.strip(),0)
        first_page = requests.get(
            'https://oto-register.autoins.ru/search/oto/1?otoId=&shortName=&address=&fio=&showCanceled=true',
            verify=False,
            proxies=proxy
        )
        soup = BeautifulSoup(
            first_page.text,
            features="html.parser"
        )
        self.total_pages_bad = int(soup.select('.page-link')[-2:][0].text.strip())
        self.total_els_bad = int(soup.select_one('.totalElements>strong').text.strip(), 0)
        self.total_pages = self.total_pages_ok + self.total_pages_bad
        self.total_els = self.total_els_ok + self.total_els_bad

    def save_operators_json(self, operators, fname='operators.json'):
        with open(fname, 'w', encoding='utf-8') as f:
            f.write(json.dumps(operators, ensure_ascii=False, indent=2))

    def load_operators_json(self, fname='operators.json'):
        with open(fname, 'r', encoding='utf-8') as f:
            operators = json.loads(f.read())
            return operators

    def parse_page(self, url, proxy=None):
        html = requests.get(url, verify=False, proxies=proxy)
        soup = BeautifulSoup(html.text, features="html.parser")
        table = soup.select('.table>tbody>tr')
        arr = []
        for tr in table:
            tds = tr.select('td')
            operator_status = list(tds[0].select_one('div').attrs['class']).pop(1)
            operator_number = tds[1].text.strip()
            operator_name = tds[2].text.strip()
            operator_address = tds[3].text.strip()
            operator_phone = tds[4].text.strip()
            operator_email = tds[5].text.strip()
            operator_site = tds[6].text.strip().strip('/')
            arr.append({
                'operator_number': operator_number,
                'operator_status': operator_status,
                'operator_name': operator_name,
                'operator_address': operator_address,
                'operator_phone': operator_phone,
                'operator_email': operator_email,
                'operator_site': operator_site
            })
        return arr

    def single_threaded_parser(self, proxy=None):
        operators = []
        for page in range(self.total_pages_ok):
            print(f'Go {page+1} of {self.total_pages_ok} ok page...')
            url = f'{self._base_url}/tables/oto/?pageNumber={page+1}'
            operators.extend(self.parse_page(url,proxy))

        for page in range(self.total_pages_bad):
            print(f'Go {page+1} of {self.total_pages_bad} bad page...')
            url = f'{self._base_url}/search/oto/{page+1}?otoId=&shortName=&address=&fio=&showCanceled=true'
            operators.extend(self.parse_page(url, proxy))

        return operators


if __name__ == '__main__':
    p = Parser()
    print(f'Total pages:\n  OK: {p.total_pages_ok}\n  Bad: {p.total_pages_bad}\n  Full: {p.total_pages_ok+p.total_pages_bad}')
    #ops = p.single_threaded_parser()
    ops = p.load_operators_json()
    print(f'Total ops: {len(ops)}')