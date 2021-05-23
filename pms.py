import machine
import select
import uos
import time

TX_TO_SENSOR_PIN   = 15 #MCU 'TX' pin
RX_FROM_SENSOR_PIN = 13 #MCU 'RX' pin

class PMSA003Reading:
    def __init__(self, data):
        self.frame_length = int.from_bytes(data[2:4], 'big')
        self.pm1_0_std = int.from_bytes(data[4:6], 'big')
        self.pm2_5_std = int.from_bytes(data[6:8], 'big')
        self.pm10_std = int.from_bytes(data[8:10], 'big')
        self.pm1_0_atm = int.from_bytes(data[10:12], 'big')
        self.pm2_5_atm = int.from_bytes(data[12:14], 'big')
        self.pm10_atm = int.from_bytes(data[14:16], 'big')
        self.num0_3 = int.from_bytes(data[16:18], 'big')
        self.num0_5 = int.from_bytes(data[18:20], 'big')
        self.num1_0 = int.from_bytes(data[20:22], 'big')
        self.num2_5 = int.from_bytes(data[22:24], 'big')
        self.num5_0 = int.from_bytes(data[24:26], 'big')
        self.num10 = int.from_bytes(data[26:28], 'big')
        self.checksum = int.from_bytes(data[30:32], 'big')
        self.bytes = data[0:32]
        if sum(data[0:30]) != self.checksum:
            print("Checksum mismatch! Expected {}, got {}".format(sum(data[0:30]), self.checksum))
    
    def __str__(self):
        return "Standard: PM1.0 {}   PM2.5 {}   PM10 {}\nCurrent:  PM1.0 {}   PM2.5 {}   PM10 {}  \nParticles per 0.1L: >0.3 {}  >0.5 {}  >1.0 {}  >2.5 {}  >5.0 {}  >10 {}\n".format(self.pm1_0_std, self.pm2_5_std, self.pm10_std, self.pm1_0_atm, self.pm2_5_atm, self.pm10_atm, self.num0_3, self.num0_5, self.num1_0, self.num2_5, self.num5_0, self.num10)
    


def parsebuf(buf):
    pos = buf.rfind(b'BM', 0, -32) #start sequence, make sure the rest of the packet is there
    if pos >= 0:
        reading = PMSA003Reading(buf[pos:])
        print(reading)
        return reading
    return None

#Let the user CTRL-C out of this script on boot if they only have serial access
print("Detaching from console in 3 seconds!")
time.sleep(3)
print("Console detached")

uos.dupterm(None, 1) #Detach serial from console so PMS sensor isn't read as REPL input

uart = machine.UART(0, 9600)
uart.init(tx=machine.Pin(TX_TO_SENSOR_PIN), rx=machine.Pin(RX_FROM_SENSOR_PIN), rxbuf=32) #Increase rxbuf to prevent overflow/dropped 16th byte

#Poll to be efficient
poll = select.poll()
poll.register(uart, select.POLLIN)

buf = bytes()

while True:
    res = poll.poll(1000)
    if len(res) > 0:
        if res[0][1] == select.POLLIN:
            newdata = uart.read()
            buf += newdata
            reading = parsebuf(buf)
            if reading is not None:
                buf = bytes()
        else:
            raise RuntimeError("Got poll error!")
    else:
        print("Got no data")