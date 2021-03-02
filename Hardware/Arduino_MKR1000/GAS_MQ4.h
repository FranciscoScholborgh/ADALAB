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


#ifndef GAS_MQ4_h
#define GAS_MQ4_h

#include <Arduino.h>

//namespace AnalogSensor {
class GAS_MQ4
{
  public:
    /**
     * Constructor
     */
    GAS_MQ4(int pin);
    
    /**
     * Returns the PPM concentration
     * Cambio del retorno de funcion de int a double
     */
    double read();

    /**
     * Calibrates the start point of 400
     */    
    double calibrate();

    /**
     * Returns the voltage
     */
    double getVoltage();
  private:
    int _pin;
};
//}
#endif
