import requests
import json
import gwa.sample
import gwa.rendering

USE_LIVE_DATA = True

def get_weather_json(weather_api_key, use_live_data = True):
    if use_live_data:
        weather_url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/richmond%2C%20va?unitGroup=metric&include=days&key={weather_api_key}&contentType=json"
        return requests.get(weather_url).text
    return gwa.sample.sample_json

def get_rendered_site_data(weather_api_key):
    json_string = get_weather_json(weather_api_key, USE_LIVE_DATA)
    parsed_json = json.loads(json_string)
    pretty_json_string = json.dumps(parsed_json, indent=4, sort_keys=True)
    day_list = get_day_info(parsed_json)
    return gwa.rendering.render(weather_api_key, pretty_json_string, day_list)

def get_day_info(parsed_json):
    days = [dict({"datetime": day['datetime'], 'feelslikemax': day['feelslikemax']}) for day in parsed_json['days'] ]
    days = [dict({"datetime": '', 'feelslikemax': ''})] + days
    return days

