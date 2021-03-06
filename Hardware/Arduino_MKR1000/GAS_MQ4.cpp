/*MIT License

Copyright (c) 2017 Pavlo Ratushnyi

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

URL ORIGINAL SOURCE: https://github.com/paveldhq/lib-sensor-analog-mq4
*/


#include "GAS_MQ4.h"

//namespace AnalogSensor {
  GAS_MQ4::GAS_MQ4(int pin) {
    this->_pin = pin;
  }
  
  const float R0 = 11.820;
  const float m = -0.318;
  const float b = 1.133;

  const float VOLT_RESOLUTION = 3.3; // if 3.3v use 3.3 else 5.0 v
  //const int ADC_RESOLUTION = 10; // for 10bit analog to digital converter.
  const int ADCRESOLUTION = 10;

  const int retries = 4; //50 (original)
  const int retry_interval = 20;

  double GAS_MQ4::calibrate() {
      double sensor_volt = this->getVoltage(); //Define variable for sensor voltage
      double RS_air; //Define variable for sensor resistance
      double R0; //Define variable for R0

      RS_air = ((5.0 * 10.0) / sensor_volt) - 10.0; //Calculate RS in fresh air
      R0 = RS_air / 4.4; //Calculate R0

      return R0;
  }

  double GAS_MQ4::getVoltage() {
    double avg = 0.0;
    for (int i = 0; i < retries; i ++) {
      avg += analogRead(this->_pin) / retries;
      delay(retry_interval);
    }

    //double voltage = avg * VOLT_RESOLUTION / (pow(2, ADC_RESOLUTION) - 1);ADCRESOLUTION
    double voltage = avg * VOLT_RESOLUTION / (pow(2, ADCRESOLUTION) - 1);

    return voltage;
  }
    
    /**
     * Returns the PPM concentration
     * //cambios del returno de int a float
     */
    double GAS_MQ4::read() {
      double sensor_volt = this->getVoltage();
      double RS_gas; //Define variable for sensor resistance
      double ratio; //Define variable for ratio
  
      RS_gas = ((5.0 * 10.0) / sensor_volt) - 10.0; //Get value of RS in a gas
  
      ratio = RS_gas / R0;   // Get ratio RS_gas/RS_air

      double ppm_log = (log10(ratio) - b) / m; //Get ppm value in linear scale according to the the ratio value
      double ppm = pow(10, ppm_log); //Convert ppm value to log scale
      //return floor(ppm);
      return ppm;
  }
//}
