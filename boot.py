# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()
# boot.py
# Этот файл запускается при загрузке.
# Можете изменить его для отключения запуска WLAN, Bluetooth или USB.

import bluetooth
