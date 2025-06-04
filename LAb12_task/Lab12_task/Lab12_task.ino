// DHT11 + TensorFlow Lite on ESP32-S3 using PSRAM

#include <Arduino.h>
#include <DHT.h>
#include <WiFi.h>
#include <esp_heap_caps.h>

// TensorFlow Lite Micro
#include "tensorflow/lite/micro/micro_interpreter.h"
#include "tensorflow/lite/micro/micro_mutable_op_resolver.h"
#include "tensorflow/lite/schema/schema_generated.h"
#include "tensorflow/lite/micro/micro_log.h"

#include "model_data.h" // Your converted .h model file

#define DHTPIN 4
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

constexpr int kTensorArenaSize = 40 * 1024;
uint8_t* tensor_arena;

const tflite::Model* model = nullptr;
tflite::MicroInterpreter* interpreter = nullptr;

// Operation resolver for model-specific ops (3 layers + activations)
static tflite::MicroMutableOpResolver<3> resolver;

void setup() {
    Serial.begin(115200);
    dht.begin();

    // Initialize PSRAM
    if (!psramInit()) {
        Serial.println("PSRAM initialization failed!");
        while(1);
    }

    // Load model
    model = tflite::GetModel(model_tflite);
    if (model->version() != TFLITE_SCHEMA_VERSION) {
        Serial.println("Model version mismatch!");
        while(1);
    }

    // Allocate PSRAM for tensor arena
    tensor_arena = (uint8_t*)ps_malloc(kTensorArenaSize);
    if (!tensor_arena) {
        Serial.println("Failed to allocate tensor arena in PSRAM!");
        while(1);
    }

    // Add model operations (matches your architecture)
    resolver.AddFullyConnected();  // For all dense layers
    resolver.AddRelu();            // For hidden layer activations
    resolver.AddSoftmax();         // For output layer

    // Initialize interpreter
    static tflite::MicroInterpreter static_interpreter(
        model, 
        resolver,
        tensor_arena,
        kTensorArenaSize
    );
    
    interpreter = &static_interpreter;

    if (interpreter->AllocateTensors() != kTfLiteOk) {
        Serial.println("Tensor allocation failed");
        while(1);
    }

    Serial.println("Setup complete. Starting inference...");
}

void loop() {
    float temperature = dht.readTemperature();
    float humidity = dht.readHumidity();

    if (isnan(temperature) || isnan(humidity)) {
        Serial.println("Failed to read from DHT sensor!");
        delay(2000);
        return;
    }

    // Get input tensor (shape [1, 2])
    TfLiteTensor* input = interpreter->input(0);
    input->data.f[0] = temperature;
    input->data.f[1] = humidity;

    // Run inference
    if (interpreter->Invoke() != kTfLiteOk) {
        Serial.println("Inference failed");
        return;
    }

    // Get output tensor (shape [1, 3])
    TfLiteTensor* output = interpreter->output(0);
    
    // Print results (assuming classification with 3 classes)
    Serial.print("Temperature: ");
    Serial.print(temperature);
    Serial.print("C, Humidity: ");
    Serial.print(humidity);
    Serial.print("%, Predictions: ");
    Serial.print("Cold: ");
    Serial.print(output->data.f[0]);
    Serial.print(", Comfort: ");
    Serial.print(output->data.f[1]);
    Serial.print(", Hot: ");
    Serial.println(output->data.f[2]);

    delay(5000);
}