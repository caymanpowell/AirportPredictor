import boto3
import pandas as pd

bucket = "dtsc3601-airport" # bucket name in s3
file = "data/Awt.cbp.gov_CLT_2023-03-05-2026-25-09.csv" # wait time file name in s3
weather_file = "api/weather_data.csv" # weather file name in s3
s3 = boto3.client("s3") # create s3 client
s3.download_file(bucket, file, "wait_times.csv") # download file from s3
s3.download_file(bucket, weather_file, "weather_data.csv") # download weather file from s3

df = pd.read_csv("wait_times.csv") # read csv file
weather = pd.read_csv("weather_data.csv") # read weather csv file

df["FlightDate"] = pd.to_datetime(df["FlightDate"], errors="coerce") # turn date into datetime
df["month"] = df["FlightDate"].dt.month # create month column
df["day_of_week"] = df["FlightDate"].dt.dayofweek # create day of week column
df["date"] = df["FlightDate"].dt.date # create date column
df["hour"] = df["HourRange"].astype(str).str[:2] # get first hour from range
df["hour"] = pd.to_numeric(df["hour"], errors="coerce") # change hour to numeric
weather["datetime"] = pd.to_datetime(weather["datetime"], errors="coerce") # turn weather time into datetime
weather["date"] = weather["datetime"].dt.date # create date column
weather["hour"] = weather["datetime"].dt.hour # create hour column
df = pd.merge(df, weather, on=["date", "hour"], how="inner") # combine wait time and weather data
df = df[["hour", "day_of_week", "month", "TotalPassengerCount", "FlightCount", "BoothsUsed",
         "temperature", "precipitation", "wind_speed", "AverageWait"]] # remove unneeded columns
df = df.dropna() # drop rows with missing values
df = df[df["AverageWait"] >= 0] # remove negative wait times
df = df[df["TotalPassengerCount"] >= 0] # remove negative passenger counts
df = df[df["FlightCount"] >= 0] # remove negative flight counts
df = df[df["BoothsUsed"] >= 0] # remove negative booth counts

df.to_csv("clean_wait_times.csv", index=False) # save cleaned file
s3.upload_file("clean_wait_times.csv", bucket, "data/clean_wait_times.csv") # upload cleaned file back to s3

print("Rows in cleaned data:", len(df))
print("Cleaned data uploaded to S3.")