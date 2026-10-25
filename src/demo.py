# Demo to train the model and make predictions without AWS
import pandas as pd
import requests
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score

# Read cleaned historical data
df = pd.read_csv("data/clean_wait_times.csv")
# Model features and target
x = df[["hour", "day_of_week", "month", "TotalPassengerCount", "FlightCount", "BoothsUsed", "temperature", "precipitation", "wind_speed"]]
y = df["AverageWait"]
# Split data
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)
# Train model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(x_train, y_train)
# Test model
predictions = model.predict(x_test)
mae = mean_absolute_error(y_test, predictions)
r2 = r2_score(y_test, predictions)
print("MAE:", round(mae, 2))
print("R2:", round(r2, 2))
print("Model trained successfully.\n")
# Ask user for prediction information
print("Airport Wait Time Predictor\n")
date_input = input("Enter date (YYYY-MM-DD): ")
hour = int(input("Enter hour (0-23): "))
if hour < 0 or hour > 23:
    print("Hour must be between 0 and 23.")
    exit()
date = datetime.strptime(date_input, "%Y-%m-%d")
today = datetime.today().date()
if (date.date() - today).days < 0 or (date.date() - today).days > 7:
    print("Date must be between today and 7 days from today.")
    exit()
month = date.month
day_of_week = date.weekday()
# Find similar historical airport conditions
similar_data = df[(df["hour"] == hour) & (df["day_of_week"] == day_of_week) & (df["month"] == month)]
# Use larger groups if there are no exact matches
if len(similar_data) == 0:
    similar_data = df[(df["hour"] == hour) & (df["month"] == month)]
if len(similar_data) == 0:
    similar_data = df[df["hour"] == hour]
if len(similar_data) == 0:
    similar_data = df
# Estimate airport conditions
passengers = round(similar_data["TotalPassengerCount"].mean())
flights = round(similar_data["FlightCount"].mean())
booths = round(similar_data["BoothsUsed"].mean())
print("Estimated airport conditions:")
print("Passenger count:", passengers)
print("Flight count:", flights)
print("Booths being used:", booths)

# Get forecast weather
url = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": 35.214, "longitude": -80.943, "hourly": "temperature_2m,precipitation,wind_speed_10m", "temperature_unit": "fahrenheit",
    "wind_speed_unit": "mph", "precipitation_unit": "inch", "forecast_days": 8, "timezone": "America/New_York"}

print("\nGetting weather data from API...")
response = requests.get(url, params=params)
if response.status_code != 200:
    print("Could not get weather data.")
    exit()
data = response.json()
if hour < 10:
    target_time = date_input + "T0" + str(hour) + ":00"
else:
    target_time = date_input + "T" + str(hour) + ":00"
if target_time not in data["hourly"]["time"]:
    print("Weather forecast is not available for that time.")
    exit()

index = data["hourly"]["time"].index(target_time)
temperature = data["hourly"]["temperature_2m"][index]
precipitation = data["hourly"]["precipitation"][index]
wind_speed = data["hourly"]["wind_speed_10m"][index]
print("Temperature:", temperature, "F")
print("Precipitation:", precipitation, "in")
print("Wind speed:", wind_speed, "mph")

# Create data for prediction
prediction_data = pd.DataFrame([{"hour": hour, "day_of_week": day_of_week,
    "month": month, "TotalPassengerCount": passengers, "FlightCount": flights, "BoothsUsed": booths,
    "temperature": temperature, "precipitation": precipitation, "wind_speed": wind_speed}])
# Make prediction
prediction = model.predict(prediction_data)
print("\nPredicted airport wait time:", round(prediction[0], 2), "minutes")