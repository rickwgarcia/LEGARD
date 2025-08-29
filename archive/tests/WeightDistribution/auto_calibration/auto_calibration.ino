/*
  HX711 Four-Scale Automatic Calibrator
  
  This sketch guides the user to automatically calibrate four individual load cells
  connected to four SparkFun HX711 breakout boards sharing a single clock pin.

  Instructions:
  1. Upload the sketch and open the Serial Monitor at 9600 baud.
  2. Follow the on-screen prompts.
  3. You will first tare all scales (ensure they are empty).
  4. You will be asked to enter the weight of your known calibration object (e.g., 5.0).
  5. You will then be prompted to place the weight on each scale (A, B, C, D) one by one.
  6. The sketch will calculate and print the unique calibration factor for each scale.
  7. After calibration, the loop will continuously display the live weight from all four scales.

  Required library: HX711 by bogde (https://github.com/bogde/HX711)

  Hardware Connections:
    HX711 CLK (shared)   -> Arduino pin 6
    HX711 DOUT (Scale A) -> Arduino pin 7
    HX711 DOUT (Scale B) -> Arduino pin 8
    HX711 DOUT (Scale C) -> Arduino pin 9
    HX711 DOUT (Scale D) -> Arduino pin 10
    VCC (all boards)     -> Arduino 5V
    GND (all boards)     -> Arduino GND
*/

#include "HX711.h"

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


// This function performs the calibration steps for a single scale to keep the main code clean.
void calibrateScale(HX711 &scale, const char* scaleName, float known_weight) {
  Serial.print("Calibrating ");
  Serial.print(scaleName);
  Serial.println("...");
  delay(50); 

  long reading = scale.get_value(10);
  float calibration_factor = reading / known_weight;

 
  Serial.print(scaleName);
  Serial.print(" calibrated to factor ");
  Serial.println(calibration_factor);

  scale.set_scale(calibration_factor);
}


void setup() {
  Serial.begin(9600);
  Serial.println("HX711 Four-Scale Autocalibrator");

  // Initialize each scale
  scaleA.begin(DOUT_PINA, CLK_PIN);
  scaleB.begin(DOUT_PINB, CLK_PIN);
  scaleC.begin(DOUT_PINC, CLK_PIN);
  scaleD.begin(DOUT_PIND, CLK_PIN);

  Serial.println("Make sure all scales are empty. Taring in 3 seconds...");
  delay(3000);

  scaleA.tare();
  scaleB.tare();
  scaleC.tare();
  scaleD.tare();

  Serial.println("All scales have been tared.");
  Serial.println();

  Serial.println("Place known weight on scale. Enter the weight: ");
  while (Serial.available() <= 0) {
    delay(100);
  }
  float known_weight = Serial.parseFloat();
  while (Serial.available() > 0) {
    Serial.read();
  }
  Serial.print("Using a known weight of ");
  Serial.print(known_weight);
  Serial.println(" lbs");
  Serial.println();


  // --- Step 3: Calibrate each scale sequentially ---
  calibrateScale(scaleA, "Scale A", known_weight/4);
  calibrateScale(scaleB, "Scale B", known_weight/4);
  calibrateScale(scaleC, "Scale C", known_weight/4);
  calibrateScale(scaleD, "Scale D", known_weight/4);

  Serial.println("All scales have been calibrated!");
  Serial.println("Live readings will now be displayed.");
  Serial.println();
  Serial.println("Readings: A, B, C, D");
 
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
