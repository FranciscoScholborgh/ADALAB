/*
 * esp8266 simple WebSocket client
 * https://www.mischainti.org
 *
 * I use the ws://echo.websocket.org/ echo server
 * When you send a message to this server you receive
 * a response with the same message
 *
 */

#include <ArduinoJson.h> 
#include <SPI.h>
#include <WiFi101.h>
#include <WebSocketsClient.h>
 
WebSocketsClient webSocket;
 
const char *ssid     = "SSID";
const char *password = "CONTRASEÑA";

StaticJsonDocument<200> doc;
bool connected = false;
 
#define DEBUG_SERIAL Serial
 
void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
    switch(type) {
        case WStype_DISCONNECTED:
            DEBUG_SERIAL.print("[WSc] Disconnected!\n");
            connected = false;
            break;
        case WStype_CONNECTED: 
            DEBUG_SERIAL.print("[WSc] Connected to url: %s\n", payload);
            connected = true;
 
            // send message to server when Connected
            DEBUG_SERIAL.println("[WSc] SENT: Connected");
            webSocket.sendTXT("{\"device_id\":\"DEV000\"}");
            Serial.print("Available inputs: ");
            Serial.println(Serial.available());
        
            break;
        case WStype_TEXT:
            DEBUG_SERIAL.print("[WSc] RESPONSE: %s\n", payload);
            break;
        case WStype_BIN:
            DEBUG_SERIAL.print("[WSc] get binary length: %u\n", length);
            hexdump(payload, length);
            break;
                case WStype_PING:
                        // pong will be send automatically
                        DEBUG_SERIAL.print("[WSc] get ping\n");
                        break;
                case WStype_PONG:
                        // answer to a ping we send
                        DEBUG_SERIAL.print("[WSc] get pong\n");
                        break;
    }
 
}
 
void setup() {
    DEBUG_SERIAL.begin(115200);
 
//  DEBUG_SERIAL.setDebugOutput(true);
 
    DEBUG_SERIAL.println();
    DEBUG_SERIAL.println();
    DEBUG_SERIAL.println();
 
    for(uint8_t t = 4; t > 0; t--) {
        DEBUG_SERIAL.print("[SETUP] BOOT WAIT %d...\n", t);
        DEBUG_SERIAL.flush();
        delay(1000);
    }
 
    WiFi.begin(ssid, password);
 
    while ( WiFi.status() != WL_CONNECTED ) {
      delay ( 500 );
      Serial.print ( "." );
    }
    DEBUG_SERIAL.print("Local IP: "); DEBUG_SERIAL.println(WiFi.localIP());
    // server address, port and URL
    webSocket.begin("djangowstest.herokuapp.com", 80, "ws/device/DEV000/");
 
    // event handler
    webSocket.onEvent(webSocketEvent);
}
 
void loop() {
    webSocket.loop();
    if (connected && Serial.available()){
      String lectura = Serial.readString();
      String str_json;
      DeserializationError error = deserializeJson(doc, lectura);
      if (!error) {
        DEBUG_SERIAL.println("[WSc] SENT: Simple js client message!!");
        serializeJson(doc, str_json);
        webSocket.sendTXT(str_json);
      }
    }
}
