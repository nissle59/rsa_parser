import logging
import logging.config
import sys
from itertools import cycle
import requests

logging.config.dictConfig(json.load(open('logging.json','r')))
LOGGER = logging.getLogger(__name__)

DATABASE = {
    'host': 'db.local',
    'port': 5432,
    'user': 'postgres',
    'pswd': 'psqlpass',
    'database': 'vindcgibdd'
}

tries = 5
proxies = []
r_proxies = cycle(proxies)
threads = 20
touched_at = 7

# logging.basicConfig(level=logging.DEBUG)
#
# handler = logging.FileHandler('app.log')
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# handler.setFormatter(formatter)
# s_handler = logging.StreamHandler(sys.stdout)
# logger = logging.getLogger(__name__)
# logger.addHandler(handler)
# logger.addHandler(s_handler)
# logger.setLevel(logging.DEBUG)
# logger.propagate = False
#
# bot_token = '7194357846:AAGfBntMhRcfEpoHPJ0JiVMdXN12FYQUQ4g'
# chat_id = '288772431'
# tg_sendmessage_url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
# def error(message):
#     logger.error(message)
#     requests.post(tg_sendmessage_url, data={'chat_id': chat_id, 'text': f'FINES: {message}'})
