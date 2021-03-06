# LilyGo-EPD47-ShowNowDay <br/>
LilyGo-EPD47 简易万年历显示-汉字 <br/>
<b>一.程序功能：</b> <br/>
   lilygo-epd47 墨水屏简易万年历,显示时间日期

   用到了esp32的休眠节能功能，每分钟唤醒屏幕并刷新1次墨水屏,最小化使用电池电量，

   理论上平均电流在1ma, 一块普通的18640电池应可供电 60-90天上下(待验证! ) <br/>
   经证实想错了!<br/>
   注:实际使用后,发现电流达不到1ma,实际是80ma, 如果要达到1ma,需要在休眠前调用epd_poweroff_all, 但是如果调用epd_poweroff_all后, esp32会断开全部引脚的供电, 待唤醒后时钟模块会清零. ds3231可以不供电的, 我不太了解原因, 可能是esp32休眠导致了ds3231短路清零导致吧.如有高手, 可以给我指点下.<br/>
   
   所以虽然使用了ESP32休眠,并达到一定程度的省电, 但此程序更适合有充足电量供应的场景. <br/>
    
 <img src= 'https://github.com/lixy123/LilyGo-EPD47-ShowNowDay/blob/main/ink_day.jpg?raw=true' />
<b>二.硬件：</b>  <br/>
1.lilygo-epd47 墨水屏(内置esp32)

2.18640电池供电 

3.ds3231时钟模块，接线

       epd47   ds3231

       VCC     VCC

       GND     GND

       IO12    SDA

       IO13    SCL 

    

<b>三.软件环境:</b>  <br/>
1.Arduino <br/>
   1.8.13   <br/>

2.引用库: <br/>
    2.1 esp32 by Espressif Systems 1.04 esp32开发必备库 <br/>
    2.2 LilyGo-EPD47 墨水屏驱动库 https://github.com/Xinyuan-LilyGO/LilyGo-EPD47
    2.3 RTClib 1.2.1 ds3231时钟模块库 <br/>

3.调整i2c引脚 <br/>
  因为lilygo-epd47 没有开放引脚21,22, 所以要修改esp32的库文件将原I2C引脚改成模块开放出的引脚12,13 <br/>

  3.1打开文件 <br/>

    C:\Users\***\AppData\Local\Arduino15\packages\esp32\hardware\esp32\1.0.4\variants\esp32\pins_arduino.h

  3.2找到 SDA =21,  SCL = 22, 将定义的SDA,SCL 引脚分别改成12,13 <br/>

       

4.烧写固件 <br/>
  开发板选择: ESP32 Dev Module <br/>
  
  PSRAM: Enabled <br/>

  选择选择正确端口号后开始烧写固件 <br/>

 

<b>四.说明： </b> <br/>
1.字库文件是自制的， <br/>
    已随源码做好，方法见目录/汉字库制作 <br/>

2.关于时钟校时 <br/>
    烧录一次RTClib库自带的例程文件ds3231，首次运行会自动校对ds3231硬件的时钟.
