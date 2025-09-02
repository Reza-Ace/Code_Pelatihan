#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>

const char* ssid = "vivo Y22";
const char* password = "suprafit";
const char* serverName = "https://c42af65b81a4.ngrok-free.app/predict"; // tanpa spasi

const int micPin = 34;
const int motorPin = 33;

const int sampleRate = 16000;
const int durationSeconds = 1;
const int numSamples = sampleRate * durationSeconds;
int16_t samples[numSamples];

void setup() {
  Serial.begin(115200);
  delay(1000);

  pinMode(motorPin, OUTPUT);
  digitalWrite(motorPin, LOW);

  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(700);
  }
  Serial.println("\nWiFi connected");
}

void loop() {
  Serial.println("Merekam suara 1 detik...");
  for (int i = 0; i < numSamples; i++) {
    samples[i] = analogRead(micPin) - 2048; 
    delayMicroseconds(1000000 / sampleRate);
  }

  if (WiFi.status() == WL_CONNECTED) {
    WiFiClientSecure client;
    client.setInsecure(); 

    HTTPClient http;
    http.begin(client, serverName);
    http.addHeader("Content-Type", "application/octet-stream");

    int httpResponseCode = http.POST((uint8_t*)samples, numSamples * sizeof(int16_t));
    String response = http.getString();

    Serial.print("HTTP Response code: ");
    Serial.println(httpResponseCode);
    Serial.print("Respons server: ");
    Serial.println(response);

    if (response.indexOf("\"klakson\":true") >= 0) {
      Serial.println("🚨 Klakson terdeteksi! Getar motor...");
      digitalWrite(motorPin, HIGH);
      delay(300);
      digitalWrite(motorPin, LOW);
    }

    http.end();
  } else {
    Serial.println("WiFi tidak terhubung.");
  }

  delay(800);
}
