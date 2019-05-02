# -*- coding: utf-8 -*-
from geopy.geocoders import *


def get_place(lat, lon):
    geolocator = Nominatim()
    location = []
    location = reverse(lat, lon, 0)
    if location == 0:
        string = str(lat) + ' ' + str(lon)
        return string, string
    if 'city' in location.raw['address'].keys():
        city = location.raw['address']['city']
    elif 'town' in location.raw['address'].keys():
        city = location.raw['address']['town']
    else:
        city = location.raw['address']['county']
    country = location.raw['address']['country']
    return city, country


def reverse(lat, lon, recursion):
    query = str(lat) + ', ' + str(lon)
    geolocator = Nominatim()
    location = []
    if recursion > 50:
        return 0
    try:
        location = geolocator.reverse(query, language='en')
        return location
    except:
        print ('except', lat, lon)
        return reverse(lat, lon, recursion + 1)


def occurrences(vector, category, field):
    count = 0
    for e in vector:
        if e[category] == field:
            count = count + 1
    return count
