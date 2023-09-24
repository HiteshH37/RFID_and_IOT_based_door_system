import time
import network
from machine import Pin
from mfrc522 import MFRC522
import utime
from gpio_lcd import GpioLcd
import BlynkLib
 
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

#Enter your ssid(wifi name) and password
wlan.connect("SSID","Password")

#Enter your token here
BLYNK_AUTH = 'authentication token'

# Create the LCD object
lcd = GpioLcd(rs_pin=Pin(8),
              enable_pin=Pin(9),
              d4_pin=Pin(10),
              d5_pin=Pin(11),
              d6_pin=Pin(12),
              d7_pin=Pin(13),
              num_lines=2, num_columns=16)

rfid_reader = MFRC522(spi_id=0,sck=2,miso=4,mosi=7,cs=5,rst=18)
# Wait for network connection
wait = 10
while wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    wait -= 1
    print('waiting for connection...')
    time.sleep(1)
 
# Handle connection error
if wlan.status() != 3:
    raise RuntimeError('network connection failed')
else:
    print('connected')
    ip = wlan.ifconfig()[0]
    print('IP: ', ip)
 
# Connect to Blynk
blynk = BlynkLib.Blynk(BLYNK_AUTH)
 
# Initialize the pins
relay = Pin(0,Pin.OUT)


 
# Register virtual pin handler
@blynk.on("V1") #virtual pin V1
def v1_write_handler(value): #read the value
    if int(value[0]) == 0:
            lcd.clear()
            lcd.putstr('Door locked')
            relay.value(0) #turn the relay1 on
            time.sleep(1)
    else:
            lcd.clear()
            lcd.putstr('Door unlocked')
            relay.value(1) #turn the relay1 off
            time.sleep(1)
       
 
def identidfn():
        rfid_reader.init()
    
        (card_status, card_type) = rfid_reader.request(rfid_reader.REQIDL)
        if card_status == rfid_reader.OK:
            (card_status, card_id) = rfid_reader.SelectTagSN()
        
        if card_status == rfid_reader.OK:
            rfid_card = int.from_bytes(bytes(card_id),"little",False)
            
            if rfid_card == 439535360:
                lcd.clear()
                lcd.putstr("Door unlocked")
                relay.value(1)
                time.sleep(5)
                lcd.clear()
                lcd.putstr("Door locked")
                relay.value(0)
                time.sleep(0.5)
            else:
                lcd.clear()
                lcd.putstr("Access denied")
                time.sleep(1)
                lcd.clear()
                lcd.putstr("Door locked")
                time.sleep(0.5)
                print("Detected Card : "+ str(rfid_card))
        
while True:
    identidfn()
    blynk.run()
    lcd.move_to(0,4)
    lcd.putstr("Place your ID on  the scanner")