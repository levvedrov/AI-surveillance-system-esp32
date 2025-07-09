#include "esp_camera.h"
#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <vector>

#define CAMERA_MODEL_AI_THINKER

const char* ssid = "FiberNet_45";
const char* password = "Levyshka2014";
const char* server = "http://192.168.50.226:5000/snap"; // use your server IP

std::vector<String> servers = { "192.168.50.226:5000" , "192.168.50.191:5000"}; // use your servers' IP


void connectWiFi(const char*, const char*);

void setup() {

  Serial.begin(115200);
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer   = LEDC_TIMER_0;
  config.pin_d0 = 5;
  config.pin_d1 = 18;
  config.pin_d2 = 19;
  config.pin_d3 = 21;
  config.pin_d4 = 36;
  config.pin_d5 = 39;
  config.pin_d6 = 34;
  config.pin_d7 = 35;
  config.pin_xclk = 0;
  config.pin_pclk = 22;
  config.pin_vsync = 25;
  config.pin_href = 23;
  config.pin_sccb_sda = 26;
  config.pin_sccb_scl = 27;
  config.pin_pwdn = 32;
  config.pin_reset = -1;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  config.frame_size   = FRAMESIZE_QVGA;
  config.jpeg_quality = 10;
  config.fb_count     = 1;

  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    return;
  }
  Serial.println("Camera initialized successfully");
  
  connectWiFi(ssid, password);
} 


void connectWiFi(const char* id, const char* pas){
  WiFi.begin(id, pas);
  Serial.printf("Connecting to %s\n", id);
  for (int attempt = 0 ; WiFi.status() != WL_CONNECTED && attempt<20 ; attempt++){
    delay(500);
    Serial.print(". ");
  }

  Serial.println();
  if (WiFi.status() != WL_CONNECTED){
    Serial.println("Connection Failed!");
  }
  else{
    Serial.println("Connected!");
  }
}

int camsnap(){
  camera_fb_t* frame = esp_camera_fb_get();
  if (!frame){ Serial.println("[ ! ] Capture failed"); return 1;}
  else {
    Serial.println("Frame captured..."); 
    Serial.printf(" - Size: %d bytes \n", frame->len); 
    Serial.printf(" - Ressolution: %dx%d \n", frame->width, frame->height); 
  }

  
  for (unsigned int index=0; index < servers.size(); index++){
    
    HTTPClient http;
    http.begin("http://"+servers[index]+"/snap");
    http.addHeader("Content-Type", "image/jpeg");
    int postStatus = http.POST(frame->buf, frame->len);

    if (postStatus > 0) { Serial.printf("[ > ] -------> Sent to %s. Response: %d\n", servers[index].c_str(), postStatus); }
    else { Serial.printf("[ ! ] -------X %s Error: %s\n", servers[index].c_str(), http.errorToString(postStatus).c_str()); }
    http.end();
  }
  Serial.println();
  
  

  esp_camera_fb_return(frame);
  delay(100);
  return 0;
}
void loop() {
  camsnap();

}

