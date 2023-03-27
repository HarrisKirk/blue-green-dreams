import json
import datetime
import pandas

def list_of_dict_to_html(day_list):
    df = pandas.DataFrame(day_list)
    html_table = df.to_html(index=False, header=True)
    return html_table

def render(weather_api_key, json_string, day_list):
    return f"""
        <!DOCTYPE html>
        <html>
        <body>
        <h1>Richmond weather at {datetime.datetime.now()}:</h1>
        {list_of_dict_to_html(day_list)}
        </body>
        </html>
    """    
