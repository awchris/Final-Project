import json, urllib.parse, urllib.request, urllib.error

def pretty(obj):
    return json.dumps(obj, sort_keys=True, indent=2)
#Turn address into lat/lng, get timezone

def safe_url_get(url):
    try:
        return urllib.request.urlopen(url)
    except urllib.error.HTTPError as e:
        return None

def get_latlng(address):
    base_url = "https://api.geoapify.com/v1/geocode/search"
    api_key = 'e3f9dfcf327545638b4cadf1e36710d4'
    urldict = {'text': address,'apiKey': api_key}
    paramstr = urllib.parse.urlencode(urldict)
    request_url = '{}?{}'.format(base_url,paramstr)
    data = safe_url_get(request_url)
    if data != None:
        data_dict = json.loads(data.read())
        try:
            lat = data_dict['features'][0]['properties']['lat']
            lng = data_dict['features'][0]['properties']['lon']
            tz = data_dict['features'][0]['properties']['timezone']['offset_STD']
            int_tz = int(tz[0:3])
            return_dict = {'lat':lat,'lng':lng,'tz_offset':int_tz}
            return return_dict
        except: 
            return None 
    else:
        return None

#Use lat/lng to get sunset
def get_sunset(lat,lng):
    request_url = 'https://api.sunrise-sunset.org/json?lat={}?lng={}'.format(lat,lng)
    data = urllib.request.urlopen(request_url).read()
    data_dict = json.loads(data)
    time = data_dict['results']['civil_twilight_end']
    am_pm = time[-1:-3]
    if am_pm == 'AM':
        is_am = True
    else:
        is_am = False
        am_pm = 'PM'
    hour = int(time.split(':')[0])
    mins = int(time.split(':')[1])
    sec = int(time.split(':')[2][0:2])
    if sec >= 30:
        mins+=1 
    sunset_time = '{}:{} {}'.format(hour,mins,am_pm)
    time_dict = {'sunset':sunset_time,'hour':hour,'mins':mins,'is_am':is_am}
    return time_dict

#Use Bing Maps distance matrix API to calculate travel distance + time
def get_trip_info(lat1, lng1, lat2, lng2):
    key = 'ArbxP41liKEMTC-j65YsT6xXzCC7y0DMYaFE1BJZSi8boqFtk0gQbgYnOPyrXobe'
    url = 'http://dev.virtualearth.net/REST/V1/Routes/Walking?wp.0={},{}&wp.1={},{}&key={}'.format(lat1,lng1,lat2,lng2,key)
    data = safe_url_get(url)
    if data != None:
        data_dict = json.loads(data.read())
        trip_time = int(data_dict['resourceSets'][0]['resources'][0]['travelDuration'])
        trip_distance = data_dict['resourceSets'][0]['resources'][0]['travelDistance']
        trip_info = {'time':trip_time,'distance':trip_distance}
        return trip_info
    else:
        return None

#Use trip info to calculate latest departure + adjust trip time to hr:min format
def calc_latest_departure(hour, mins, is_am, trip_time):
    trip_mins = round((trip_time/60) % 60)
    trip_hours = trip_time//3600
    max_min = mins - trip_mins 
    if max_min < 0:
        max_min += 60
        trip_hours += 1
    max_hour = hour - trip_hours
    if max_hour < 1:
        max_hour += 12 
        is_am = not is_am 
    am_pm = 'AM'
    if is_am == False:
        am_pm = 'PM'
    if len(str(max_min)) == 1:
        max_min = '0'+str(max_min)
    elif max_min == 0:
        max_min = '00'
    latest_time = '{}:{} {}'.format(max_hour,max_min,am_pm)
    clean_trip_time = '{}hrs {}mins'.format(trip_hours, trip_mins)
    departure_dict = {'latest_time':latest_time,'trip_time':clean_trip_time}
    return departure_dict


#Get map image
def get_map_url(lat1,lng1,lat2,lng2):
    key='ArbxP41liKEMTC-j65YsT6xXzCC7y0DMYaFE1BJZSi8boqFtk0gQbgYnOPyrXobe'
    url='https://dev.virtualearth.net/REST/v1/Imagery/Map/Road/Routes/Walking?wp.0={},{}&wp.1={},{}&format=png&mapSize=500,500&key={}'.format(lat1,lng1,lat2,lng2,key)
    return(url)

#get_map(47.649177,-122.30219,47.658253,-122.322965)
    

def get_key_data(loc1, loc2):
    latlng1 = get_latlng(loc1)
    latlng2 = get_latlng(loc2)
    if latlng1 and latlng2 != None:
        lat1 = latlng1['lat'] 
        lng1 = latlng1['lng'] 

        lat2 = latlng2['lat'] 
        lng2 = latlng2['lng'] 

        sunset_dict = get_sunset(lat1,lng1)
        sunset = sunset_dict['sunset']
        hour = sunset_dict['hour']
        mins = sunset_dict['mins']
        is_am = sunset_dict['is_am']
    
        trip_info_dict = get_trip_info(lat1,lng1,lat2,lng2)
        if trip_info_dict != None:
            trip_time = trip_info_dict['time']
            trip_distance = trip_info_dict['distance']    

            departure_dict = calc_latest_departure(hour,mins,is_am,trip_time)

            clean_trip_time = departure_dict['trip_time']
            departure_time = departure_dict['latest_time']
            map_url = get_map_url(lat1,lng1,lat2,lng2)
            key_data = {'sunset_time':sunset,'trip_time':clean_trip_time,'trip_distance':trip_distance,'departure_time':departure_time,'map':map_url}
            return key_data
        else:
            return None
    else:
        return None


