# micropython_PMSx003_demo
Quick and dirty interface between micropython (tested on ESP8266) and a PMSx003 sensor (tested on PMSA003). Prints sensor data out via the WebREPL (not the serial console) due to hardware limitations, so to view the data follow the instructions [here](https://docs.micropython.org/en/latest/esp8266/tutorial/repl.html#webrepl-a-prompt-over-wifi)

This repo was created because although it sounds easy to use micropython to interface with one of these sensors, there are some gotchas along the way that weren't immediately clear to me. Hopefully this saves someone else the trouble.

In particular:
 - There are only two UARTs on the ESP8266, UART(0) which can read/write, and UART(1) which can only write. So to interface with the sensor, UART(0) must be used.
 - UART(0) must be detached from the REPL so we can use it to talk to the sensor.
 - The serial 'rxbuf' needs to be increased from 15, or else it drops the 16th byte, leading to each message from the sensor appearing to be two 15-byte chunks. Much confusion ensues.
 - Trying to use UART(0) and UART(1) at the same time (even just to try to attach UART(1) to the USB serial pins to print stuff) seems to be problematic, so the serial console just goes silent after boot.
