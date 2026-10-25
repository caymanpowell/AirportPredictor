# Airport Wait Time Predictor Documentation

## Overview

Airport Wait Time Predictor is a predictive analytics project that forecasts average CBP processing wait times at Charlotte Douglas International Airport (CLT). The project uses historical CBP processing data, airport operating conditions, and weather information to predict future average wait times.

The project contains two ways to run the model:
- `bin/demo.py` provides a standalone demo that does not require AWS.
- The scripts in `src/` provide the complete version that uses Amazon S3 for data and model storage.

---

## bin/demo.py

`demo.py` provides a standalone version of the Airport Wait Time Predictor.
It uses the cleaned dataset included in the repository and does not require access to AWS.

### How It Works

1. Loads `data/clean_wait_times.csv`.
2. Separates the model features from the `AverageWait` target variable.
3. Splits the dataset into training and testing sets.
4. Trains a Random Forest regression model.
5. Calculates Mean Absolute Error (MAE) and R-squared.
6. Asks the user for a future date and hour.
7. Finds historical records with similar time information.
8. Estimates passenger count, flight count, and booth usage from the historical data.
9. Retrieves forecast weather from the Open-Meteo API.
10. Creates the input data for the model.
11. Predicts the average CBP processing wait time.

### User Input

The user enters:

- Future date
- Hour of the day

### Automatically Retrieved or Estimated Data

The program automatically estimates:

- Passenger count
- Flight count
- Number of booths being used

The program retrieves the following weather information from Open-Meteo:

- Temperature
- Precipitation
- Wind speed

### Output

The output is a predicted average CBP processing wait time in minutes.

Run the demo with:

```bash
python bin/demo.py
```

---

## src/get_weather_data.py

`get_weather_data.py` retrieves the historical weather information used during model training.

### How It Works

1. Connects to the Open-Meteo historical weather API.
2. Requests hourly weather data for the CLT area.
3. Retrieves:
   - Temperature
   - Precipitation
   - Wind speed
4. Converts the API response into a pandas DataFrame.
5. Saves the weather data as `weather_data.csv`.
6. Uploads the weather data to Amazon S3.

The historical weather data is used with the historical airport data during preprocessing.

Run with:

```bash
python src/get_weather_data.py
```

---

## src/preprocessing.py

`preprocessing.py` prepares the historical airport and weather data for model training.

### How It Works

1. Downloads the historical CBP airport wait-time data from Amazon S3.
2. Downloads the historical weather data from Amazon S3.
3. Reads both datasets using pandas.
4. Converts the flight date into a datetime value.
5. Creates the following time features:
   - `hour`
   - `day_of_week`
   - `month`
6. Matches the airport data with weather data using date and hour.
7. Removes missing values.
8. Removes invalid negative values.
9. Keeps only the features needed by the prediction model.
10. Saves the cleaned data as `clean_wait_times.csv`.
11. Uploads the cleaned dataset back to Amazon S3.

### Cleaned Data Features

The processed dataset contains:

- `hour`
- `day_of_week`
- `month`
- `TotalPassengerCount`
- `FlightCount`
- `BoothsUsed`
- `temperature`
- `precipitation`
- `wind_speed`
- `AverageWait`

Run with:

```bash
python src/preprocessing.py
```

---

## src/train_model.py

`train_model.py` trains and evaluates the airport wait-time prediction model.

### How It Works

1. Downloads `clean_wait_times.csv` from Amazon S3.
2. Reads the cleaned dataset using pandas.
3. Separates the input features from the target variable.
4. Splits the dataset into training and testing sets.
5. Creates a Random Forest regression model.
6. Trains the model using the training data.
7. Makes predictions using the testing data.
8. Calculates model performance using:
   - Mean Absolute Error (MAE)
   - R-squared
9. Saves the trained model as `wait_time_model.pt`.
10. Uploads the trained model to Amazon S3.

### Model

The project uses a RandomForestRegressor model

### Input Features

The model uses nine input features:

- `hour`
- `day_of_week`
- `month`
- `TotalPassengerCount`
- `FlightCount`
- `BoothsUsed`
- `temperature`
- `precipitation`
- `wind_speed`

### Target Variable

The target variable is Average Wait. `AverageWait` represents the average CBP processing wait time in minutes.

### Evaluation

The model is evaluated using:

- Mean Absolute Error (MAE)
- R-squared

The current model has produced approximately:
MAE: 6.52
R2: 0.24

Run with:

```bash
python src/train_model.py
```

---

## src/predict.py

`predict.py` is the full AWS-based prediction program.

### How It Works

1. Downloads the trained model from Amazon S3.
2. Loads the trained model.
3. Downloads the cleaned historical dataset from Amazon S3.
4. Asks the user for:
   - Future date
   - Hour
5. Calculates the month and day of the week.
6. Finds historical records with similar time information.
7. Estimates:
   - Passenger count
   - Flight count
   - Booth usage
8. Requests forecast weather from the Open-Meteo API.
9. Retrieves:
   - Temperature
   - Precipitation
   - Wind speed
10. Creates a row containing all nine model features.
11. Sends the input data to the trained model.
12. Displays the predicted average CBP processing wait time.

### Historical Estimates

The program first searches for records with the same:

- Hour
- Day of week
- Month

If an exact group is unavailable, it uses a broader group of historical records.

This allows the program to estimate airport operating conditions without requiring the user to know passenger counts, flight counts, or booth staffing.

Run with:

```bash
python src/predict.py
```

---

## Model Feature Descriptions

### `hour`

The hour of the day for the prediction.

Airport traffic and processing times can vary throughout the day.

### `day_of_week`

The day of the week represented as a numeric value.

This allows the model to learn differences between different days of the week.

### `month`

The month of the year.

This allows the model to account for seasonal travel patterns.

### `TotalPassengerCount`

The number of passengers being processed during the time period.

Higher passenger volume may increase processing wait times.

### `FlightCount`

The number of flights represented during the time period.

Flight volume provides another measurement of airport activity.

### `BoothsUsed`

The number of CBP processing booths being used.

This represents the available processing capacity.

### `temperature`

The forecast or historical temperature in Fahrenheit.

### `precipitation`

The forecast or historical precipitation in inches.

### `wind_speed`

The forecast or historical wind speed in miles per hour.

Weather features are included because weather conditions may affect airport operations.

---

## Project Workflow

The complete AWS pipeline is:

```text
Historical CBP Data
        |
        v
    Amazon S3

Open-Meteo Historical Weather API
        |
        v
get_weather_data.py
        |
        v
    Amazon S3
        |
        v
preprocessing.py
        |
        v
clean_wait_times.csv
        |
        v
train_model.py
        |
        v
wait_time_model.pt
        |
        v
    Amazon S3
        |
        v
predict.py
        |
        +---- Open-Meteo Forecast API
        |
        v
Predicted CBP Wait Time
```

The standalone demo uses a simpler workflow:

```text
data/clean_wait_times.csv
        |
        v
bin/demo.py
        |
        +---- Open-Meteo Forecast API
        |
        v
Predicted CBP Wait Time
```

---

## Limitations

The model is trained specifically on CBP processing data from Charlotte Douglas International Airport.
Future passenger count, flight count, and booth usage are estimated using historical records rather than known information.
Weather forecasts may also change as the requested date approaches.
