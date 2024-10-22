import random
import requests
import json

### https://js.datadome.co/tags.js << find ddk here ###
def cookie_gen(domain, ddk):
    # Generate random x-forwarded-for IP
    x_forwarded_for = f"{random.randint(10, 99)}.{random.randint(10, 99)}.{random.randint(10, 99)}"

    # Create headers
    headers = {
        'x-forwarded-for': x_forwarded_for,
        'Content-type': 'application/x-www-form-urlencoded',
        'Host': 'api-js.datadome.co',
        'Origin': domain,
        'Referer': domain,
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
    }

    # Create body parameters
    body_data = {
        'ddv': '4.6.0',
        'eventCounters': [],
        'jsType': 'ch',
        'ddk': ddk,
        'events': [],
        'request': '%2F',
        'responsePage': 'origin',
        'cid': 'null',
        'dddomain': domain,
        'Referer': '',
        'jsData': json.dumps({
            "ttst": f"{random.randint(10, 99)}.{random.randint(1000000000000, 9999999999999)}",
            "ifov": False,
            "tagpu": f"{random.randint(10, 99)}.{random.randint(1000000000000, 9999999999999)}",
            "glvd": "Google Inc. (NVIDIA)",
            "glrd": "ANGLE (NVIDIA, NVIDIA GeForce GTX 1660 SUPER Direct3D11 vs_5_0 ps_5_0, D3D11)",
            "hc": 16,
            "br_oh": 1040,
            "br_ow": 1920,
            "ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
            "wbd": False,
            "wdif": False,
            "wdifrm": False,
            "npmtm": False,
            "br_h": 969,
            "br_w": 963,
            "nddc": 1,
            "rs_h": 1080,
            "rs_w": 1920,
            "rs_cd": 24,
            "phe": False,
            "nm": False,
            "jsf": False,
            "lg": "en-US",
            "pr": 1,
            "ars_h": 1040,
            "ars_w": 1920,
            "tz": 480,
            "str_ss": True,
            "str_ls": True,
            "str_idb": True,
            "str_odb": True,
            "plgod": False,
            "plg": random.randint(5, 14),
            "plgne": True,
            "plgre": True,
            "plgof": False,
            "plggt": False,
            "pltod": False,
            "hcovdr": False,
            "hcovdr2": False,
            "plovdr": False,
            "plovdr2": False,
            "ftsovdr": False,
            "ftsovdr2": False,
            "lb": False,
            "eva": 33,
            "lo": False,
            "ts_mtp": 0,
            "ts_tec": False,
            "ts_tsa": False,
            "vnd": "Google Inc.",
            "bid": "NA",
            "mmt": "application/pdf,text/pdf",
            "plu": "PDF Viewer,Chrome PDF Viewer,Chromium PDF Viewer,Microsoft Edge PDF Viewer,WebKit built-in PDF",
            "hdn": False,
            "awe": False,
            "geb": False,
            "dat": False,
            "med": "defined",
            "aco": "probably",
            "acots": False,
            "acmp": "probably",
            "acmpts": True,
            "acw": "probably",
            "acwts": False,
            "acma": "maybe",
            "acmats": False,
            "acaa": "probably",
            "acaats": True,
            "ac3": "",
            "ac3ts": False,
            "acf": "probably",
            "acfts": False,
            "acmp4": "maybe",
            "acmp4ts": False,
            "acmp3": "probably",
            "acmp3ts": False,
            "acwm": "maybe",
            "acwmts": False,
            "ocpt": False,
            "vco": "probably",
            "vcots": False,
            "vch": "probably",
            "vchts": True,
            "vcw": "probably",
            "vcwts": True,
            "vc3": "maybe",
            "vc3ts": False,
            "vcmp": "",
            "vcmpts": False,
            "vcq": "",
            "vcqts": False,
            "vc1": "probably",
            "vc1ts": True,
            "dvm": 8,
            "sqt": False,
            "so": "landscape-primary",
            "wdw": True,
            "cokys": "bG9hZFRpbWVzY3NpYXBwL=",
            "ecpc": False,
            "lgs": True,
            "lgsod": False,
            "psn": True,
            "edp": True,
            "addt": True,
            "wsdc": True,
            "ccsr": True,
            "nuad": True,
            "bcda": False,
            "idn": True,
            "capi": False,
            "svde": False,
            "vpbq": True,
            "ucdv": False,
            "spwn": False,
            "emt": False,
            "bfr": False,
            "dbov": False,
            "prm": True,
            "tzp": "America/Los_Angeles",
            "cvs": True,
            "usb": "defined",
            "jset": random.randint(1000000000, 9999999999)
        })
    }

    # Make the request
    response = requests.post('https://api-js.datadome.co/js/', headers=headers, data=body_data)

    # Process response
    res_data = response.text
    cookie = res_data[24:-2]  # Extract cookie
    return {
        'raw': cookie,
        'cookie': cookie.split(';')[0],
        'value': cookie.split(';')[0].split('=')[1],
    }
