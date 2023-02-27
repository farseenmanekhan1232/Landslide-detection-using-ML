/////////////////////////////////////////////
//    IoT Weather Station Predicting       //
//    Rainfall Intensity w/ TensorFlow     //
//         ------------------------        //
//           NodeMCU (ESP-12E)             //
//           by Kutluhan Aktar             //
//                                         //
/////////////////////////////////////////////

//
// Collates weather data on Google Sheets and interprets it with a neural network built in TensorFlow to make predictions on the rainfall intensity.
//
// For more information:
// https://www.theamplituhedron.com/projects/IoT_Weather_Station_Predicting_Rainfall_Intensity_with_TensorFlow
//
// Connections
// NodeMCU (ESP-12E) :
//                                Weather Station
// VV  --------------------------- 5V
// D5  --------------------------- RX
// D6  --------------------------- TX
// G   --------------------------- GND

// Include required libraries:
#include <ESP8266WiFi.h>
#include <WiFiClient.h>
#include <ESP8266WebServer.h>
#include <ESP8266HTTPClient.h>
#include <SoftwareSerial.h>

// Define your WiFi settings.
const char *ssid = "<SSID>";
const char *password = "<PASSWORD>";

// Define weather station settings:
char databuffer[35];
double temp;
int transferring = 0;

// Define the serial connection pins - RX and TX.
SoftwareSerial Serial_1(D6, D5); // (Rx, Tx)

void setup()
{
  // Wait until connected.
  delay(1000);
  // Initiate serial ports:
  Serial.begin(115200);
  Serial_1.begin(9600);
  // It is just for assuring if connection is alive.
  WiFi.mode(WIFI_OFF);
  delay(1000);
  // This mode allows NodeMCU to connect any WiFi directly.
  WiFi.mode(WIFI_STA);
  // Connect NodeMCU to your WiFi.
  WiFi.begin(ssid, password);

  Serial.print("\n\n");
  Serial.print("Try to connect to WiFi. Please wait! ");
  Serial.print("\n\n");
  // Halt the code until connected to WiFi.
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    Serial.print("*");
  }

  // If connection is successful:
  Serial.print("\n\n");
  Serial.print("-------------------------------------");
  Serial.print("\n\n");
  Serial.print("Connection is successful!");
  Serial.print("\n\n");
  Serial.print("Connected WiFi SSID : ");
  Serial.print(ssid);
  Serial.print("\n\n");
  Serial.println("Connected IPAddress : ");
  Serial.println(WiFi.localIP());
  Serial.print("\n\n");
}

void loop()
{
  // Get data from the remote weather station:
  getBuffer();
  // Debug the information and create the link:
  String weather_data = "wd=" + String(WindDirection()) + "&a_ws=" + String(WindSpeedAverage()) + "&m_ws=" + String(WindSpeedMax()) + "&1_rf=" + String(RainfallOneHour()) + "&24_rf=" + String(RainfallOneDay()) + "&tem=" + String(Temperature()) + "&hum=" + String(Humidity()) + "&b_pr=" + String(BarPressure());
  String server = "http://192.168.1.24/remote_weather_station/?";
  Serial.println("Weather Data => " + weather_data);
  Serial.println("Buffer => " + String(databuffer));
  // Send data packets every 5 minutes to Raspberry Pi (or any server).
  transferring++;
  Serial.println("Time => " + String(transferring) + "s / " + String(int(5 * 60)) + "s\n\n");
  if (transferring == 5 * 60)
  {
    // Create the HTTP object to make a request to the server.
    HTTPClient http;
    http.begin(server + weather_data);
    int httpCode = http.GET();
    String payload = http.getString();
    Serial.println("Data Send...\nHTTP Code => " + String(httpCode) + "\nServer Response => " + payload + "\n\n");
    http.end();
    transferring = 0;
  }
  // Wait 1 second...
  delay(1000);
}

// WEATHER STATION
void getBuffer()
{
  int index;
  for (index = 0; index < 35; index++)
  {
    if (Serial_1.available())
    {
      databuffer[index] = Serial_1.read();
      if (databuffer[0] != 'c')
      {
        index = -1;
      }
    }
    else
    {
      index--;
    }
  }
}

int transCharToInt(char *_buffer, int _start, int _stop)
{
  int _index;
  int result = 0;
  int num = _stop - _start + 1;
  int _temp[num];
  for (_index = _start; _index <= _stop; _index++)
  {
    _temp[_index - _start] = _buffer[_index] - '0';
    result = 10 * result + _temp[_index - _start];
  }
  return result;
}

int WindDirection() { return transCharToInt(databuffer, 1, 3); } // Wind Direction (deg)

float WindSpeedAverage()
{
  temp = 0.44704 * transCharToInt(databuffer, 5, 7);
  return temp;
} // Average Air Speed (1 minute)

float WindSpeedMax()
{
  temp = 0.44704 * transCharToInt(databuffer, 9, 11);
  return temp;
} // Max Air Speed (5 minutes)

float Temperature()
{
  temp = (transCharToInt(databuffer, 13, 15) - 32.00) * 5.00 / 9.00;
  return temp;
} // Temperature ("C")

float RainfallOneHour()
{
  temp = transCharToInt(databuffer, 17, 19) * 25.40 * 0.01;
  return temp;
} // Rainfall (1 hour)

float RainfallOneDay()
{
  temp = transCharToInt(databuffer, 21, 23) * 25.40 * 0.01;
  return temp;
} // Rainfall (24 hours)

int Humidity() { return transCharToInt(databuffer, 25, 26); } // Humidity (%)

float BarPressure()
{
  temp = transCharToInt(databuffer, 28, 32);
  return temp / 10.00;
} // Barometric Pressure (hPA)
