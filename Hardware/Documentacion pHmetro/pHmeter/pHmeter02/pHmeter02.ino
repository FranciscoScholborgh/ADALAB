
//http://scidle.com/es/como-usar-un-sensor-de-ph-con-arduino/
//Calibracion
// volt   pH
//  3.95   4
//  3.29   7
//  2.9    10

// Compensacion de temperatura
// E = k - KT(pH)   (pendiente -KT)
// KT =2.3026.RT/F = 59.16 mV por unidad de pH a 25 °C
//K(mV/pH)        T (°C)
//54.20          0 °C
//64.00         50 °C
//66.10         60 °C
//74.04        100 °C


 long readVcc()
{
   ADMUX = _BV(REFS0) | _BV(MUX3) | _BV(MUX2) | _BV(MUX1);
   delay(2);
   ADCSRA |= _BV(ADSC);
   while (bit_is_set(ADCSRA, ADSC));
   
   long result = ADCL;
   result |= ADCH << 8;
   result = 1126400L / result; // Back-calculate AVcc in mV
   return result;
}
 
const int analogInPin_P0 = 0; 
const int analogInPin_D0 = 1;
const int analogInPin_T0 = 2;

int sensorValue = 0; 
unsigned long int avgValue; 
float b, tempValue, pHlmValue;
int buf[10], temp;
void setup() {
 Serial.begin(9600);
 //analogReference(INTERNAL);// pone como referencia iterna 1.1V
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

 float vcc = readVcc() / 1000.0;
 float pHVol=(float)avgValue*vcc/1024/6;
 float pHValue = -5.5911*pHVol + 25.898;

 float pHValue2 = (pHVol-3.95)*(10-4)/(2.9-3.95);
 
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
