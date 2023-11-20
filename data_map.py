# key: AIzaSyBQhuzfyLd3co-CulKlI4fQjD0Lva_KICY

import requests
import json
from tree import Business

if __name__ == '__main__':
    businesses = []
    with open('cache.json', 'r') as f:
        cache = json.loads(f.read())
        for key in cache:
            businesses.append(Business(json=cache[key], id=key))

    for business in businesses:
        for mode in ['driving', 'walking', 'bicycling', 'transit']:
            if business.distance == 0 or business.time[mode] == 0:
                destination = business.address[:-10].replace(' ', '%20')
                response = requests.get('https://maps.googleapis.com/maps/api/directions/json'+
                                        '?destination='+destination+
                                        '&origin=1225%20Geddes%20Ave%20Ann%20Arbor'+
                                        '&mode='+mode+
                                        '&key=AIzaSyBQhuzfyLd3co-CulKlI4fQjD0Lva_KICY')
                try:
                    jsonData = json.loads(response.text)['routes'][0]['legs'][0]
                except:
                    print(response.text)
                    quit()
                time = jsonData['duration']['value']
                business.set_time(mode, time)
                if 'time' not in cache[business.id]:
                    cache[business.id]['time'] = {}
                cache[business.id]['time'][mode] = time
                if business.distance == 0:
                    business.set_distance(jsonData['distance']['value'])
                    cache[business.id]['distance'] = business.distance

    dumped = json.dumps(cache)
    with open('cache.json', 'w') as f:
        f.write(dumped)
