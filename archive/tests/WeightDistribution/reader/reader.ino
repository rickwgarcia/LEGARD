/*
  HX711 Four-Scale Load Cell Reader
  Adapted for reading four individual load cells using SparkFun HX711 breakout boards.
  
  This sketch initializes and reads data from four load cells connected to four HX711 boards.
  It assumes each load cell has been independently calibrated using the HX711 calibration sketch.

  Required library: HX711 by bogde (https://github.com/bogde/HX711)

  Hardware connections:
    HX711 CLK (shared)  -> Arduino pin 8
    HX711 DOUT (Scale A) -> Arduino pin 9
    HX711 DOUT (Scale B) -> Arduino pin 10
    HX711 DOUT (Scale C) -> Arduino pin 11
    HX711 DOUT (Scale D) -> Arduino pin 12
    VCC  -> Arduino 5V
    GND  -> Arduino GND

  Note:
  - Each load cell must be individually calibrated to determine its unique calibration factor.
  - This sketch assumes the load cells are tared (zeroed) at startup with no weight applied.
*/

#include "HX711.h"

// Calibration factors determined from separate calibration for each load cell
#define CALIBRATION_FACTOR_A -20730   // Replace with actual calibrated value for Scale A
#define CALIBRATION_FACTOR_B -20730   // Replace with actual calibrated value for Scale B
#define CALIBRATION_FACTOR_C -20730   // Replace with actual calibrated value for Scale C
#define CALIBRATION_FACTOR_D -20730   // Replace with actual calibrated value for Scale D

// Define pins: one shared clock pin, four individual data pins
#define CLK_PIN   6
#define DOUT_PINA 7
#define DOUT_PINB 8
#define DOUT_PINC 9
#define DOUT_PIND 10

// Create HX711 instances for each load cell
HX711 scaleA;
HX711 scaleB;
HX711 scaleC;
HX711 scaleD;


void setup() {
  Serial.begin(9600);
  Serial.println("HX711 Four Scale Demo");

  // Initialize each scale
  scaleA.begin(DOUT_PINA, CLK_PIN);
  scaleB.begin(DOUT_PINB, CLK_PIN);
  scaleC.begin(DOUT_PINC, CLK_PIN);
  scaleD.begin(DOUT_PIND, CLK_PIN);

  // Set the calibration factor for each scale
  scaleA.set_scale(CALIBRATION_FACTOR_A);
  scaleB.set_scale(CALIBRATION_FACTOR_B);
  scaleC.set_scale(CALIBRATION_FACTOR_C);
  scaleD.set_scale(CALIBRATION_FACTOR_D);

  // Tare each scale (assuming there is no weight on the scales at startup)
  Serial.println("Taring scales... Please wait.");
  scaleA.tare();
  scaleB.tare();
  scaleC.tare();
  scaleD.tare();
  Serial.println("Scales tared. Readings:");
}

void loop() {
  // Print the readings from all four scales in a comma-separated format
  Serial.print(scaleA.get_units(), 1);
  Serial.print(",");
  Serial.print(scaleB.get_units(), 1);
  Serial.print(",");
  Serial.print(scaleC.get_units(), 1);
  Serial.print(",");
  Serial.println(scaleD.get_units(), 1);

  delay(50); // Delay to avoid overwhelming the Serial Monitor
}
