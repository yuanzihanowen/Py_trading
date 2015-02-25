__author__ = 'zihanyuanowen'

import requests
import json


def connect(domain, access_token, account_id, inst):

    try:
        s = requests.session()
        url = domain + "/v1/candles"
        # url = domain + "/v1/prices" # Get Streaming data
        param = {'accountId': account_id, 'instrument': inst}
        # param = {'accountId': account_id, 'instruments': inst}
        header = {'Authorization' : 'Bearer ' + access_token,   # 'X-Accept-Datetime-Format' : 'unix'
                  }
        req = requests.Request('GET', url, headers=header, params=param)
        prep = req.prepare()
        response = s.send(prep)
        return response
    except Exception as e:
        s.close()
        print str(e)


def read_data(r, inst_name):
    json_file = r.json()  # r is the response
    file_name = inst_name + '.txt'
    with open(file_name, "w") as outfile:
        json.dump(json_file, outfile)


def load_dict(accountid, dict_domain, token):
    s = requests.session()
    dict_domain += "/v1/instruments"
    parameter = {'accountId': accountid}
    hdr= {'Authorization' : 'Bearer ' + token}
    req = requests.Request('GET', dict_domain, headers=hdr, params=parameter)
    pre = req.prepare()
    dict_resp = s.send(pre)
    with open('dict.txt', "w") as outfile:
        json.dump(dict_resp.json(), outfile)


if __name__ == '__main__':
    dm = 'https://api-fxpractice.oanda.com'
    a_t = '9e6898d3bc4f5ef5dd0cacd8fd025b31-7dc39a42131d5dfbaa3844e0ea330914' #Access Token needed
    acct_id = '8244239'
    instrument = 'EUR_USD'
    load_dict(acct_id, dm, a_t)
    resp = connect(dm, a_t, acct_id, instrument)
    read_data(resp, instrument)
