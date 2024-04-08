async def trueReturn(data=None, status='SUCCESS'):
    return {
        "OPT_STATUS": status,
        "DATA": data,
        "DESCRIPTION": 'SUCCESS',
    }


async def falseReturn(status='FAIL', message=None, err=None, data=False):
    return {
        "OPT_STATUS": status,
        "DESCRIPTION": message,
        "DATA": data,
        "LEVEL": 0,
        "ERR": err,
    }

    # return LCJSONEncoder().encode(resp)
