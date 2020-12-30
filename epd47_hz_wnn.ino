#include <Arduino.h>
#include <esp_task_wdt.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "epd_driver.h"
#include <Wire.h>
#include "RTClib.h"

/*
一.程序功能：
   lilygo-epd47 墨水屏简易万年历,显示时间日期
   用到了esp32的休眠节能功能，每分钟唤醒屏幕并刷新1次墨水屏,最小化使用电池电量，
   理论上平均电流在1ma, 一块普通的18640电池应可供电 60-90天上下(待验证!)
      
二.硬件：
1.lilygo-epd47 墨水屏(内置esp32) 
2.18640电池供电  
3.ds3231时钟模块，接线
       epd47   ds3231
       VCC     VCC
       GND     GND
       IO12    SDA
       IO13    SCL
     
三.软件环境:
1.Arduino 1.8.13   
2.引用库: 
    esp32 by Espressif Systems 1.04 esp32开发必备库
    LilyGo-EPD47 墨水屏驱动库 https://github.com/Xinyuan-LilyGO/LilyGo-EPD47
    RTClib 1.2.1 ds3231时钟模块库
3.调整i2c引脚 (因为lilygo-epd47 没有开放引脚21,22,所以将其改成开放的引脚12,13
  3.1打开文件
    C:\Users\***\AppData\Local\Arduino15\packages\esp32\hardware\esp32\1.0.4\variants\esp32\pins_arduino.h 
  3.2找到 SDA =21,  SCL = 22, 将定义的SDA,SCL 引脚分别改成12,13
        
4.烧写固件
  开发板选择: ESP32 Dev Module
  选择选择正确端口号后开始烧写固件 

四.说明
1.字库文件是自制的，
    已随源码做好，方法见目录/汉字库制作
2.关于时钟校时
    烧录一次RTClib库自带的例程文件ds3231，首次运行会自动校对ds3231硬件的时钟.
*/


//微软雅黑字体
#include "hzwnn_96.h"
#include "hzwnn_64.h"

RTC_DS3231 rtc;
int TIME_TO_SLEEP = 60; //下次唤醒间隔时间(秒）
#define uS_TO_S_FACTOR 1000000  /* Conversion factor for micro seconds to seconds */

String week_list[] = {"星期日", "星期一", "星期二", "星期三", "星期四", "星期五", "星期六"};

uint8_t *framebuffer;

void setup()
{
  Serial.begin(115200);
  // disable Core 0 WDT
  //TaskHandle_t idle_0 = xTaskGetIdleTaskHandleForCPU(0);
  // esp_task_wdt_delete(idle_0);

  if (! rtc.begin()) {
    Serial.println("Couldn't find RTC");
    while (1);
  }

  epd_init();

  framebuffer = (uint8_t *)heap_caps_malloc(EPD_WIDTH * EPD_HEIGHT / 2, MALLOC_CAP_SPIRAM);
  memset(framebuffer, 0xFF, EPD_WIDTH * EPD_HEIGHT / 2);


  showtime();

  esp_sleep_enable_timer_wakeup(TIME_TO_SLEEP * uS_TO_S_FACTOR);

  // ESP进入deepSleep状态
  //最大时间间隔为 4,294,967,295 µs 约合71分钟
  //休眠后，GPIP的高，低状态将失效，无法用GPIO控制开关
  esp_deep_sleep_start();

}

void loop()
{
}

void showtime()
{
  epd_poweron();
  volatile uint32_t t1 = millis();
  epd_clear();
  volatile uint32_t t2 = millis();
  printf("EPD clear took %dms.\n", t2 - t1);

  t1 = millis();

  DateTime now = rtc.now();

  String hh = String(now.hour());
  if (hh.length() < 2)
    hh = "0" + hh;

  String mm = String(now.minute());
  if (mm.length() < 2)
    mm = "0" + mm;
  String time_txt = hh + ":" + mm;
  //Serial.println("time_txt: " + String(time_txt));

  /*
    char *string1 = "12:13";
    char *string2 = "12月19日";
    char *string3 = "星期六";
  */

  epd_poweron();
  int cursor_x = 210; //字左
  int cursor_y = 180; //字底
  writeln((GFXfont *)&msyh96, (char *)time_txt.c_str(), &cursor_x, &cursor_y, NULL);

  String mon = String(now.month());
  if (mon.length() < 2)
    mon = "0" + mon;

  String dd = String(now.day());
  if (dd.length() < 2)
    dd = "0" + dd;
  time_txt = mon + "月" + dd+"日";

  cursor_x = 180;
  cursor_y = 340;
  writeln((GFXfont *)&msyh64, (char *)time_txt.c_str(), &cursor_x, &cursor_y, NULL);


  cursor_x = 270;
  cursor_y = 500;

  String week_str = week_list[now.dayOfTheWeek()];

  writeln((GFXfont *)&msyh64, (char *)week_str.c_str(), &cursor_x, &cursor_y, NULL);

  epd_poweroff();

  //epd_poweroff_all();

  t2 = millis();
  printf("EPD draw took %dms.\n", t2 - t1);

}
