import json
import requests
from enum import Enum
from collections import Counter
from PIL import Image
from io import BytesIO

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
        self.time = {'driving': 0, 
                     'walking': 0, 
                     'bicycling': 0, 
                     'transit': 0}
        self.left = None
        self.right = None
        self.parent = None
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
                for mode in self.time:
                    self.time[mode] = self.time[mode] / 60

    def set_distance(self, distance):
        self.distance = distance
    
    def set_time(self, mode, time):
        self.time[mode] = time

    def set_left(self, left):
        self.left = left
    
    def set_right(self, right):
        self.right = right
    
    def set_parent(self, parent):
        self.parent = parent

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
        else:
            return None

    def is_in_range(self, range_dict):
        if not range_dict:
            return True
        for attr in range_dict:
            if self.get_attr_val(attr) < range_dict[attr][0] or self.get_attr_val(attr) > range_dict[attr][1]:
                return False
        return True

    def is_match_categories(self, prefered_categories, filter_categories, prefered_logic='or', filter_logic='or'):
        if not prefered_categories and not filter_categories:
            return True
        if prefered_categories:
            if prefered_logic == 'or':
                if not set(self.categories) & set(prefered_categories):
                    return False
            elif prefered_logic == 'and':
                if not set(prefered_categories) <= set(self.categories):
                    return False
        if filter_categories:
            if filter_logic == 'or':
                if set(self.categories) & set(filter_categories):
                    return False
            elif filter_logic == 'and':
                if set(filter_categories) & set(self.categories) == set(filter_categories):
                    return False
        return True

    def get_name(self):
        return self.name
    
    def show_name_and_picture(self):
        print(self.name)
        response = requests.get(self.image_url)
        img = Image.open(BytesIO(response.content))
        img.show()
    
    def show_price_and_rating(self):
        if self.price == 0:
            price_display = '\u2606'
        else:
            price_display = '\u2605' * self.price
        print('Price: '+price_display)
        if self.rating == 0:
            rating_display = '\u2606'
        else:
            rating_display = '\u2605' * int(self.rating)
            if self.rating - int(self.rating) >= 0.5:
                rating_display += '\u2606'
        print('Rating: '+rating_display)

    def show_address_distance_time(self):
        print('Address: '+self.address)
        print('Distance: '+str(int(self.distance))+'m')
        print('Driving: '+str(int(self.time['driving']))+'min')
        print('Walking: '+str(int(self.time['walking']))+'min')
        print('Bicycling: '+str(int(self.time['bicycling']))+'min')
        print('Transit: '+str(int(self.time['transit']))+'min')

    def show_you_may_also_like(self):
        print('You may also like:')
        result = [self.left, self.right, self.parent]
        result = [business for business in result if business]
        for i, business in enumerate(result):
            print('('+str(i+1)+') '+business.get_name())
        while get_yes_no('Do you want to see more details?'):
            business = result[get_number('Enter number to see more details:', len(result))-1]
            business.run_show()

    def run_show(self):
        question = 'What do you want to see for '+self.name+'?\n' + \
            '(1) Name and Picture, (2) Price and Rating, (3) Address, Distance and Time, (4) You may also like, (5) Quit'
        number = get_number(question, 5)
        while number != 5:
            if number == 1:
                self.show_name_and_picture()
            elif number == 2:
                self.show_price_and_rating()
            elif number == 3:
                self.show_address_distance_time()
            elif number == 4:
                self.show_you_may_also_like()
                break
            number = get_number(question, 5)

class Tree:
    def __init__(self, root=None, search_max=10):
        self.root = root
        self.range_extremes = {Attr.PRICE: [None, None], Attr.RATING: [None, None], Attr.DISTANCE: [None, None],
                                Attr.DRIVING: [None, None], Attr.WALKING: [None, None], Attr.BICYCLING: [None, None], 
                                Attr.TRANSIT: [None, None]}
        self.categories = Counter()
        self.search_max = search_max
    
    def updateTree(self, business):
        for attr in self.range_extremes:
            if self.range_extremes[attr][0] == None or business.get_attr_val(attr) < self.range_extremes[attr][0]:
                self.range_extremes[attr][0] = business.get_attr_val(attr)
            if self.range_extremes[attr][1] == None or business.get_attr_val(attr) > self.range_extremes[attr][1]:
                self.range_extremes[attr][1] = business.get_attr_val(attr)
        for category in business.categories:
            self.categories.update([category])
    
    def insert(self, business):
        self.updateTree(business)
        attr_idx = Attr.PRICE
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
                    business.set_level_attr(attr_idx)
                    position.set_left(business)
                    business.set_parent(position)
                    break
            else:
                if position.right:
                    position = position.right
                else:
                    business.set_level_attr(attr_idx)
                    position.set_right(business)
                    business.set_parent(position)
                    break
            attr_idx = Attr(attr_idx.value % 7 + 1)
    
    def breadthFirstSearch(self, id=None, name=None, location=None):
        if not id and not name and not location:
            return None
        queue = [self.root]
        rst = []
        while queue:
            position = queue.pop(0)
            if id and position.id == id:
                return position
            if name and (position.name == name or name in position.name):
                rst.append(position)
            if location and (position.address == location or location in position.address):
                    rst.append(position)
            if len(rst) >= self.search_max:
                return rst
            if position.left:
                queue.append(position.left)
            if position.right:
                queue.append(position.right)
        return rst
    
    def rangeSearch(self, range_dict=None, prefered_categories=None, filter_categories=None, prefered_logic='or', filter_logic='or'):
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
            if len(result) >= self.search_max:
                break
        return result  

    def getRange(self, attr, unit=''):
        param_range = [None, None]
        for i in range(2):
            if i == 0:
                bound = 'lower'
            else:
                bound = 'upper'
            while not (isinstance(param_range[i], int) or isinstance(param_range[i], float)):
                if param_range[i]:
                    print('Invalid input, please press ENTER to skip or enter an number within given range.')
                if i == 0: 
                    print(attr.name.lower()+' range '+bound+' bound: '+str(int(self.range_extremes[attr][0]))+
                        ' - '+str(int(self.range_extremes[attr][1]))+unit)
                lower = input('Enter '+attr.name.lower()+' range '+bound+' bound (ENTER to skip):\n')
                if lower == '':
                    param_range[i] = self.range_extremes[attr][i]
                else:
                    try:
                        param_range[i] = float(lower)
                        if param_range[i] < self.range_extremes[attr][0] \
                                or param_range[i] > self.range_extremes[attr][1]:
                            param_range[i] = None
                        if i == 1 and param_range[i] < param_range[i-1]:
                            param_range[i] = None
                    except:
                        param_range[i] = None
        return param_range

    def getRangeSearchParams(self):
        range_dict = {}
        for attr in [Attr.PRICE, Attr.RATING]:
            range_dict[attr] = [None, None]
            range_dict[attr] = self.getRange(attr)
        range_dict[Attr.DISTANCE] = self.range_extremes[Attr.DISTANCE]
        range_dict[Attr.DRIVING] = self.range_extremes[Attr.DRIVING]
        range_dict[Attr.WALKING] = self.range_extremes[Attr.WALKING]
        range_dict[Attr.BICYCLING] = self.range_extremes[Attr.BICYCLING]
        range_dict[Attr.TRANSIT] = self.range_extremes[Attr.TRANSIT]
        get_distance_type = False
        distance_type = None
        while not get_distance_type:
            if distance_type:
                print('Invalid input, please press ENTER to skip or enter an integer within given range.')
            distance_type = input('Search by: (1) Distance, (2) Time, (ENTER) Skip\n')
            if distance_type == '':
                break
            elif distance_type == '1':
                get_distance_type = True
                range_dict[Attr.DISTANCE] = [None, None]
                range_dict[Attr.DISTANCE] = self.getRange(Attr.DISTANCE, 'm')
            elif distance_type == '2':
                get_distance_type = True
                get_travel_mode = False
                travel_mode = None
                while not get_travel_mode:
                    if travel_mode:
                        print('Invalid input, please enter enter an integer within given range.')
                    travel_mode = int(input('Search by: (1) Driving, (2) Walking, (3) Bicycling, (4) Transit\n'))
                    if travel_mode < 1 or travel_mode > 4:
                        travel_mode = None
                    else:
                        range_dict[Attr(travel_mode+3)] = [None, None]
                        range_dict[Attr(travel_mode+3)] = self.getRange(Attr(travel_mode+3), 'min')
                        get_travel_mode = True
        return range_dict

    def getCategories(self, type='prefered'):
        print('Identify any '+type+' categories:')
        common_categories = [category[0] for category in self.categories.most_common(15)]
        for i, category in enumerate(common_categories):
            print('('+str(i)+') '+category+',')
        get_categories = False
        categories = None
        while not get_categories:
            if categories:
                print('Invalid input, please press ENTER to skip or enter a list of integers within given range.')
            categories = input('Enter '+type+' categories, seperate with "," (ENTER to skip):\n')
            if categories == '':
                break
            else:
                try:
                    categories = [common_categories[int(category)] for category in categories.split(',')]
                    get_categories = True
                except:
                    categories = None
        logic='or'
        if categories:
            print('Identify logic for '+type+' categories:')
            logic = None
            while logic != 'and' and logic != 'or':
                if logic:
                    print('Invalid input, please enter "and" or "or".')
                logic = input('Enter logic for '+type+' categories ("and" or "or"):\n')
        return categories, logic

    def getCategoriesSearchParams(self):
        prefered_categories, prefered_logic = self.getCategories('prefered')
        filter_categories, filter_logic = self.getCategories('filter')
        return prefered_categories, filter_categories, prefered_logic, filter_logic

    def runSearch(self):
        searchType = None
        while not isinstance(searchType, int) or (searchType < 1 or searchType > 4):
            if searchType:
                print('Invalid input, please enter a number.')
            searchType = int(input('Search by: (1) ID, (2) Name, (3) Location, (4) Range & Filter\n'))
        if searchType in [1, 2, 3]:
            query = input('Enter '+['ID', 'Name', 'Location'][searchType-1]+':\n')
            if searchType == 1:
                result = self.breadthFirstSearch(id=query)
            elif searchType == 2:
                result = self.breadthFirstSearch(name=query)
            elif searchType == 3:
                result = self.breadthFirstSearch(location=query)
        elif searchType == 4:
            range_dict = self.getRangeSearchParams()
            prefered_categories, filter_categories, prefered_logic, filter_logic = self.getCategoriesSearchParams()
            result = self.rangeSearch(range_dict, prefered_categories, filter_categories, prefered_logic, filter_logic)
        if result:
            if isinstance(result, list):
                print('Found '+str(len(result))+' results:')
                for i, business in enumerate(result):
                    print('('+str(i+1)+') '+business.get_name())
                while get_yes_no('Do you want to see more details?'):
                    business = result[get_number('Enter number to see more details:', len(result))-1]
                    business.run_show()
                    for i, business in enumerate(result):
                        print('('+str(i+1)+') '+business.get_name())
            else:
                print('Found result:')
                print(result.get_name())
                if get_yes_no('Do you want to see more details?'):
                    result.run_show()
        else:
            print('No result found.') 

def get_number(question, upper_bound):
    number = None
    while not isinstance(number, int) or number < 1 or number > upper_bound:
        if number:
            print('Invalid input, please enter an integer between 1 and '+str(upper_bound)+'.')
        number = input(question+'\n')
        try:
            number = int(number)
        except:
            number = None
    return number

def get_yes_no(question):
    answer = None
    while answer != 'y' and answer != 'n':
        if answer:
            print('Invalid input, please enter y or n.')
        answer = input(question+' (y/n)\n')
    return answer == 'y'

if __name__ == '__main__':
    tree = Tree()
    with open('cache.json', 'r') as f:
        cache = json.loads(f.read())
        for key in cache:
            tree.insert(Business(json=cache[key], id=key))
    cont = True
    while cont:
        tree.runSearch()
        cont = get_yes_no('Do you want to continue?')
