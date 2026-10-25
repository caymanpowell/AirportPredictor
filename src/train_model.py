# Train model using cleaned wait times data from s3
import boto3
import pandas as pd
import torch
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score

def train_model():
    bucket = "dtsc3601-airport" # bucket name in s3
    file = "data/clean_wait_times.csv" # cleaned data file in s3
    s3 = boto3.client("s3") # create s3 client

    s3.download_file(bucket, file, "clean_wait_times.csv") # download cleaned data
    df = pd.read_csv("clean_wait_times.csv") # read csv file
    x = df[["hour", "day_of_week", "month", "TotalPassengerCount", "FlightCount", "BoothsUsed",
            "temperature", "precipitation", "wind_speed"]] # features
    y = df["AverageWait"] # target variable
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42) # split data into training and testing data

    model = RandomForestRegressor(n_estimators=100, random_state=42) # create model
    model.fit(x_train, y_train) # train model
    predictions = model.predict(x_test) # test model
    mae = mean_absolute_error(y_test, predictions) # calculate mean absolute error
    r2 = r2_score(y_test, predictions) # calculate r2 score
    print("MAE:", round(mae, 2))
    print("R2:", round(r2, 2))
    local_model_path = "wait_time_model.pt" # model file name
    torch.save(model, local_model_path) # save trained model locally
    s3.upload_file(Filename=local_model_path, Bucket=bucket, Key="models/wait_time_model.pt") # upload trained model to s3
    print("Model uploaded to S3.")

if __name__ == "__main__":
    train_model()