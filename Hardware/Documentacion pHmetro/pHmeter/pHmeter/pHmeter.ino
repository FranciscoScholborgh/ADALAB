//https://www.arduinolibraries.info/libraries/p-h-probe-interface
//https://www.sparkyswidgets.com/portfolio-item/ph-probe-interface/
//http://scidle.com/es/como-usar-un-sensor-de-ph-con-arduino/
//Calibracion
// volt   pH
//  3.95   4
//  3.29   7
//  2.9    10
 
const int analogInPin_P0 = 0; 
const int analogInPin_D0 = 1;
const int analogInPin_T0 = 2;

int sensorValue = 0; 
unsigned long int avgValue; 
float b, tempValue, pHlmValue;
int buf[10], temp;
void setup() {
 Serial.begin(9600);
}
 
void loop() {
 for(int i=0;i<10;i++) 
 { 
  buf[i]    = analogRead(analogInPin_P0);
  pHlmValue = analogRead(analogInPin_D0);
  tempValue = analogRead(analogInPin_T0);
  delay(20);
 }
 for(int i=0;i<9;i++)
 {
  for(int j=i+1;j<10;j++)
  {
   if(buf[i]>buf[j])
   {
    temp=buf[i];
    buf[i]=buf[j];
    buf[j]=temp;
   }
  }
 }
 avgValue=0;

 
 for(int i=2;i<8;i++)
 avgValue+=buf[i];
 float pHVol=(float)avgValue*5.0/1024/6;
 float pHValue = -5.5911*pHVol + 25.898;
 
 Serial.print("sensor pH= ");
 Serial.println(pHValue);

 Serial.print("sensor Voltaje= ");
 Serial.println(pHVol);
 
 //Serial.print("Limite de pH= ");
 //Serial.println(pHlmValue);
 
 //Serial.print("Temp = ");
 //Serial.println(tempValue);
 
 delay(1000);
}
