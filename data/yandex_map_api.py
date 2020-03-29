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


def get_map_source(x, y, corners):
    map_source = "http://static-maps.yandex.ru/1.x/?ll=" + ','.join([x, y]) + '&z=' + \
                 corners + '&l=map&size=600,450'
    return map_source



def search(geocode):
    geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
    geocoder_params = {
        "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
        "geocode": geocode,
        "format": "json"}
    return requests.get(geocoder_api_server, params=geocoder_params)


def map_request(name):
    map_l = 'map'
    geocoder_request = "http://geocode-maps.yandex.ru/1.x/?apikey=" \
                       "40d1649f-0493-4b70-98ba-98533de7710b&geocode=" + name + "&format=json"
    response1 = requests.get(geocoder_request)
    json_response = response1.json()
    toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
    corners = [list(map(float, i.split())) for i in toponym['boundedBy']['Envelope'].values()]
    toponym_coodrinates = str(corners[0][0] + (corners[1][0] - corners[0][0]) / 2)[:10] + ',' + str(
        corners[0][1] + (corners[1][1] - corners[0][1]) / 2)[:10]
    corners = ','.join([str((corners[1][0] - corners[0][0]))[:10],
                        str((corners[1][1] - corners[0][1]))[:10]])
    return "http://static-maps.yandex.ru/1.x/?ll=" + toponym_coodrinates + "&spn=" + \
           corners + "&l=" + map_l


def distance(a, b):
    degree_to_meters_factor = 111 * 1000
    a_lon, a_lat = a
    b_lon, b_lat = b
    radians_lattitude = math.radians((a_lat + b_lat) / 2.)
    lat_lon_factor = math.cos(radians_lattitude)
    dx = abs(a_lon - b_lon) * degree_to_meters_factor * lat_lon_factor
    dy = abs(a_lat - b_lat) * degree_to_meters_factor
    return math.sqrt(dx * dx + dy * dy)