# Client ID: rDl9M3sVUUrhMFQlGaK4qA

import requests
import json
from tree import Business

if __name__ == '__main__':
    searches = ['Ann%20Arbor%20Downtown', 'University%20of%20Michigan', 'Ann%20Arbor%20Parks%20Area', 'Ann%20Arbor%20Northside', 
                'Ann%Arbor%20Westside', 'Ann%20Arbor%20Southside', 'Ann%20Arbor%20Old%20West%20Side', 'Sosltice%20Neighborhood', 
                'Ann%20Arbor%20Northeast%20Side', 'Ann%20Arbor%20Burns%20Park']#, 'Ann%20Arbor%Westwood', 'Ann%20Arbor%20Pittsfield%20Village','']
    businesses = []
    cache = {}
    for search in searches:
        url = "https://api.yelp.com/v3/businesses/search?location="+search+"&sort_by=best_match&limit=50"
        headers = {"accept": "application/json",
                "Authorization": "Bearer Ko8Y3LTAND_Qy4iqIBWCC_0bh1AZh7S91IAoBzuzD8Nk7__jQKNNvtwT_7l-N5saOQr9y9i1_ekZdZmc-LgP_LMoDMZDz_9EHnXDP6CF1V2tVsidGqaU3Dg0CYpZZXYx"}
        response = requests.get(url, headers=headers)
        businessData = json.loads(response.text)
        try:
            businesses = [Business(business) for business in businessData['businesses']]
        except:
            print(businessData)
            print(search)
            continue
        businesses_temp = [business for business in businesses if business.id != '']
        businesses.extend(businesses_temp)

        for b in businesses_temp:
            cache[b.id] = {'name': b.name, 'image_url': b.image_url, 'categories': b.categories, 'phone': b.phone, 
                        'address': b.address, 'price': b.price, 'rating': b.rating, 'url': b.url}
        if len(cache) > 100:
            print('reach 100')
            break
        
    dumped = json.dumps(cache)
    with open('cache.json', 'w') as f:
        f.write(dumped)
