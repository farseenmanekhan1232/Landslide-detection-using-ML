# IoT Weather Station Predicting Rainfall Intensity w/ TensorFlow

# Windows, Linux, or Ubuntu

# By Kutluhan Aktar

# Collates weather data on Google Sheets and interprets it with a neural network built in TensorFlow to make predictions on the rainfall intensity.

# For more information:
# https://www.theamplituhedron.com/projects/IoT_Weather_Station_Predicting_Rainfall_Intensity_with_TensorFlow

import tensorflow as tf
from tensorflow import keras
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os

# Create a class to build a neural network after getting, visualizing, and scaling (normalizing) weather data.


class Weather_Station:
    def __init__(self, data):
        self.df = data
        self.input = []
        self.label = []
        # Define class names for different rainfall intensity predictions and values.
        self.class_names = ['None', 'Light Rain',
                            'Moderate Rain', 'Heavy Rain', 'Violent Rain']
    # Create graphics for requested columns.

    def graphics(self, column_1, column_2, xlabel, ylabel):
        # Show requested columns from the data set:
        plt.style.use("dark_background")
        plt.gcf().canvas.set_window_title('IoT Weather Station')
        plt.hist2d(self.df[column_1], self.df[column_2])
        plt.colorbar()
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(xlabel)
        plt.show()
    # Visualize data before creating and feeding the neural network model.

    def data_visualization(self):
        # Inspect requested columns to build a model with appropriately formatted data:
        self.graphics('WD', '1h_RF', 'Wind Direction (deg)',
                      'One-Hour Rainfall (mm)')
        self.graphics('Av_WS', '1h_RF', 'Average Wind Speed (m/s)',
                      'One-Hour Rainfall (mm)')
        self.graphics('Mx_WS', '1h_RF', 'Maximum Wind Speed (m/s)',
                      'One-Hour Rainfall (mm)')
        self.graphics('24h_RF', '1h_RF', '24-Hour Rainfall (mm)',
                      'One-Hour Rainfall (mm)')
        self.graphics('Tem', '1h_RF', 'Temperature (°C)',
                      'One-Hour Rainfall (mm)')
        self.graphics('Hum', '1h_RF', 'Humidity (%)', 'One-Hour Rainfall (mm)')
        self.graphics('b_PR', '1h_RF', 'Barometric Pressure (hPA)',
                      'One-Hour Rainfall (mm)')
    # Scale (normalize) data depending on the neural network model.

    def scale_data(self):
        # Wind Direction and Speed:
        wv = self.df.pop('Av_WS')
        max_wv = self.df.pop('Mx_WS')
        # Convert to radians.
        wd_rad = self.df.pop('WD')*np.pi / 180
        # Calculate the wind x and y components.
        self.df['scaled_WX'] = wv*np.cos(wd_rad)
        self.df['scaled_WY'] = wv*np.sin(wd_rad)
        # Calculate the max wind x and y components.
        self.df['scaled_max_WX'] = max_wv*np.cos(wd_rad)
        self.df['scaled_max_WY'] = max_wv*np.sin(wd_rad)
        # Temperature:
        tem = self.df.pop('Tem')
        self.df['scaled_Tem'] = tem / 25
        # Humidity:
        hum = self.df.pop('Hum')
        self.df['scaled_Hum'] = hum / 70
        # Barometric Pressure:
        bPR = self.df.pop('b_PR')
        self.df["scaled_bPR"] = bPR / 1013
        # 24 Hour Rainfall (Approx.)
        rain_24 = self.df.pop('24h_RF')
        self.df['scaled_24h_RF'] = rain_24 / 24
    # Define the input and label arrays.

    def create_input_and_label(self):
        n = len(self.df)
        # Create the input array using the scaled variables:
        for i in range(n):
            self.input.append(np.array([self.df['scaled_WX'][i], self.df['scaled_WY'][i], self.df['scaled_max_WX'][i],
                              self.df['scaled_max_WY'][i], self.df['scaled_Tem'][i], self.df['scaled_Hum'][i], self.df['scaled_bPR'][i]]))
        self.input = np.asarray(self.input)
        # Create the label array using the one-hour and 24-hour rainfall variables:
        for i in range(n):
            _class = 0
            # Evaluate the approximate rainfall rate:
            approx_RF_rate = (self.df['1h_RF'][i] +
                              self.df['scaled_24h_RF'][i]) * 100
            # As labels, assign classes of rainfall intensity according to the approximate rainfall rate (mm):
            if approx_RF_rate == 0:
                _class = 0
            elif approx_RF_rate < 2.5:
                _class = 1
            elif 2.5 < approx_RF_rate and approx_RF_rate < 7.6:
                _class = 2
            elif 7.6 < approx_RF_rate and approx_RF_rate < 50:
                _class = 3
            else:
                _class = 4
            self.label.append(_class)
        self.label = np.asarray(self.label)
    # Split the data for the training and test sets.

    def split_data(self):
        n = len(self.df)
        # (60%, 40%) - (training, test)
        self.train_input = self.input[0:int(n*0.6)]
        self.test_input = self.input[int(n*0.6):]
        self.train_label = self.label[0:int(n*0.6)]
        self.test_label = self.label[int(n*0.6):]
    # Build and train the artificial neural network (ANN) to make predictions on the rainfall intensity with classes.

    def build_and_train_model(self):
        # Build the neural network:
        self.model = keras.Sequential([
            keras.Input(shape=(7,)),
            keras.layers.Dense(16, activation='relu'),
            keras.layers.Dense(32, activation='relu'),
            keras.layers.Dense(64, activation='relu'),
            keras.layers.Dense(128, activation='relu'),
            keras.layers.Dense(5, activation='softmax')
        ])
        # Compile:
        self.model.compile(
            optimizer='adam', loss="sparse_categorical_crossentropy", metrics=['accuracy'])
        # Train:
        self.model.fit(self.train_input, self.train_label, epochs=19)
        # Test the accuracy:
        print("\n\nModel Evaluation:")
        test_loss, test_acc = self.model.evaluate(
            self.test_input, self.test_label)
        print("Evaluated Accuracy: ", test_acc)
    # Make rainfall intensity class [0 - 4] predictions using different input arrays.

    def make_prediction(self, pre_array):
        print("\n\nModel Predictions:\n")
        prediction = self.model.predict(pre_array)
        for i in range(len(pre_array)):
            print("Prediction => ", self.class_names[np.argmax(prediction[i])])
    # Save the model for further usage without training steps:

    def save_model(self):
        self.model.save(os.getcwd()+"/weather_station.h5")
    # Run Artificial Neural Network (ANN):

    def Neural_Network(self, save):
        self.scale_data()
        self.create_input_and_label()
        self.split_data()
        self.build_and_train_model()
        if save == True:
            self.save_model()
        # Example Input and Layer:
        print("\nScaled Input [EXP]:\n")
        print(self.train_input[0])
        print("\nScaled Label [EXP]:\n")
        print(self.train_label[0])


# Read data (Remote Weather Station.csv):
csv_path = os.getcwd()+"/Remote Weather Station.csv"
df = pd.read_csv(csv_path)

# Define a new class object named 'station':
station = Weather_Station(df)

# Visualize data:
# station.data_visualization()

# Artificial Neural Network (ANN):
station.Neural_Network(True)

# Enter inputs for making predictions:
