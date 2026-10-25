# Airport Wait Time Predictor

Airport Wait Time Predictor is a predictive analytics project that forecasts average CBP processing wait times at Charlotte Douglas International Airport (CLT). The project uses historical airport processing data, airport operating conditions, and weather information to estimate future wait times.


## Group 9

- Cayman Powell
- Ryan Moser
- Elijah Ford
- Brendan Higgins

## Installation

### Requirements

The project requires Python 3 and the following libraries:

- pandas
- boto3
- requests
- scikit-learn
- torch

### Clone the Repository

```bash
git clone https://github.com/caymanpowell/AirportPredictor.git
cd AirportPredictor
```

### Create a Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Install Required Libraries

```bash
pip install -r requirements.txt
```

## Get Started/Demo

This script loads the cleaned data, trains and evaluates the Random Forest regression model, asks the user for a future date and hour, retrieves forecast weather from Open-Meteo, estimates airport operating conditions from historical data, and produces a predicted CBP processing wait time. The demo does not use AWS, although this functionality still exists in the full pipeline (as listed below).

Run:

```bash
python bin/demo.py
```

This script loads the cleaned data, trains a Random Forest regression model, and evaluates the model using Mean Absolute Error (MAE) and R-squared.

## Full Project

The complete project uses Amazon S3 for data and model storage and Open-Meteo for weather data.

Run the pipeline in the following order.

### 1. Retrieve Historical Weather Data

```bash
python src/get_weather_data.py
```

This script retrieves historical temperature, precipitation, and wind speed from the Open-Meteo API and uploads the data to Amazon S3.

### 2. Preprocess the Data

```bash
python src/preprocessing.py
```

This script downloads the historical CBP airport data and historical weather data from Amazon S3.

It then:

- Converts dates into a usable format.
- Creates hour, day-of-week, and month features.
- Combines the airport and weather datasets using date and hour.
- Removes missing and invalid values.
- Selects the features needed by the model.
- Uploads the cleaned training data back to Amazon S3.

### 3. Train the Model

```bash
python src/train_model.py
```

This script downloads the cleaned dataset from Amazon S3, splits it into training and testing sets, and trains a `RandomForestRegressor`.

The model is evaluated using:

- Mean Absolute Error (MAE)
- R-squared

The trained model is saved and uploaded to Amazon S3.

### 4. Make a Prediction

```bash
python src/predict.py
```

The user enters:

- A future date
- An hour of the day

The requested date must be between the current date and seven days in the future.

The program then:

- Estimates passenger count using similar historical records.
- Estimates flight count using similar historical records.
- Estimates booth usage using similar historical records.
- Retrieves forecast temperature, precipitation, and wind speed from Open-Meteo.
- Downloads the trained model from Amazon S3.
- Predicts the average CBP processing wait time in minutes.

## Model

The model is a Random Forest regression model.

The input features are:

- Hour
- Day of week
- Month
- Passenger count
- Flight count
- Booths used
- Temperature
- Precipitation
- Wind speed

The output is `AverageWait`, which represents the predicted average CBP processing wait time in minutes. The model is a regression model because the output is a continuous numerical value.

## Data

The historical airport data comes from CBP Airport Wait Times data for Charlotte Douglas International Airport.

The cleaned training dataset is included in:

```text
data/clean_wait_times.csv
```

The cleaned dataset contains:

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

Historical and forecast weather information is retrieved from the Open-Meteo API.

## Project Files

### `src/demo.py`

Provides a quick way to train and evaluate the model using the cleaned dataset included in the repository.

### `src/get_weather_data.py`

Retrieves historical weather information from the Open-Meteo API and uploads it to Amazon S3.

### `src/preprocessing.py`

Downloads historical airport and weather data, combines and cleans the datasets, and uploads the processed training data to Amazon S3.

### `src/train_model.py`

Downloads the processed training data, trains and evaluates the Random Forest regression model, and uploads the trained model to Amazon S3.

### `src/predict.py`

Downloads the trained model, estimates future airport operating conditions, retrieves forecast weather, and produces a predicted wait time.

## Project Structure

```text
AirportPredictor/
├── README.md
├── LICENSE
├── requirements.txt
├── .gitignore
├── src/
│   ├── demo.py
│   ├── get_weather_data.py
│   ├── preprocessing.py
│   ├── train_model.py
│   └── predict.py
└── data/
    └── clean_wait_times.csv
```

## Limitations

The model is trained using CBP processing data from Charlotte Douglas International Airport and should not be treated as a prediction of TSA security wait times or wait times at other airports. Future passenger count, flight count, and booth usage are estimated from similar historical records rather than actual future operating data. Weather forecasts may also change as the requested date approaches.

## Questions

For questions about the project, contact Cayman Powell at cpowel71@charlotte.edu.

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for more information.
