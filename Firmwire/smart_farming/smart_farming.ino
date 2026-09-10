#include<Adafruit_Sensor.h>
#include<DHT.h>
#include<BH1750.h>
#include<WiFi.h>
#include<WebServer.h>
#include<Wire.h>
#include<LiquidCrystal_I2C.h>
#include<HTTPClient.h>
#include<WiFiClientSecure.h>



#define LED 2
#define DHTTYPE DHT11
#define DHTPIN 4
#define RAIN 13
#define MOIST 34

const char* wifi="DARK NETWORK";
const char* passwd="theboyz456";
const char* SERVER_URL="http://192.168.29.108:8000";
const char* POST_END_POINT="/sensor-data";
//const char* GET_END_POINT="";
unsigned long lastSend=0;

typedef struct SensorData{
  float humidity;
  float temperature;
  float lux;
  int moisture;
  bool rain;
}SensorData;

class Sensors{
  private:
    DHT dht;
    BH1750 lightSensor;
    const int dry=4090;
    const int wet=1380;
    int avgCount=0;
    float humiditySum=0;
    float tempSum=0;
    float luxSum=0;
    float moistureSum=0;
  public:
    Sensors(): dht(DHTPIN,DHTTYPE){}

    void begin(){
      dht.begin();
      pinMode(RAIN,INPUT);
      Wire.begin(21,22);
      lightSensor.begin();
    }
    float getTemperature(){
        float value = dht.readTemperature();
        if (isnan(value)) {
            Serial.println("DHT temperature error");
            return NAN;
        }
        return value;
    }
    float getHumidity(){
        float value = dht.readHumidity();
        if (isnan(value)){
            Serial.println("DHT humidity error");
            return NAN;
        }
        return value;
    }
    int getMoisture(){
        int raw = analogRead(MOIST);
        int percentage = map(raw,dry,wet,0,100);
        percentage = constrain(percentage,0,100);
        return percentage;
    }
    bool isRaining(){
        int value = digitalRead(RAIN);
        return value == HIGH;
    }
    float getLight(){
        float lux = lightSensor.readLightLevel();
        if (isnan(lux)) {
            Serial.println("BH1750 reading error");
            return NAN;
        }
        return lux;
    }

    SensorData readSensors(){
      SensorData data;
      data.temperature=getTemperature();
      data.humidity = getHumidity();
      data.moisture = getMoisture();
      data.rain = isRaining();
      data.lux = getLight();
      if(!isnan(data.temperature)) tempSum+=data.temperature;
      if(!isnan(data.humidity)) humiditySum+=data.humidity;
      if(!isnan(data.lux)) luxSum+=data.lux;
      moistureSum += data.moisture;
      avgCount++;
      return data;
    }   
    SensorData avgReading(){
        SensorData avg;
        if(avgCount==0) return avg;
        avg.temperature = tempSum / avgCount;
        tempSum=0;
        avg.humidity = humiditySum / avgCount;
        humiditySum=0;
        avg.moisture = moistureSum / avgCount;
        moistureSum=0;
        avg.lux = luxSum / avgCount;
        luxSum=0;
        avgCount=0;
        return avg;
    }
    int getAvgCount(){
        return avgCount;
    }
};
class DisplayManager{
private:
    LiquidCrystal_I2C lcd;
public:
    DisplayManager() : lcd(0x27, 16, 2) {}
    void begin(){
        lcd.init();
        lcd.backlight();
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("Smart Farming");
        lcd.setCursor(0, 1);
        lcd.print("Starting...");
        delay(500);
        lcd.clear();
    }
    void showTemperatureHumidity(SensorData data){
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.printf("Temp: %.2f%cC",data.temperature,223);
        lcd.setCursor(0, 1);
        lcd.printf("Humidity: %.2f%%",data.humidity);
        delay(1000);
    }
    void showMoisture(SensorData data){
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("Soil Moisture");
        lcd.setCursor(0, 1);
        lcd.printf("%d%%",data.moisture);
        delay(1000);
    }
    void showRain(SensorData data){
        lcd.clear();
        lcd.setCursor(0, 0);
        if (data.rain)lcd.print("Raining: Yes");
        else lcd.print("Raining: No");
        delay(1000);
    }
    void showLight(SensorData data){
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("Light:");
        lcd.setCursor(0, 1);
        lcd.printf("%.2f lux",data.lux);
        delay(1000);
    }
};

class WiFiManagerCustom{
public:
    void connect(){
        WiFi.begin(wifi, passwd);
        Serial.print("Connecting to WiFi");
        while (WiFi.status() != WL_CONNECTED){
            delay(500);
            Serial.print(".");
        }
        Serial.println();
        Serial.println("WiFi connected");
        Serial.print("ESP32 IP: ");
        Serial.println(WiFi.localIP());
    }
};

class WebManager {
private:
    WebServer& server;
    SensorData& sensorData;

public:
    WebManager(WebServer& webServer, SensorData& data)
        : server(webServer), sensorData(data) {}

    void begin() {
        server.on("/", [this]() {
            handleHome();
        });

        server.on("/data", [this]() {
            handleData();
        });

        server.begin();
        Serial.println("Web server started");
    }

    void handleClient() {
        server.handleClient();
    }

private:
    void handleHome() {
        String html = R"rawliteral(
                      <!DOCTYPE html>
                      <html>
                      <head>
                      <meta name="viewport" content="width=device-width, initial-scale=1">
                      <title>ESP32 Smart Farming</title>

                      <style>
                      * {
                          box-sizing: border-box;
                      }

                      body {
                          margin: 0;
                          font-family: Arial;
                          min-height: 100vh;
                          display: flex;
                          justify-content: center;
                          align-items: center;
                          background: linear-gradient(135deg, #0f172a, #1e293b);
                          color: white;
                      }

                      .container {
                          width: 90%;
                          max-width: 800px;
                          text-align: center;
                      }

                      h1 {
                          font-size: 35px;
                      }

                      .status {
                          color: #4ade80;
                          margin-bottom: 30px;
                      }

                      .cards {
                          display: grid;
                          grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
                          gap: 20px;
                      }

                      .card {
                          background: rgba(255, 255, 255, 0.1);
                          padding: 30px;
                          border-radius: 20px;
                          box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                      }

                      .label {
                          margin-top: 10px;
                          font-size: 16px;
                          color: #cbd5e1;
                      }

                      .value {
                          font-size: 30px;
                          font-weight: bold;
                          margin-top: 10px;
                      }
                      </style>
                      </head>

                      <body>
                      <div class="container">
                          <h1>ESP32 Smart Farming</h1>

                          <div class="status">
                              LIVE SENSOR DATA
                          </div>

                          <div class="cards">
                              <div class="card">
                                  <div class="label">Temperature</div>
                                  <div class="value" id="temp">--</div>
                              </div>

                              <div class="card">
                                  <div class="label">Humidity</div>
                                  <div class="value" id="humi">--</div>
                              </div>

                              <div class="card">
                                  <div class="label">Soil Moisture</div>
                                  <div class="value" id="mois">--</div>
                              </div>

                              <div class="card">
                                  <div class="label">Rain</div>
                                  <div class="value" id="rain">--</div>
                              </div>

                              <div class="card">
                                  <div class="label">Light</div>
                                  <div class="value" id="lux">--</div>
                              </div>
                          </div>
                      </div>

                      <script>
                      function updateData() {
                          fetch("/data")
                              .then(response => response.json())
                              .then(data => {
                                  document.getElementById("temp").innerHTML =
                                      data.temperature + " °C";

                                  document.getElementById("humi").innerHTML =
                                      data.humidity + " %";

                                  document.getElementById("mois").innerHTML =
                                      data.moisture + " %";

                                  document.getElementById("rain").innerHTML =
                                      data.rain;

                                  document.getElementById("lux").innerHTML =
                                      data.lux + " lux";
                              })
                              .catch(error => {
                                  console.log("Error:", error);
                              });
                      }

                      setInterval(updateData, 1500);
                      updateData();
                      </script>
                      </body>
                      </html>
                      )rawliteral";
        server.send(200, "text/html", html);
    }
    void handleData() {
        String json = "{";
        json += "\"temperature\":";
        json += String(sensorData.temperature, 2);
        json += ",\"humidity\":";
        json += String(sensorData.humidity, 2);
        json += ",\"moisture\":";
        json += String(sensorData.moisture);
        json += ",\"lux\":";
        json += String(sensorData.lux, 2);
        json += ",\"rain\":\"";
        if (sensorData.rain) {
            json += "Raining";
        } else {
            json += "Not raining";
        }
        json += "\"}";
        server.send(200, "application/json", json);
    }
};

class BackendClient{
    public:
    bool sendData(SensorData sendSensorData) {
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("WiFi not connected...");
        return false;
    }

    WiFiClient client;
    HTTPClient http;

    String url = String(SERVER_URL) + POST_END_POINT;

    Serial.printf("Sending POST request: %s\n", url.c_str());

    if (!http.begin(client, url)) {
        Serial.println("Connection failed...");
        return false;
    }

    String reqBody = "{";
    reqBody += "\"device_id\":\"esp32-1\",";
    reqBody += "\"temp\":" + String(sendSensorData.temperature, 2) + ",";
    reqBody += "\"humidity\":" + String(sendSensorData.humidity, 2) + ",";
    reqBody += "\"moisture\":" + String(sendSensorData.moisture) + ",";
    reqBody += "\"ambidientLight\":" + String(sendSensorData.lux); 
    reqBody += "}";

    http.addHeader("Content-Type", "application/json");

    Serial.println("Sending: " + reqBody);

    int httpCode = http.POST(reqBody);

    if (httpCode > 0) {
        Serial.printf("HTTP Response Code: %d\n", httpCode);
        String response = http.getString();
        Serial.println("Server Response: " + response);
        http.end();
        return true;
    }

    Serial.println("POST error:");
    Serial.println(http.errorToString(httpCode));

    http.end();
    return false;
    }
};
Sensors sensors;
DisplayManager display;
WiFiManagerCustom wifiManager;
SensorData data;
WebServer server(80);
WebManager web(server, data);
BackendClient backend;

void setup() {
    Serial.begin(115200);
    pinMode(LED, OUTPUT);
    sensors.begin(); 
    display.begin();
    wifiManager.connect();
    web.begin();
}

void loop() {
    data = sensors.readSensors();
    digitalWrite(LED, HIGH);
    web.handleClient();
    Serial.println("----------------");
    Serial.printf("Temperature: %.2f C\n", data.temperature);
    Serial.printf("Humidity: %.2f %%\n", data.humidity);
    Serial.printf("Soil Moisture: %d %%\n", data.moisture);
    Serial.printf("Light: %.2f lux\n", data.lux);
    if (data.rain)Serial.println("Rain: YES");
    else Serial.println("Rain: NO");
    Serial.println("----------------");
    display.showTemperatureHumidity(data);
    display.showMoisture(data);
    display.showRain(data);
    display.showLight(data);
    digitalWrite(LED, LOW);
    delay(100);
    if(millis()-lastSend>=5000){
        lastSend=millis();
        if(sensors.getAvgCount()>0){
            SensorData avgData=sensors.avgReading();
            backend.sendData(avgData);
        }
        delay(250);
        //String prediction;
        //backend.getData(prediction);
    }
}

