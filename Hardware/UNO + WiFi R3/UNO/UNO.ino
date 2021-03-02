#include <ArduinoJson.h>
#include <SoftwareSerial.h>
#include <OneWire.h> 
#include <DallasTemperature.h>
#include <MQUnifiedsensor.h>
#include <pt.h>
/************************Hardware Related Macros************************************/
#define         Board                   ("Arduino UNO")
#define         PinMQ4                     (A4)  //Analog input 4 of your arduino
#define         PinMQ135                   (A5)  //Analog input 5 of your arduino
/***********************Software Related Macros************************************/
#define         Type                    ("MQ-4") //MQ4
#define         Type2                   ("MQ-135") //MQ135
#define         Voltage_Resolution      (5)
#define         ADC_Bit_Resolution      (10) // For arduino UNO/MEGA/NANO
#define         RatioMQ4CleanAir        (4.4) //RS / R0 = 60 ppm 
#define         RatioMQ135CleanAir      (3.6)
/*****************************Globals***********************************************/

#define TdsSensorPin A3
#define VREF 5.0 // analog reference voltage(Volt) of the ADC
#define SCOUNT 30 // sum of sample point
int analogBuffer[SCOUNT]; // store the analog value in the array, read from ADC
int analogBufferTemp[SCOUNT];
int analogBufferIndex = 0,copyIndex = 0;
float averageVoltage = 0,tdsValue = 0,temperature = 25;

//Declare Sensor
MQUnifiedsensor MQ4(Board, Voltage_Resolution, ADC_Bit_Resolution, PinMQ4, Type);
MQUnifiedsensor MQ135(Board, Voltage_Resolution, ADC_Bit_Resolution, PinMQ135, Type2);

#define ONE_WIRE_BUS 4 
OneWire oneWire(ONE_WIRE_BUS); 
DallasTemperature sensors(&oneWire);

struct pt baseThread, tdsThread;

StaticJsonDocument<50> doc;

SoftwareSerial ss(2,3);
         
void setup() {
  // put your setup code here, to run once:
  //Serial.begin(115200);
  ss.begin(115200); 
  MQ4.setRegressionMethod(1); //_PPM =  a*ratio^b
  MQ135.setRegressionMethod(1);
  MQ4.setA(1012.7); MQ4.setB(-2.786); // Configurate the ecuation values to get CH4 concentration
  MQ135.setA(605.18); MQ135.setB(-3.937); // Configurate the ecuation values to get CO concentration
  //Serial.println("Dallas Temperature IC Control Library Demo"); 
  pinMode(TdsSensorPin,INPUT);
  sensors.begin(); 
  MQ4.init(); 
  float MQ4calcR0 = 0;
  float MQ135calcR0 = 0;
  for(int i = 1; i<=10; i ++) {
    MQ4.update(); // Update data, the arduino will be read the voltage on the analog pin
    MQ135.update(); // Update data, the arduino will be read the voltage on the analog pin
    MQ4calcR0 += MQ4.calibrate(RatioMQ4CleanAir);
    MQ135calcR0 += MQ135.calibrate(RatioMQ135CleanAir);
  }
  MQ4.setR0(MQ4calcR0/10);
  MQ135.setR0(MQ135calcR0/10);
  if(isinf(MQ4calcR0) || isinf(MQ135calcR0)) {ss.println("Warning: Conection issue founded, R0 is infite (Open circuit detected) please check your wiring and supply"); while(1);}
  if(MQ4calcR0 == 0 || MQ135calcR0 == 0){ss.println("Warning: Conection issue founded, R0 is zero (Analog pin with short circuit to ground) please check your wiring and supply"); while(1);}
  doc["temp"]["t1"] = 0.0;
  doc["temp"]["t2"] = 0.0;
  doc["ch4"] = 0.0;
  doc["co2"] = 0.0;
  doc["tds"] = 0.0;
  PT_INIT(&baseThread);
  PT_INIT(&tdsThread);
}

void readBasic(struct pt *pt){
  PT_BEGIN(pt);
  static long lastRead = 0 ;
  sensors.requestTemperatures(); // Send the command to get temperature readings 
  doc["temp"]["t1"] = sensors.getTempCByIndex(0);
  doc["temp"]["t2"] = sensors.getTempCByIndex(1);
  MQ4.update(); // Update data, the arduino will be read the voltage on the analog pin
  MQ135.update(); // Update data, the arduino will be read the voltage on the analog pin
  doc["ch4"] = MQ4.readSensor();
  doc["co2"] = MQ135.readSensor();
  lastRead = millis();
  PT_WAIT_UNTIL(pt, millis() - lastRead > 1000);
  //serializeJson(doc, Serial);
  serializeJson(doc, ss);
  PT_END(pt);
}

void readTDS(struct pt *pt){
  PT_BEGIN(pt);
  static unsigned long analogSampleTimepoint = millis();
  if(millis()-analogSampleTimepoint > 40U) {
    //every 40 milliseconds,read the analog value from the ADC
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

void loop() {
  // put your main code here, to run repeatedly:
  readBasic(&baseThread);
  readTDS(&tdsThread);
}

int getMedianNum(int bArray[], int iFilterLen) {
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
