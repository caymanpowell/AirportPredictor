# Get historical weather data from API and save it to s3
import requests
import pandas as pd
import boto3

bucket = "dtsc3601-airport" # bucket name in s3
s3 = boto3.client("s3") # create s3 client

url = "https://archive-api.open-meteo.com/v1/archive"

params = {"latitude": 35.214, "longitude": -80.943, "start_date": "2023-05-03", "end_date": "2026-09-25", "hourly": "temperature_2m,precipitation,wind_speed_10m",
          "temperature_unit": "fahrenheit", "wind_speed_unit": "mph", "precipitation_unit": "inch", "timezone": "America/New_York"}
response = requests.get(url, params=params) # request historical weather data
if response.status_code != 200:
    print("Could not get historical weather data.")
    exit()
data = response.json() # turn response into json
weather = pd.DataFrame({"datetime": data["hourly"]["time"], "temperature": data["hourly"]["temperature_2m"], "precipitation": data["hourly"]["precipitation"], "wind_speed": data["hourly"]["wind_speed_10m"]}) # create dataframe
weather.to_csv("weather_data.csv", index=False) # save locally
s3.upload_file("weather_data.csv", bucket, "api/weather_data.csv") # upload to s3
print("Historical weather data uploaded to S3.")