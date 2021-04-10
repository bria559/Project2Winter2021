#################################
##### Name: Briana Whyte
##### Uniqname: brianawh
#################################

from bs4 import BeautifulSoup
import requests
import json
import api_secrets # file that contains your API key

api_key = api_secrets.API_KEY
CACHE_FILENAME = "nps_cache.json"
CACHE_DICT = {}

base_url = "https://www.nps.gov"
response = requests.get(base_url)
soup = BeautifulSoup(response.text, 'html.parser')
#print(soup.prettify())

class NationalSite:
    '''a national site

    Instance Attributes
    -------------------
    category: string
        the category of a national site (e.g. 'National Park', '')
        some sites have blank category.
    
    name: string
        the name of a national site (e.g. 'Isle Royale')

    address: string
        the city and state of a national site (e.g. 'Houghton, MI')

    zipcode: string
        the zip-code of a national site (e.g. '49931', '82190-0168')

    phone: string
        the phone of a national site (e.g. '(616) 319-7906', '307-344-7381')
    '''
    def __init__(self, category, name, address, zipcode, phone):
        self.category = category
        self.name = name
        self.address = address
        self.zipcode = zipcode
        self.phone = phone

    def info(self):
        '''
        Returns
        -------
        An instance of itself
        '''

        return f"{self.name} ({self.category}): {self.address} {self.zipcode}"



def build_state_url_dict():
    ''' Make a dictionary that maps state name to state page url from "https://www.nps.gov"

    Parameters
    ----------
    None

    Returns
    -------
    dict
        key is a state name and value is the url
        e.g. {'michigan':'https://www.nps.gov/state/mi/index.htm', ...}
    '''
    state_name_url = {}
    all_state_elements = soup.find(class_="dropdown-menu SearchBar-keywordSearch")
    #print(all_state_elements)
    
    state_listing = all_state_elements.find_all('li', recursive=False)
    #print(state_listing)
    '''
    <li><a href="/state/al/index.htm">Alabama</a></li>
    '''

    for state_list in state_listing:
        name_tag = state_list.find('a').contents[0]
        name_tag = name_tag.lower()
        state_tag = state_list.find('a')
        url_path = state_tag['href']
        state_url = base_url + url_path
        state_name_url[name_tag] = state_url
    
    return state_name_url


def get_site_instance(site_url):
    '''Make an instances from a national site URL.
    
    Parameters
    ----------
    site_url: string
        The URL for a national site page in nps.gov

    Returns
    -------
    instance
        a national site instance
    '''
    response = requests.get(site_url)
    soupDetail = BeautifulSoup(response.text, 'html.parser' )
    all_park_elements = soupDetail.find(class_='Hero-titleContainer clearfix')
    # print(all_park_elements)

    name = all_park_elements.find(class_='Hero-title').text

    category_site = all_park_elements.find(class_='Hero-designationContainer')
    category = category_site.find(class_='Hero-designation').text
    # print(category)

    address_listing = soupDetail.find(class_='vcard')
    full_address = address_listing.find(class_='adr')
    city_address = full_address.find(itemprop='addressLocality').text
    state_address = full_address.find(itemprop='addressRegion').text
    address = city_address + ', ' + state_address
    #print(address)
    
    zip_address = full_address.find(itemprop='postalCode').text
    
    phone_num = address_listing.find(itemprop='telephone').text
    #print(phone_num)
    var = NationalSite(category, name, address, zip_address.strip(), phone_num.strip())

    return var


def open_cache():
    ''' Opens the cache file if it exists and loads the JSON into
    the CACHE_DICT dictionary.
    if the cache file doesn't exist, creates a new cache dictionary
    
    Parameters
    ----------
    None
    
    Returns
    -------
    The opened cache: dict
    '''
    try:
        cache_file = open(CACHE_FILENAME, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict


def save_cache(cache_dict):
    ''' Saves the current state of the cache to disk
    
    Parameters
    ----------
    cache_dict: dict
        The dictionary to save
    
    Returns
    -------
    None
    '''
    dumped_json_cache = json.dumps(cache_dict)
    fw = open(CACHE_FILENAME,"w")
    fw.write(dumped_json_cache)
    fw.close()


def make_request_with_cache(url):
    '''Check the cache for a saved result for this baseurl+params:values
    combo. If the result is found, return it. Otherwise send a new 
    request, save it, then return it.

    AUTOGRADER NOTES: To test your use of caching in the autograder, please do the following:
    If the result is in your cache, print "fetching cached data"
    If you request a new result using make_request(), print "making new request"

    Do no include the print statements in your return statement. Just print them as appropriate.
    This, of course, does not ensure that you correctly retrieved that data from your cache, 
    but it will help us to see if you are appropriately attempting to use the cache.
    
    Parameters
    ----------
    url

    Returns
    -------
    dict
        the results of the query as a dictionary loaded from cache
        JSON
    '''
    #TODO Implement function
    # construct params dict based on hashtag and count

    CACHE_DICT = open_cache() # when you want to check if something is in cache dictionary need to make sure it is open to be checked

    if url in CACHE_DICT.keys():
        print("using cache")
        return CACHE_DICT[url]
        # return make_request(baseurl, params)
    else:
        print("fetching")
        response = requests.get(url)
        CACHE_DICT[url] = response.text
        save_cache(CACHE_DICT)
        return CACHE_DICT[url]


def get_sites_for_state(state_url):
    '''Make a list of national site instances from a state URL.
    
    Parameters
    ----------
    state_url: string
        The URL for a state page in nps.gov
    
    Returns
    -------
    list
        a list of national site instances
    '''
    cache_dict_response = make_request_with_cache(state_url)
    state_url_list = []


    # response = requests.get(state_url)
    #response.text
    soupDetails = BeautifulSoup(cache_dict_response, 'html.parser')

    all_park_links = soupDetails.find(id='parkListResultsArea')
    list_elements = all_park_links.find_all('li', class_='clearfix')


    for x in list_elements:
        url = x.find('h3')
        park_link_tag = url.find('a')
        state_path = park_link_tag['href']
        full_url = base_url + state_path
        state_url_list.append(full_url)

    national_site_instances = []

    for url in state_url_list:
        lo = get_site_instance(url)
        national_site_instances.append(lo)

    return national_site_instances

def make_zip_request_with_cache(site_object, params=None, base_url=None):
    '''Check the cache for a saved result for this baseurl+params:values
    combo. If the result is found, return it. Otherwise send a new 
    request, save it, then return it.

    Parameters
    ----------
    site_object

    Returns
    -------
    dict
        the results of the query as a dictionary loaded from cache
        JSON
    '''
    #TODO Implement function

    CACHE_DICT = open_cache() # when you want to check if something is in cache dictionary need to make sure it is open to be checked

    if site_object in CACHE_DICT.keys():
        print("using cache")
        return CACHE_DICT[site_object]
    else:
        print("fetching")
        response = requests.get(base_url, params)
        CACHE_DICT[site_object] = response.json()
        save_cache(CACHE_DICT)
        return CACHE_DICT[site_object]

def get_nearby_places(site_object):
    '''Obtain API data from MapQuest API.
    
    Parameters
    ----------
    site_object: object
        an instance of a national site
    
    Returns
    -------
    dict
        a converted API return from MapQuest API
    '''


    '''
    parameters for mapquest api request
    key: API key from secrets.py
    origin: Zip code of a national site(UseNationalSite instance attribute.)
    radius: Distance from the origin to search is 10 miles.
    maxMatches: The number of results returned in the response is 10.
    ambiguities: “ignore”
    outFormat:“json”
    '''

    base_url = 'http://www.mapquestapi.com/search/v2/radius'
    params = {'key' : api_key,
                'origin': site_object.zipcode ,
                'radius': 10,
                'maxMatches' : 10,
                'ambiguities' : 'ignore',
                'outFormat' : 'json'
    }
    cache_dict_response = make_zip_request_with_cache(site_object.info(), params, base_url)

    distance_data = cache_dict_response
    searchResults = distance_data['searchResults']
    for result in searchResults:
        name = result['name']
        address = result['fields']['address']
        if address == '':
            address = 'no address'
        category = result['fields']['group_sic_code_name_ext']
        if category == '':
            category = 'no category'
        city = result['fields']['city']
        if city == '':
            city = 'no city'
        string_rep = f"{name} ({category}) : {address}, {city}\n"
    print(string_rep)
    return cache_dict_response



if __name__ == "__main__":
    # build_state_url_dict()
    # state_websites = get_sites_for_state('https://www.nps.gov/state/ak/index.htm')
    # print(state_websites)
    # get_nearby_places(site_instance)


    # user_input = input("Please enter a state name or exit: ")
    # if user_input.isalpha():
    # else:
    #     print('Enter proper state name')

    def get_userInput():
        '''
        Parameters: No parameters

        This function prompts users to enter a search term or to exit the program.
        Users can enter exit to leave the program or
        Users can enter a search term state info. An organized list is returned to the screen.
        
        When exit is entered, the program quits.

        '''
        #state = input("Please enter a state name or exit: ")
        while True:
            state = input("Please enter a state name or exit: ")
            if state != 'exit':
                if state.isalpha():
                    dictionary = build_state_url_dict()
                    if state.lower() in dictionary.keys():
                        print(f'List of National Sites in {state.title()}')
                        state_website = dictionary[state.lower()]
                        site_instances = get_sites_for_state(state_website)
                        # print(site_instances)
                        for i, site_instance in enumerate(site_instances):
                            print(f'[{i}] {site_instance.info()}')

                    while True:
                        user_input = input("Choose a number for more detail or 'back' or 'exit': ")
                        if user_input.isnumeric() == True:
                            user_input = int(user_input)
                            if user_input <= len(site_instances):
                                user_input = user_input -1
                                print(f'Places near {site_instances[user_input].name}')
                                print(get_nearby_places(site_instances[user_input]))
                            else:
                                print("Invalid number")

                        elif user_input.isalpha() and user_input.lower() == 'back':
                            print('Going back...')
                            #state
                        elif user_input.isalpha() and user_input.lower() =='exit':
                            print('Goodbye!')
                        break
            else:
                break

    get_userInput()

