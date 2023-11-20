from enum import Enum

class Attr(Enum):
    PRICE = 1
    RATING = 2
    DISTANCE = 3
    DRIVING = 4
    WALKING = 5
    BICYCLING = 6
    TRANSIT = 7

class Business:

    def __init__(self, json = None, id = None):
        self.id = ''
        self.name = ''
        self.image_url = ''
        self.categories = []
        self.phone = 0
        self.address = ''
        self.price = 0
        self.rating = 0
        self.url = ''
        self.distance = 0
        self.time = {'driving': 0, 'walking': 0, 'bicycling': 0, 'transit': 0}
        self.left = None
        self.right = None
        self.level_attr = None

        if 'id' in json:
            self.id = json['id']
        elif id:
            self.id = id
        if 'name' in json:
            self.name = json['name']
        if 'image_url' in json:
            self.image_url = json['image_url']
        if 'categories' in json:
            if json['categories'][0].__class__ == str:
                self.categories = json['categories']
            else:
                self.categories = [category['title'] for category in json['categories']]
        if 'phone' in json:
            if json['phone'].__class__ == int:
                self.phone = json['phone']
            else:
                if json['phone'][:5] != '+1734':
                    self.id=''
                    return
                self.phone = int(json['phone'][2:])
        if 'location' in json:
            if 'display_address' in json['location']:
                self.address = ' '.join(json['location']['display_address'])
            else:
                self.address = ' '.join(json['location'].values())
        elif 'address' in json:
            self.address = json['address']
        if 'price' in json:
            if json['price'].__class__ == int:
                self.price = json['price']
            else:
                self.price = len(json['price'])
        if 'rating' in json:
            self.rating = json['rating']   
        if 'url' in json:
            self.url = json['url']     
        if id:
            if 'distance' in json:
                self.distance = json['distance']
            if 'time' in json:
                self.time = json['time']

    def set_distance(self, distance):
        self.distance = distance
    
    def set_time(self, mode, time):
        self.time[mode] = time

    def set_left(self, left):
        self.left = left
    
    def set_right(self, right):
        self.right = right
    
    def set_level_attr(self, level_attr):
        self.level_attr = level_attr

    def get_level_attr_val(self):
        return self.get_attr_val(self.level_attr)
    
    def get_attr_val(self, attr):
        if attr == Attr.PRICE:
            return self.price
        elif attr == Attr.RATING:
            return self.rating
        elif attr == Attr.DISTANCE:
            return self.distance
        elif attr == Attr.DRIVING:
            return self.time['driving']
        elif attr == Attr.WALKING:
            return self.time['walking']
        elif attr == Attr.BICYCLING:
            return self.time['bicycling']
        elif attr == Attr.TRANSIT:
            return self.time['transit']

    def is_in_range(self, range_dict):
        for attr in range_dict:
            if self.get_attr_val(attr) < range_dict[attr][0] or self.get_attr_val(attr) > range_dict[attr][1]:
                return False
        return True

    def is_match_categories(self, prefered_categories, filter_categories, prefered_logic='or', filter_logic='or'):
        if prefered_logic == 'or':
            if not set(self.categories) & set(prefered_categories):
                return False
        elif prefered_logic == 'and':
            if not set(prefered_categories) <= set(self.categories):
                return False
        if filter_logic == 'or':
            if set(self.categories) & set(filter_categories):
                return False
        elif filter_logic == 'and':
            if set(filter_categories) & set(self.categories) == set(filter_categories):
                return False
        return True

class Tree:
    def __init__(self, root = None):
        self.root = root
    
    def insert(self, business):
        attr_idx = 1
        if not self.root:
            self.root = business
            self.root.set_level_attr(attr_idx)
            return
        position = self.root
        while position:
            if position.id == business.id:
                return
            if business.get_attr_val(position.level_attr) < position.get_attr_val(position.level_attr):
                if position.left:
                    position = position.left
                else:
                    position.left = business
                    break
            else:
                if position.right:
                    position = position.right
                else:
                    position.right = business
                    break
            attr_idx = attr_idx % 7 + 1
    
    def breadthFirstSearch(self, id=None, name=None):
        if not id and not name:
            return None
        queue = [self.root]
        while queue:
            position = queue.pop(0)
            if id and position.id == id:
                return position
            if name and position.name == name:
                return position
            if position.left:
                queue.append(position.left)
            if position.right:
                queue.append(position.right)
    
    def rangeSearch(self, range_dict, prefered_categories=None, filter_categories=None, prefered_logic='or', filter_logic='or'):
        queue = [self.root]
        result = []
        while queue:
            position = queue.pop(0)
            if position.is_in_range(range_dict) and \
                    position.is_match_categories(prefered_categories, filter_categories, prefered_logic, filter_logic):
                result.append(position)
            if position.get_attr_val(position.level_attr) >= range_dict[position.level_attr][0] \
                    and position.get_attr_val(position.level_attr) <= range_dict[position.level_attr][1]:
                if position.left:
                    queue.append(position.left)
                if position.right:
                    queue.append(position.right)
        return result