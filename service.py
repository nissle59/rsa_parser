import parser
import sql_adapter
import logging

p = parser.Parser()


def root():
    LOGGER = logging.getLogger(__name__ + ".root")
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
    LOGGER = logging.getLogger(__name__ + ".parse_to_local")
    ops = p.single_threaded_parser()
    p.save_operators_json(ops)
    return {
        'totalParsed': len(ops)
    }


async def parse():
    LOGGER = logging.getLogger(__name__ + ".parse")
    ops = p.single_threaded_parser()
    data = await sql_adapter.create_otos(ops)
    LOGGER.info(f"Parsed {len(ops)}, Status: SUCCESS")
    return {
        'status': data,
        'total': len(ops)
    }