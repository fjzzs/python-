import httpx
from jsonpath import jsonpath
from pprint import pprint
from fake_useragent import UserAgent

url = 'https://www.mxnzp.com/api/address/list?app_id=mqlvnqg8phisekjs&app_secret=qJFLH5jTf15oSbTn03W04tl7IJd9Hdx2'
headers = {
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': UserAgent().random
}

json_data = httpx.get(url, headers=headers, timeout=None).json()
code = jsonpath(json_data, '$..[?(@.name=="黄陂区")].code')[0]
print(code)