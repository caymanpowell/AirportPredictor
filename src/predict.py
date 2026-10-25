# Ask user for date and time and predict airport wait time
import pandas as pd
import requests
import boto3
import torch
from datetime import datetime

bucket = "dtsc3601-airport" # bucket name in s3
s3 = boto3.client("s3") # create s3 client

s3.download_file(bucket, "models/wait_time_model.pt", "wait_time_model.pt") # download trained model from s3
model = torch.load("wait_time_model.pt", weights_only=False) # load trained model
s3.download_file(bucket, "data/clean_wait_times.csv", "clean_wait_times.csv") # download historical data
df = pd.read_csv("clean_wait_times.csv") # read historical data

print("Airport Wait Time Predictor\n")

date_input = input("Enter date (YYYY-MM-DD): ")
hour = int(input("Enter hour (0-23): "))
if hour < 0 or hour > 23: # check if hour is valid
    print("Hour must be between 0 and 23.")
    exit()
date = datetime.strptime(date_input, "%Y-%m-%d") # convert date input to datetime object
today = datetime.today().date() # get today's date
if (date.date() - today).days < 0 or (date.date() - today).days > 7:
    print("Date must be between today and 7 days from today.")
    exit()
month = date.month # get month from date
day_of_week = date.weekday() # get day of week from date

# find similar historical airport data
similar_data = df[(df["hour"] == hour) & (df["day_of_week"] == day_of_week) & (df["month"] == month)]

# use a larger group if there is no exact historical match
if len(similar_data) == 0:
    similar_data = df[(df["hour"] == hour) & (df["month"] == month)]
if len(similar_data) == 0:
    similar_data = df[df["hour"] == hour]
if len(similar_data) == 0:
    similar_data = df
passengers = round(similar_data["TotalPassengerCount"].mean())
flights = round(similar_data["FlightCount"].mean())
booths = round(similar_data["BoothsUsed"].mean())
print("\nEstimated airport conditions:")
print("Passenger count:", passengers)
print("Flight count:", flights)
print("Booths being used:", booths)

url = "https://api.open-meteo.com/v1/forecast" # weather api url
params = {"latitude": 35.214, "longitude": -80.943, "hourly": "temperature_2m,precipitation,wind_speed_10m", "temperature_unit": "fahrenheit",
    "wind_speed_unit": "mph", "precipitation_unit": "inch", "forecast_days": 8, "timezone": "America/New_York"} # api parameters
print("\nGetting weather data from API...")

response = requests.get(url, params=params) # get weather from api

if response.status_code != 200:
    print("Could not get weather data.")
    exit()
data = response.json()
if hour < 10: # fix formatting if hour is less than 10
    target_time = date_input + "T0" + str(hour) + ":00"
else:
    target_time = date_input + "T" + str(hour) + ":00"
if target_time not in data["hourly"]["time"]:
    print("Weather forecast is not available for that time.")
    exit()

index = data["hourly"]["time"].index(target_time) # find forecast for entered time
temperature = data["hourly"]["temperature_2m"][index]
print("Temperature:", temperature, "F")
precipitation = data["hourly"]["precipitation"][index]
print("Precipitation:", precipitation, "in")
wind_speed = data["hourly"]["wind_speed_10m"][index]
print("Wind speed:", wind_speed, "mph")
prediction_data = pd.DataFrame([{"hour": hour, "day_of_week": day_of_week, "month": month, "TotalPassengerCount": passengers,
    "FlightCount": flights, "BoothsUsed": booths, "temperature": temperature, "precipitation": precipitation, "wind_speed": wind_speed}])

prediction = model.predict(prediction_data) # make prediction

print(
    "\nPredicted airport wait time:",
    round(prediction[0], 2),
    "minutes"
)