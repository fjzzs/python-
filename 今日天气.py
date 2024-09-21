import httpx
from pprint import pprint
from jsonpath_ng import parse
from fake_useragent import UserAgent

city_name = '黄陂区'
search_api = f'https://www.mxnzp.com/api/weather/current/{city_name}?app_id=mqlvnqg8phisekjs&app_secret=qJFLH5jTf15oSbTn03W04tl7IJd9Hdx2'
headers = {
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': UserAgent().random
}

response = httpx.get(url=search_api, headers=headers, timeout=None)
response.raise_for_status()
json_data = response.json()
address = json_data['data']['address']
citycode = json_data['data']['cityCode']
humidity = json_data['data']['humidity']
reportTime = json_data['data']['reportTime']
temp = json_data['data']['temp']
weather = json_data['data']['weather']
windDirection = json_data['data']['windDirection']
print(address, citycode, humidity, reportTime, temp, weather, windDirection)

