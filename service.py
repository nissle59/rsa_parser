import parser
import sql_adapter
import logging
from config import cf
p = parser.Parser()


def root():
    LOGGER = logging.getLogger(__name__ + "." + cf()['name'])
    if p.total_els > 0:
        rem_status = 'OK'
        d = {
            'remoteSrcStatus': rem_status,
            'total': p.total_els
        }
    else:
        rem_status = 'UNAVAILIABLE'
        d = {
            'remoteSrcStatus': rem_status
        }
    return d


def parse_to_local():
    LOGGER = logging.getLogger(__name__ + "." + cf()['name'])
    ops = p.single_threaded_parser()
    p.save_operators_json(ops)
    return {
        'totalParsed': len(ops)
    }


async def parse():
    LOGGER = logging.getLogger(__name__ + "." + cf()['name'])
    ops = p.single_threaded_parser()
    data = await sql_adapter.create_otos(ops)
    LOGGER.info(f"Parsed {len(ops)}, Status: SUCCESS")
    return {
        'status': data,
        'total': len(ops)
    }

if __name__ == "__main__":
    parse_to_local()