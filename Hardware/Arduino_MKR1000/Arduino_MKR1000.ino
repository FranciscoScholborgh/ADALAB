#include <ArduinoJson.h>
#include <pt.h>
#include <OneWire.h> 
#include <DallasTemperature.h>
#include <SPI.h>
#include <WiFi101.h>
#include <WebSocketClient.h>
#include "MQ135.h"
#include "GAS_MQ4.h"

//static struct pt pt1;

// Here we define a maximum framelength to 64 bytes. Default is 256.
#define MAX_FRAME_LENGTH 64

// Define how many callback functions you have. Default is 1.
#define CALLBACK_FUNCTIONS 1

WiFiClient client;
WebSocketClient webSocketClient;

static struct pt baseThread, MQ4Thread ,tdsThread;

int status = WL_IDLE_STATUS;
char ssid[] = "SSID";
char pass[] = "CONTRASEÑA";

StaticJsonDocument<200> doc;

#define ONE_WIRE_BUS 0
OneWire oneWire(ONE_WIRE_BUS); 
DallasTemperature temp_sensors(&oneWire);

#define TdsSensorPin A6
#define VREF 3.3 // analog reference voltage(Volt) of the ADC
#define SCOUNT 30 // sum of sample point
int analogBuffer[SCOUNT]; // store the analog value in the array, read from ADC
int analogBufferTemp[SCOUNT];
int analogBufferIndex = 0,copyIndex = 0;
float averageVoltage = 0,tdsValue = 0,temperature = 25;

MQ135 MQ135_sensor = MQ135(A5);
GAS_MQ4 MQ4_sensor = GAS_MQ4(A4);

void printWiFiStatus() {
  // print the SSID of the network you're attached to:
  Serial.print("SSID: ");
  Serial.println(WiFi.SSID());

  // print your WiFi shield's IP address:
  IPAddress ip = WiFi.localIP();
  Serial.print("IP Address: ");
  Serial.println(ip);

  // print the received signal strength:
  long rssi = WiFi.RSSI();
  Serial.print("signal strength (RSSI):");
  Serial.print(rssi);
  Serial.println(" dBm");
}

void read_sensors() {
  temp_sensors.requestTemperatures(); // Send the command to get temperature readings 
  doc["temp"]["t1"] = temp_sensors.getTempCByIndex(0);
  doc["temp"]["t2"] = temp_sensors.getTempCByIndex(1);
  doc["temperatura"] = temp_sensors.getTempCByIndex(0);
  doc["co2"] = MQ135_sensor.getPPM();
}

void read_MQ4() {
   MQ4_sensor.calibrate();
   doc["ch4"] = MQ4_sensor.read();
}

static int main_thread(struct pt *pt) {
  static unsigned long lastRead = 0;
  PT_BEGIN(pt);
  while(1) {
    lastRead = millis();
    if (client.connected()) {
      String data;
      webSocketClient.getData(data);
      
      if (data.length() > 0) {
        Serial.print("Received data: ");
        Serial.println(data);
      }
  
      read_sensors();
      //doc["ch4"] = 0.0;
      //doc["tds"] = 0.0;
      String str_json;
      serializeJson(doc, str_json);
      Serial.println("Sending data: " + str_json);
      webSocketClient.sendData(str_json);
   } else {
      Serial.println("Client disconnected.");
      /*while (1) {
        // Hang on disconnect.
      }*/
   }
    PT_WAIT_UNTIL(pt, millis() - lastRead > 1000);
  }
  PT_END(pt);
}

static int MQ4_thread(struct pt *pt) {
  static unsigned long lastRead = 0;
  PT_BEGIN(pt);
  read_MQ4();
  PT_END(pt);
}

static int readTDS(struct pt *pt){
  PT_BEGIN(pt);
  static unsigned long analogSampleTimepoint = millis();
  if(millis()-analogSampleTimepoint > 40U) { //every 40 milliseconds,read the analog value from the ADC
    analogSampleTimepoint = millis();
    analogBuffer[analogBufferIndex] = analogRead(TdsSensorPin); //read the analog value and store into the buffer
    analogBufferIndex++;
    if(analogBufferIndex == SCOUNT)
    analogBufferIndex = 0;
  }
  static unsigned long printTimepoint = millis();
  if(millis()-printTimepoint > 800U) {
    printTimepoint = millis();
    for(copyIndex=0;copyIndex<SCOUNT;copyIndex++)
    analogBufferTemp[copyIndex]= analogBuffer[copyIndex];
    averageVoltage = getMedianNum(analogBufferTemp,SCOUNT) * (float)VREF/ 1024.0; // read the analog value more stable by the median filtering algorithm, and convert to voltage value
    float compensationCoefficient=1.0+0.02*(temperature-25.0); //temperature compensation formula: fFinalResult(25^C) = fFinalResult(current)/(1.0+0.02*(fTP-25.0));
    float compensationVolatge=averageVoltage/compensationCoefficient; //temperature compensation
    tdsValue=(133.42*compensationVolatge*compensationVolatge*compensationVolatge - 255.86*compensationVolatge*compensationVolatge + 857.39*compensationVolatge)*0.5; //convert voltage value to tds value
    doc["tds"] = tdsValue;
  }
  PT_END(pt);
}

void setup() {
  
  Serial.begin(115200);

  // check for the presence of the shield:
  if (WiFi.status() == WL_NO_SHIELD) {
    Serial.println("WiFi shield not present");
    // don't continue:
    while (true);
  }

  // attempt to connect to WiFi network:
  while (status != WL_CONNECTED) {
    Serial.print("Attempting to connect to SSID: ");
    Serial.println(ssid);
    // Connect to WPA/WPA2 network. Change this line if using open or WEP network:
    status = WiFi.begin(ssid, pass);

    // wait 10 seconds for connection:
    delay(1000);
  }
  Serial.println("Connected to wifi");
  printWiFiStatus();
  
  // This delay is needed to let the WiFly respond properly
  delay(100);

  // Connect to the websocket server
  if (client.connect("djangowstest.herokuapp.com", 80)) {
    Serial.println("Connected");
    
  } else {
    Serial.println("Connection failed.");
    while(1) {
      // Hang on failure
    }
  }

  // Handshake with the server
  webSocketClient.path = "ws/device/DEV000/";
  webSocketClient.host = "djangowstest.herokuapp.com";

  if (webSocketClient.handshake(client)) {
    Serial.println("Handshake successful");
    webSocketClient.sendData("{\"device_id\":\"DEV000\"}");
    read_MQ4();
    read_sensors();    

    Serial.print("Available inputs: ");
    Serial.println(Serial.available());
  } else {
    Serial.println("Handshake failed.");
    while(1) {
      // Hang on failure
    }
  }
  PT_INIT(&baseThread);
  PT_INIT(&tdsThread);
  PT_INIT(&MQ4Thread);
}

void loop() {
  MQ4_thread(&MQ4Thread);
  readTDS(&tdsThread);
  main_thread(&baseThread);
}

int getMedianNum(int bArray[], int iFilterLen){
  int bTab[iFilterLen];
  for (byte i = 0; i<iFilterLen; i++)
    bTab[i] = bArray[i];
  int i, j, bTemp;
  for (j = 0; j < iFilterLen - 1; j++) {
    for (i = 0; i < iFilterLen - j - 1; i++) {
      if (bTab[i] > bTab[i + 1]) {
        bTemp = bTab[i];
        bTab[i] = bTab[i + 1];
        bTab[i + 1] = bTemp;
      }
    }
  }
  if ((iFilterLen & 1) > 0)
    bTemp = bTab[(iFilterLen - 1) / 2];
  else
    bTemp = (bTab[iFilterLen / 2] + bTab[iFilterLen / 2 - 1]) / 2;
  return bTemp;
}
