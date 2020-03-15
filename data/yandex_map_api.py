import requests
import math


def get_map(toponym_coodrinates, corners, map_type='sat', pt=None):
    api_server = "http://static-maps.yandex.ru/1.x/"
    params = {"ll": toponym_coodrinates,
              "z": corners,
              "l": map_type,
              'size': '600,450'}
    if pt is not None:
        params['pt'] = pt
    request = requests.get(api_server, params=params)
    return request


def search(geocode):
    geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
    geocoder_params = {
        "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
        "geocode": geocode,
        "format": "json"}
    return requests.get(geocoder_api_server, params=geocoder_params)


def distance(a, b):
    degree_to_meters_factor = 111 * 1000
    a_lon, a_lat = a
    b_lon, b_lat = b
    radians_lattitude = math.radians((a_lat + b_lat) / 2.)
    lat_lon_factor = math.cos(radians_lattitude)
    dx = abs(a_lon - b_lon) * degree_to_meters_factor * lat_lon_factor
    dy = abs(a_lat - b_lat) * degree_to_meters_factor
    return math.sqrt(dx * dx + dy * dy)


def return_organization_address(address):
    search_params = {"apikey": 'dda3ddba-c9ea-4ead-9010-f43fbc15c6e3',
                     "text": address,
                     "lang": "ru_RU",
                     "type": "biz",
                     'results': '1'}
    response = requests.get("https://search-maps.yandex.ru/v1/", params=search_params)
    if not response:
        return None
    json_response = response.json()
    organization = json_response["features"][0]
    return list(map(float, organization["geometry"]["coordinates"]))