import requests
import time
import datetime

API_URL = "https://bz4z5d4iwi.execute-api.us-east-2.amazonaws.com/prod"

SEARCH_URL = API_URL+'/networks'

SEARCH_TEMPLATE = SEARCH_URL+"?lat={lat}&lon={lon}&radius={radius}"

lat_start = 46
lat_end = 47

lon_start = -73
lon_end = -74

NUM_REQUEST = 1000



def main():
    results = []
    req_url = SEARCH_TEMPLATE.format(lat=45.48, lon=-73.58, radius=100)

    t_start = time.time()
    req = requests.get(req_url)
    t_elapsed = time.time() - t_start

    print(req.text)

    print("Request time to response headers: ", req.elapsed.microseconds / 1000)
    print("Request total time: ", t_elapsed * 1000)



main()