import requests
import subprocess

from dotenv import load_dotenv
import os

env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=env_path)

# Now you can safely retrieve the API key
api_key = os.getenv("GOOGLE_API_KEY")


def get_ip():
    response = requests.get('https://api64.ipify.org?format=json').json()
    return response["ip"]

def get_wifi_networks(interface='wlan0'):
    cmd = ['sudo', 'iwlist', interface, 'scan']
    result = subprocess.run(cmd, stdout=subprocess.PIPE)
    output = result.stdout.decode('utf-8')

    wifi_list = []
    for line in output.split('\n'):
        if "Address" in line:
            mac = line.split("Address: ")[1]
        if "Signal level" in line:
            signal = int(line.split('=')[2].split(' ')[0])
            wifi_list.append({
                "macAddress": mac,
                "signalStrength": signal
            })
    print(wifi_list)
    return wifi_list

def get_location(_=None):
    wifi_list = get_wifi_networks()
    geolocation_url = f'https://www.googleapis.com/geolocation/v1/geolocate?key={api_key}'
    geolocation_data = {
        'wifiAccessPoints': wifi_list,
    }
    geolocation_response = requests.post(geolocation_url, json=geolocation_data).json()
    
    location = geolocation_response.get('location')
    if location:
        # Now perform reverse geocoding to get the street address
        lat, lng = location['lat'], location['lng']
        reverse_geocode_url = f'https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lng}&key={api_key}'
        reverse_geocode_response = requests.get(reverse_geocode_url).json()
        
        # Extract the formatted address from the first result
        results = reverse_geocode_response.get('results', [])
        if results:
            address = results[0].get('formatted_address')
            return address

    return None  # or return an appropriate message/error
