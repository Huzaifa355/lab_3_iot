#include <WiFi.h>
#include <HTTPClient.h>
#include <DHT.h>
#include <time.h>

// ====== WiFi Credentials ======
const char* ssid = "Huzaifa";
const char* password = "12345678";

// ====== Firebase Configuration ======
const String FIREBASE_HOST = "lab-11-iot-3ee05-default-rtdb.firebaseio.com";
const String FIREBASE_AUTH = "NmpdcOjSAdgGLoLvjJswiaHgcrLIBhnYaZTPPFb7";
const String FIREBASE_PATH = "/sensor_data_1348.json";

// ====== DHT Sensor Config ======
#define DHTPIN 4
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

// ====== Timing Config ======
const unsigned long SEND_INTERVAL = 10000;  // 10 seconds
const unsigned long SENSOR_DELAY = 2000;    // 2 seconds
unsigned long lastSendTime = 0;
unsigned long lastReadTime = 0;

// ====== NTP Time Config (Pakistan Time UTC+5) ======
const char* ntpServer1 = "pool.ntp.org";
const char* ntpServer2 = "time.nist.gov";
const char* ntpServer3 = "time.google.com";
const long gmtOffset_sec = 5 * 3600;
const int daylightOffset_sec = 0;

void setup() {
  Serial.begin(115200);
  Serial.println("\nESP32-S3 DHT11 Firebase Monitor");

  dht.begin();
  connectWiFi();

  // Configure NTP
  configTime(gmtOffset_sec, daylightOffset_sec, ntpServer1, ntpServer2, ntpServer3);
  waitForTimeSync();
  printLocalTime();
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    connectWiFi();
  }

  if (millis() - lastReadTime >= SENSOR_DELAY) {
    float temp, hum;
    if (readDHT(&temp, &hum)) {
      if (millis() - lastSendTime >= SEND_INTERVAL) {
        sendToFirebase(temp, hum);
        lastSendTime = millis();
      }
    }
    lastReadTime = millis();
  }
}

// ========== FUNCTIONS ==========

void connectWiFi() {
  Serial.print("Connecting to WiFi");
  WiFi.disconnect(true);
  WiFi.begin(ssid, password);

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✅ WiFi Connected!");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\n❌ WiFi Connection Failed!");
  }
}

bool readDHT(float* temp, float* hum) {
  *temp = dht.readTemperature();
  *hum = dht.readHumidity();

  if (isnan(*temp) || isnan(*hum)) {
    Serial.println("❌ DHT Read Failed");
    return false;
  }

  Serial.printf("🌡 Temp: %.1f°C | 💧 Humidity: %.1f%%\n", *temp, *hum);
  return true;
}

void waitForTimeSync() {
  struct tm timeinfo;
  int retry = 0;
  const int maxRetries = 10;

  while (!getLocalTime(&timeinfo) && retry < maxRetries) {
    Serial.print("⏳ Waiting for NTP sync...");
    delay(1000);
    retry++;
  }

  if (retry >= maxRetries) {
    Serial.println("\n❌ Time sync failed.");
  } else {
    Serial.println("\n✅ Time synchronized.");
  }
}

void printLocalTime() {
  struct tm timeinfo;
  if (!getLocalTime(&timeinfo)) {
    Serial.println("❌ Failed to obtain time");
    return;
  }
  Serial.println(&timeinfo, "Current Time: %Y-%m-%d %H:%M:%S");
}

void sendToFirebase(float temp, float hum) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("❌ Cannot send - WiFi disconnected");
    return;
  }

  struct tm timeinfo;
  if (!getLocalTime(&timeinfo)) {
    Serial.println("❌ Failed to get time");
    return;
  }

  char timeStr[30];
  strftime(timeStr, sizeof(timeStr), "%Y-%m-%d %H:%M:%S", &timeinfo);
  String timestamp = String(timeStr);

  String url = "https://" + FIREBASE_HOST + FIREBASE_PATH + "?auth=" + FIREBASE_AUTH;

  String jsonPayload = "{\"temperature\":" + String(temp) +
                       ",\"humidity\":" + String(hum) +
                       ",\"timestamp\":\"" + timestamp + "\"}";

  Serial.println("📤 Sending to Firebase:");
  Serial.println(jsonPayload);

  HTTPClient http;
  http.begin(url);
  http.addHeader("Content-Type", "application/json");

  int httpCode = http.POST(jsonPayload);
  if (httpCode == HTTP_CODE_OK || httpCode == HTTP_CODE_ACCEPTED) {
    Serial.println("✅ Firebase update successful");
  } else {
    Serial.printf("❌ Firebase Error: %d\n", httpCode);
  }

  http.end();
}
