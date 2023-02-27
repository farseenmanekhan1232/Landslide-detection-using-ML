from tensorflow import keras
import os
import numpy as np

class_names = ['None', 'Light Rain',
               'Moderate Rain', 'Heavy Rain', 'Violent Rain']
model = keras.models.load_model(os.getcwd()+"/weather_station.h5")
pre_array = np.array([
    [0, 0, 0.31819805, 0.31819805, 0.6988, 0.81498571, 0.99349753],
    [0, -0, 0, -0, 0.8444, 1, 0.96835143],
    [0, 0, 0.45, 0, 0.87577, 0.95857143, 1.00128332],
    [-0, -0, -0, -0, 0.8224, 1.05714286, 0.99279368]
])
prediction = model.predict(pre_array)
for i in range(len(pre_array)):
    print("Prediction => ", class_names[np.argmax(prediction[i])])
