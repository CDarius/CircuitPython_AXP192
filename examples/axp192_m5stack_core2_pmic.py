# SPDX-FileCopyrightText: Copyright (c) 2023 Dario Cammi
#
# SPDX-License-Identifier: MIT

import time
import board
from axp192 import AXP192

__LCD_BRIGHTNESS_MIN_V = 2.45
__LCD_BRIGHTNESS_MAX_V = 3.3


class PMIC(AXP192):
    def __init__(self):
        super().__init__(board.I2C())

    @property
    def speaker_enabled(self) -> bool:
        """Enable/disable onboard speaker"""
        return self._is_gpio_floating(2)

    @speaker_enabled.setter
    def speaker_enabled(self, enabled: bool) -> None:
        if enabled is True:
            self._set_gpio_floating(2)
        else:
            self._set_gpio_output_low(2)

    @property
    def green_led_brightness(self) -> int:
        """
        Green led brightness

        Brightness range goes from 0 (led off) to 255 (full brightness)
        """
        return 255 - self._get_gpio_pwm_out(1)

    @green_led_brightness.setter
    def green_led_brightness(self, brightness: int) -> None:
        brightness = min(255, max(0, brightness))
        self._set_gpio_pwm_out(1, 255 - brightness)

    @property
    def vibration_motor_strength(self) -> int:
        """
        Vibration motor strength

        Streght range goes from 0 (motor off) to 15 (max intensity)
        """
        volt = self._ldo3_setpoint
        if volt == 0:
            return 0

        return round((self._ldo3_setpoint - 1.8) / 0.1)

    @vibration_motor_strength.setter
    def vibration_motor_strength(self, strength: int) -> None:
        if isinstance(strength, int):
            if strength <= 0:
                self._ldo3_setpoint = 0
            else:
                strength = min(15, strength)
                self._ldo3_setpoint = 1.8 + strength * 0.1
        else:
            raise ValueError("strengh must be an integer value in range 0-15")

    @property
    def lcd_brightness(self) -> float:
        """LCD backlight brightness

        Brightness range goes from 0.0 (no backlight) to 1.0 (max brightness)
        """
        volt = self._dcdc3_setpoint
        if volt == 0:
            return 0

        dV = __LCD_BRIGHTNESS_MAX_V - __LCD_BRIGHTNESS_MIN_V
        brightness = (volt - __LCD_BRIGHTNESS_MIN_V) / dV
        return max(0.0, brightness)

    @lcd_brightness.setter
    def lcd_brightness(self, brightness: float) -> None:
        if brightness < 0.1:
            self._dcdc3_setpoint = 0
        else:
            brightness = min(1.0, brightness)
            dV = __LCD_BRIGHTNESS_MAX_V - __LCD_BRIGHTNESS_MIN_V
            self._dcdc3_setpoint = brightness * dV + __LCD_BRIGHTNESS_MIN_V

    @property
    def power_supply_from_m_bus_enabled(self) -> bool:
        """Enable/disable if Core2 power supply should comes from an M-BUS stackable module"""
        return self._is_gpio_floating(0)

    @power_supply_from_m_bus_enabled.setter
    def power_supply_from_m_bus_enabled(self, enabled: bool) -> None:
        if not isinstance(enabled, bool):
            raise ValueError(
                "power_supply_from_m_bus_enabled must be True/False boolean value"
            )

        # If the requested power source is already active do not take any action
        if enabled == self.power_supply_from_m_bus_enabled:
            return

        if enabled:
            # Swith to M_BUS

            # Enable IPSOUT regardless of N_VBUSEN
            self._set_bit_in_register(0x30, 0b10000000)
            # Disable the 5V power boost
            self._exten = False
            # Set GPIO0 to float and the pull down resistor set N_VBUSEN low
            # When N_VBUSEN is low IPSOUT select VBUS as source (BUS_5V)
            self._set_gpio_floating(0)
        else:
            # Swtch to USB or battery power supply

            # Set GPIO0 to LDO_OUTPUT to set N_VBUSEN high
            # When N_VBUSEN is high IPSOUT do not select VBUS as source (BUS_5V)
            self._set_gpio_ldo_voltage_out(0, 3.3)
            # Enable the 5V power boost
            self._exten = True
            # Enable IPSOUT only when N_VBUSEN is set
            self._clear_bit_in_register(0x30, 0b10000000)

    @property
    def bus_5v_power_boost_enabled(self) -> bool:
        """Enable/disable BUS_5V power boost"""
        return self._exten

    @bus_5v_power_boost_enabled.setter
    def bus_5v_power_boost_enabled(self, enabled: bool) -> None:
        self._exten = enabled


pmic = PMIC()

while True:
    for i in range(255):
        pmic.green_led_brightness = i
        time.sleep(0.001)

    for i in range(255, 0, -1):
        pmic.green_led_brightness = i
        time.sleep(0.001)
