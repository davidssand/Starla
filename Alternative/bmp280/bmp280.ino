//Programa: Temperatura, Pressao e Altitude com BMP280
//Autor: Arduino e Cia

#include <Wire.h>
#include <U8glib.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BMP280.h>

Adafruit_BMP280 sensor_bmp;

//Definicoes do display Oled
U8GLIB_SSD1306_128X64 u8g(U8G_I2C_OPT_FAST);

void draw()
{
  //Comandos graficos para o display devem ser colocados aqui
  u8g.setFont(u8g_font_8x13B);
  u8g.drawRFrame(0, 16, 128, 48, 4);
  u8g.drawRFrame(0, 0, 128, 16, 4);
  u8g.drawStr(40, 13, "BMP280");
  //Mostra a temperatura
  u8g.drawStr(10, 31, "Temp:      C");
  u8g.drawCircle(93, 22, 2); //Grau
  u8g.setPrintPos(55, 31);
  u8g.print(sensor_bmp.readTemperature(), 1);
  //Mostra a pressao (em hPa)
  u8g.drawStr(10, 45, "Pres:");
  u8g.setPrintPos(55, 45);
  u8g.print(sensor_bmp.readPressure(), 1);
  //Mostra a altitude
  u8g.drawStr(10, 59, "Alt :       m");
  u8g.setPrintPos(55, 59);
  u8g.print(sensor_bmp.readAltitude(1013.25));
}

void setup()
{
  Serial.begin(9600);
  Serial.println("Teste modulo BMP280");

  //Verifica a conexão do sensor BMP280
  if (!sensor_bmp.begin())
  {
    Serial.println("Sensor não encontrado. Verifique as conexoes!");
    while (1);
  }

  //Display Oled
  if ( u8g.getMode() == U8G_MODE_R3G3B2 ) {
    u8g.setColorIndex(255);     // white
  }
  else if ( u8g.getMode() == U8G_MODE_GRAY2BIT ) {
    u8g.setColorIndex(3);         // max intensity
  }
  else if ( u8g.getMode() == U8G_MODE_BW ) {
    u8g.setColorIndex(1);         // pixel on
  }
  else if ( u8g.getMode() == U8G_MODE_HICOLOR ) {
    u8g.setHiColorByRGB(255, 255, 255);
  }
}

void loop()
{
  //Chama a rotina de desenho na tela
  u8g.firstPage();
  do
  {
    draw();
  }
  while ( u8g.nextPage() );
  delay(10000);
}
