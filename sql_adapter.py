import datetime
import re
import config
from database import AsyncDatabase


def del_tz(dt: datetime.datetime):
    dt = dt.replace(tzinfo=None)
    return dt


def convert_to_ts(s: str):
    dt = datetime.datetime.strptime(s, '%Y-%m-%d')
    dt = del_tz(dt)
    # dt = s
    return dt


camel_pat = re.compile(r'([A-Z])')
under_pat = re.compile(r'_([a-z])')


def get_insert_query():
    query = f"""
                INSERT INTO 
                    oto 
                VALUES (
                    $1::int4,
                    $2,
                    $3,
                    $4,
                    $5,
                    $6,
                    $7,
                    $8::timestamp,
                    $9::timestamp
                ) ON CONFLICT (operator_number) DO 
                UPDATE SET 
                    operator_status=$2, 
                    operator_name=$3, 
                    operator_address=$4, 
                    operator_phone=$5,
                    operator_email=$6,
                    operator_site=$7,
                    touched_at=$8::timestamp
            """
    return query


def set_items_tuple_create_oto_record(d, multi=False):
    nowdt = del_tz(datetime.datetime.now())
    if d['operator_status'] == 'ok':
        d['cancel_at'] = None
    elif d['operator_status'] == 'cancel':
        d['cancel_at'] = nowdt
    else:
        d['cancel_at'] = None
    if multi is True:
        items_tuple = (
            int(d['operator_number']),
            d['operator_status'],
            d['operator_name'],
            d['operator_address'],
            d['operator_phone'],
            d['operator_email'],
            d['operator_site'],
            nowdt,
            d['cancel_at']
        )
    else:
        items_tuple = [
            int(d['operator_number']),
            d['operator_status'],
            d['operator_name'],
            d['operator_address'],
            d['operator_phone'],
            d['operator_email'],
            d['operator_site'],
            nowdt,
            d['cancel_at']
        ]
    return items_tuple


def camel_to_underscore(name):
    return camel_pat.sub(lambda x: '_' + x.group(1).lower(), name)


def underscore_to_camel(name):
    return under_pat.sub(lambda x: x.group(1).upper(), name)


conf = config.DATABASE


def list_detector(input):
    new_data = {}
    if isinstance(input, list):
        data = [dict(record) for record in input][0]
    else:
        data = dict(input)
    for key, value in data.items():
        new_data[underscore_to_camel(key)] = data.get(key)
    return new_data


def list_detector_to_list(input):
    if isinstance(input, list):
        new_data = []
        # data = [dict(record) for record in input]
        for record in input:
            new_d = {}
            record = dict(record)
            for key, value in record.items():
                new_d[underscore_to_camel(key)] = record.get(key)
            new_data.append(new_d)
    else:
        new_data = {}
        data = dict(input)
        for key, value in data.items():
            new_data[underscore_to_camel(key)] = data.get(key)
    return new_data


async def get_setting(setting_name: str):
    query = f"SELECT value FROM settings WHERE setting_name = '{setting_name}'"

    async with AsyncDatabase(**conf) as db:
        data = await db.fetch(query)

    if data is None:
        return {}

    data = list_detector(data)

    return data[setting_name]


async def get_active_proxies(proxy_type: str):
    if proxy_type == "HTTPS":
        t_name = 'https_active_proxies'
    elif proxy_type == 'SOCKS5':
        t_name = 'socks_active_proxies'
    else:
        t_name = 'active_proxies'

    query = f"SELECT * FROM {t_name}"
    async with AsyncDatabase(**conf) as db:
        data = await db.fetch(query)

    if data is None:
        return []

    data = list_detector_to_list(data)

    return data


async def find_oto(oto_num):
    query = f"SELECT * FROM oto WHERE operator_number = '{oto_num}'"

    async with AsyncDatabase(**conf) as db:
        data = await db.fetch(query)

    if data is None:
        return {}

    data = list_detector(data)

    return data


async def scan_otos_to_update():
    touched_at = config.touched_at
    query = f"""select 
                    operator_number, 
                    touched_at 
                from 
                    oto 
                where 
                    oto.operator_name is null 
                    or (now()-touched_at) >= '{touched_at} days'
            """

    async with AsyncDatabase(**conf) as db:
        data = await db.fetch(query)

    if data is None:
        return []
    # config.logger.info(data)
    data = [{'vin': item['vin'], 'createdAt': item['createdAt']} for item in list_detector_to_list(data)]
    config.logger.info(data)
    return data


async def create_oto(d):
    config.logger.debug(f'{d["operator_name"]} SQL Insert...')
    items_tuple = set_items_tuple_create_oto_record(d, multi=False)
    query = get_insert_query()
    async with AsyncDatabase(**conf) as db:
        data = await db.execute(query, items_tuple)
        return data


async def create_otos(l):
    async with AsyncDatabase(**conf) as db:
        items_arr = []
        for d in l:
            items_tuple = set_items_tuple_create_oto_record(d, multi=True)
            items_arr.append(items_tuple)
        query = get_insert_query()
        data = await db.executemany(query, items_arr)
        query = 'SELECT * FROM oto'
        data = await db.fetch(query)
        items = []
        for item in data:
            nowdt = del_tz(datetime.datetime.now())
            d = {
                'operator_number': item['operator_number'],
                'operator_status': item['operator_status'],
                'cancel_at': item['cancel_at']
            }
            if d['operator_status'] == 'cancel':
                if d['cancel_at'] is None:
                    d['cancel_at'] = nowdt
            else:
                d['cancel_at'] = None
            items.append((d['cancel_at'], item['operator_number']))
        query = 'UPDATE oto SET cancel_at = $1::timestamp where operator_number = $2::int4'
        data = await db.executemany(query, items)
        if data is not None:
            return True
        else:
            return None


async def update_canceled_otos():
    query = 'SELECT * FROM oto'
    async with AsyncDatabase(**conf) as db:
        data = await db.fetch(query)

    if data is None:
        return []
    items = []
    for item in data:
        nowdt = del_tz(datetime.datetime.now())
        d = {
            'operator_number': item['operator_number'],
            'operator_status': item['operator_status'],
            'cancel_at': item['cancel_at']
        }
        if d['operator_status'] == 'cancel':
            if d['cancel_at'] is None:
                d['cancel_at'] = nowdt
        else:
            d['cancel_at'] = None
        items.append((d['cancel_at'], item['operator_number']))
    query = 'UPDATE oto SET cancel_at = $1::timestamp where operator_number = $2::int4'
    async with AsyncDatabase(**conf) as db:
        data = await db.executemany(query, items)
        if data is not None:
            return True
        else:
            return None