# LilyGo-EPD47-ShowNowDay
LilyGo-EPD47 简易万年历显示-汉字
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
1.Arduino
1.8.13  

2.引用库:
    esp32 by Espressif Systems 1.04 esp32开发必备库

    LilyGo-EPD47 墨水屏驱动库 https://github.com/Xinyuan-LilyGO/LilyGo-EPD47

    RTClib 1.2.1 ds3231时钟模块库

3.调整i2c引脚
因为lilygo-epd47 没有开放引脚21,22,所以将其改成开放的引脚12,13

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
