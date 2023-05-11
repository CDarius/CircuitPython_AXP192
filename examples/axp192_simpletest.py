# SPDX-FileCopyrightText: Copyright (c) 2023 Dario Cammi
#
# SPDX-License-Identifier: MIT

import time
import board
from axp192 import AXP192

i2c = board.I2C()
pmic = AXP192(i2c)

while True:
    if pmic.is_battery_connected:
        battery_voltage = pmic.battery_voltage
        print(f"Battery voltage {battery_voltage}V")
    else:
        print("No battery connected")

    time.sleep(1)
