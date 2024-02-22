import parser
import sql_adapter

p = parser.Parser()


def root():
    if len(p.total_els > 0):
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
    ops = p.single_threaded_parser()
    p.save_operators_json(ops)
    return {
        'totalParsed': len(ops)
    }


async def parse():
    ops = p.single_threaded_parser()
    data = await sql_adapter.create_otos(ops)
    return {
        'status': data,
        'total': len(ops)
    }