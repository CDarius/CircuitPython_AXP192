# SPDX-FileCopyrightText: Copyright (c) 2023 Dario Cammi
#
# SPDX-License-Identifier: MIT
"""
`axp192`
================================================================================

Circuitpython driver for AXP192 power management IC


* Author(s): Dario Cammi

Implementation Notes
--------------------

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://circuitpython.org/downloads

* Adafruit's Bus Device library: https://github.com/adafruit/Adafruit_CircuitPython_BusDevice

"""

from adafruit_bus_device.i2c_device import I2CDevice

from micropython import const

try:
    import busio
    from typing import Tuple
except ImportError:
    pass

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/CDarius/CircuitPython_AXP192.git"


_AXP192_INPUT_POWER_STATE = const(0x00)
_AXP192_INPUT_POWER_STATE_ACIN_IS_PRESENT = const(0b10000000)
_AXP192_INPUT_POWER_STATE_VBUS_IS_PRESENT = const(0b00100000)

_AXP192_POWER_CHARGE_STATUS = const(0x01)
_AXP192_POWER_CHARGE_STATUS_CHARGING = const(0b01000000)
_AXP192_POWER_CHARGE_STATUS_BAT_PRESENT = const(0b00100000)

_AXP192_DCDC13_LDO23_CTRL = const(0x12)
_AXP192_DCDC13_LDO23_CTRL_EXTEN = const(0b01000000)
_AXP192_DCDC13_LDO23_CTRL_DCDC2 = const(0b00010000)
_AXP192_DCDC13_LDO23_CTRL_LDO3 = const(0b00001000)
_AXP192_DCDC13_LDO23_CTRL_LDO2 = const(0b00000100)
_AXP192_DCDC13_LDO23_CTRL_DCDC3 = const(0b00000010)
_AXP192_DCDC13_LDO23_CTRL_DCDC1 = const(0b00000001)

_AXP192_DCDC2_OUT_VOLTAGE = const(0x25)
_AXP192_DCDC1_OUT_VOLTAGE = const(0x26)
_AXP192_DCDC3_OUT_VOLTAGE = const(0x27)

_AXP192_LDO23_OUT_VOLTAGE = const(0x28)

_AXP192_POWER_OFF_VOLTAGE = const(0x31)

_AXP192_POWER_OFF_BATT_CHGLED_CTRL = const(0x32)
_AXP192_POWER_OFF_BATT_CHGLED_CTRL_OFF = const(0b10000000)

_AXP192_CHARGING_CTRL1 = const(0x33)
_AXP192_CHARGING_CTRL1_ENABLE = const(0b10000000)

_AXP192_BACKUP_BATT = const(0x35)
_AXP192_BACKUP_BATT_CHARGING_ENABLE = const(0b10000000)

_AXP192_IRQ_3_STATUS = const(0x46)
_AXP192_IRQ_3_STATUS_PEK_SHORT_PRESS = const(0b00000010)
_AXP192_IRQ_3_STATUS_PEK_LONG_PRESS = const(0b00000001)

_AXP192_ADC_ENABLE_1 = const(0x82)

_AXP192_GPIO0_FUNCTION = const(0x90)
_AXP192_GPIO1_FUNCTION = const(0x92)
_AXP192_GPIO2_FUNCTION = const(0x93)
_AXP192_GPIO34_FUNCTION = const(0x95)

_AXP192_GPIO0_LDO_VOLTAGE = const(0x91)
_AXP192_PWM1_DUTY_RATIO_Y1 = const(0x99)
_AXP192_PWM2_DUTY_RATIO_Y1 = const(0x9C)


# pylint: disable=no-self-use
# pylint: disable=too-many-public-methods
class AXP192:
    """Circuitpython driver for AXP192 power management IC

    This driver class is designed not to be directly instanciated but to be extended.
    The subclass should not directly expose DCDCs, LDOs and GPIOs but specific properties
    and methos to interact with connected hardware. For example on M5Stack Core2 the DCDC3
    output power the LCD backlight. The subclass instead of expose the DCDC3 voltage control
    should expose a property to control the DCDC3 brightness

    :param ~busio.I2C i2c: The I2C bus AXP192 is connected to
    :param int device_address: The I2C bus addres. Default to 0x34

    **Quickstart: Importing and using the device**

    Here is an example of using the :py:class:`AXP192` class.
    First you will need to import the libraries to use the sensor

    .. code-block:: python

        import board
        from axp192 import AXP192

    Once this is done you can define your `board.I2C` object and define your sensor object

    .. code-block:: python

        i2c = board.I2C()  # uses board.SCL and board.SDA
        pmic = AXP192(i2c)

    Now you can get the AXP192 battery status

    .. code-block:: python

        is_battery_connected = pmic.is_battery_connected
        battery_voltage = pmic.battery_voltage
    """

    def __init__(self, i2c: busio.I2C, device_address: int = 0x34):
        self._device = I2CDevice(i2c, device_address)

    @property
    def is_acin_present(self) -> bool:
        """True when voltage is present on the ACIN input line"""
        reg_val = self._read_register8(_AXP192_INPUT_POWER_STATE)
        return (reg_val & _AXP192_INPUT_POWER_STATE_ACIN_IS_PRESENT) != 0

    @property
    def acin_voltage(self) -> float:
        """ACIN line actual voltage in V

        In order to be able to read this voltage ADCs must be enable via :py:attr:`all_adc_enabled`
        """
        return 1.7 * self._read_register12(0x56) / 1000.0

    @property
    def acin_current(self) -> float:
        """ACIN input line actual current in mA

        In order to be able to read this current ADCs must be enable via :py:attr:`all_adc_enabled`
        """
        return 0.625 * self._read_register12(0x58)

    @property
    def is_vbus_present(self) -> bool:
        """True when voltage is present on the VBUS power input line"""
        reg_val = self._read_register8(_AXP192_INPUT_POWER_STATE)
        return (reg_val & _AXP192_INPUT_POWER_STATE_VBUS_IS_PRESENT) != 0

    @property
    def vbus_voltage(self) -> float:
        """VBUS input line actual voltage in V

        In order to be able to read this voltage ADCs must be enable via :py:attr:`all_adc_enabled`
        """
        return 1.7 * self._read_register12(0x5A) / 1000.0

    @property
    def vbus_current(self) -> float:
        """VBUS power input line actual current in mA

        In order to be able to read this current ADCs must be enable via :py:attr:`all_adc_enabled`
        """
        return 0.375 * self._read_register12(0x5C)

    @property
    def aps_voltage(self) -> float:
        """APS (internal power supply) actual voltage in V

        In order to be able to read this voltage ADCs must be enable via :py:attr:`all_adc_enabled`
        """
        return 1.4 * self._read_register12(0x7E) / 1000.0

    @property
    def is_battery_connected(self) -> bool:
        """True when a battery is connected to AXP192"""
        reg_val = self._read_register8(_AXP192_POWER_CHARGE_STATUS)
        return (reg_val & _AXP192_POWER_CHARGE_STATUS_BAT_PRESENT) != 0

    @property
    def is_battery_charging(self) -> bool:
        """True when the battery is connected to AXP192 and is charging"""
        reg_val = self._read_register8(_AXP192_POWER_CHARGE_STATUS)
        return (reg_val & _AXP192_POWER_CHARGE_STATUS_CHARGING) != 0

    @property
    def battery_charging_enabled(self) -> bool:
        """Enable/disable the battery charging"""
        reg_val = self._read_register8(_AXP192_CHARGING_CTRL1)
        return (reg_val & _AXP192_CHARGING_CTRL1_ENABLE) != 0

    @battery_charging_enabled.setter
    def battery_charging_enabled(self, enabled: bool) -> None:
        if isinstance(enabled, bool):
            if enabled:
                self._set_bit_in_register(
                    _AXP192_CHARGING_CTRL1, _AXP192_CHARGING_CTRL1_ENABLE
                )
            else:
                self._clear_bit_in_register(
                    _AXP192_CHARGING_CTRL1, _AXP192_CHARGING_CTRL1_ENABLE
                )
        else:
            raise ValueError("Enabled must be a boolean")

    @property
    def battery_voltage(self) -> float:
        """Battery voltage in V

        In order to be able to read this voltage ADCs must be enable via :py:attr:`all_adc_enabled`
        Return 0 if no battery is connected to AXP192
        """
        return 0.0011 * self._read_register12(0x78)

    @property
    def battery_charge_current(self) -> float:
        """Battery charging current in mA

        In order to be able to read this current ADCs must be enable via :py:attr:`all_adc_enabled`
        Return 0 if no battery is connected to AXP192
        """
        return 0.5 * self._read_register12(0x7A)

    @property
    def battery_discharge_current(self) -> float:
        """Battery discharging current in mA

        In order to be able to read this current ADCs must be enable via :py:attr:`all_adc_enabled`
        Return 0 if no battery is connected to AXP192
        """
        return 0.5 * self._read_register12(0x7C)

    @property
    def battery_ouput_power(self) -> float:
        """Battery istantaneous ouput power in mW

        In order to be able to read this power ADCs must be enable via :py:attr:`all_adc_enabled`
        Return 0 if no battery is connected to AXP192
        """
        return 1.1 * 0.5 * self._read_register24(0x70) / 1000

    @property
    def battery_level(self) -> float:
        """Battery level in range 0-100%

        In order to be able to read this power ADCs must be enable via :py:attr:`all_adc_enabled`
        Return 0 if no battery is connected to AXP192
        """
        bat_voltage = self.battery_voltage
        bat_chg_current = self.battery_charge_current
        vmin = self.battery_switch_off_voltage
        vmax = self.battery_charge_target_voltage

        level = (bat_voltage - vmin) / (vmax - vmin) * 100

        # When the battery is charging the measured  battery voltage raise a little. About 0.1V
        if bat_chg_current > 15:
            level -= 10

        return min(100, max(0, level))

    @property
    def battery_switch_off_voltage(self) -> float:
        """AXP192 power off voltage threshold when powered via batterty in V"""
        reg_val = self._read_register8(_AXP192_POWER_OFF_VOLTAGE) & 0x07
        return 2.6 + 0.1 * int(reg_val)

    @property
    def battery_charge_target_voltage(self) -> float:
        """Battery charging target voltage in V

        Voltage threshold for status: battery fully charged. For LiPo battery is 4.2V
        """
        reg_val = (self._read_register8(_AXP192_CHARGING_CTRL1) & 0x60) >> 5
        if reg_val == 0:
            return 4.1
        if reg_val == 1:
            return 4.15
        if reg_val == 2:
            return 4.2

        return 4.36

    @property
    def all_adc_enabled(self) -> bool:
        """Enable/disable all AXP192 ADCs of register 0x82

        +-----------------------+------------------------------------------+
        | Register 0x82 ADCs    | AXP192 Property                          |
        +=======================+==========================================+
        | Battery voltage ADC   | :py:attr:`battery_voltage`               |
        +-----------------------+------------------------------------------+
        | Battery current ADC   | :py:attr:`battery_charge_current`        |
        |                       |                                          |
        |                       | :py:attr:`battery_discharge_current`     |
        +-----------------------+------------------------------------------+
        | ACIN voltage ADC      | :py:attr:`acin_voltage`                  |
        +-----------------------+------------------------------------------+
        | ACIN Current ADC      | :py:attr:`acin_current`                  |
        +-----------------------+------------------------------------------+
        | VBUS voltage ADC      | :py:attr:`vbus_voltage`                  |
        +-----------------------+------------------------------------------+
        | VBUS Current ADC      | :py:attr:`vbus_current`                  |
        +-----------------------+------------------------------------------+
        | APS Voltage ADC       | :py:attr:`aps_voltage`                   |
        +-----------------------+------------------------------------------+
        | TS pin ADC function   |                                          |
        +-----------------------+------------------------------------------+
        """
        return self._read_register8(_AXP192_ADC_ENABLE_1) == 0xFF

    @all_adc_enabled.setter
    def all_adc_enabled(self, enable: bool) -> None:
        self._write_register8(_AXP192_ADC_ENABLE_1, 0xFF if enable else 0x00)

    @property
    def internal_temperature(self) -> float:
        """Internal AXP192 temperature in Celsius degrees"""
        return -144.7 + 0.1 * self._read_register12(0x5E)

    @property
    def power_key_was_pressed(self) -> Tuple[bool, bool]:
        """Power key pressed status

        :returns: Two booleans: Power key is short press and power key is long press
        """
        reg_val = self._read_register8(_AXP192_IRQ_3_STATUS)
        short_press = (reg_val & _AXP192_IRQ_3_STATUS_PEK_SHORT_PRESS) != 0
        long_press = (reg_val & _AXP192_IRQ_3_STATUS_PEK_LONG_PRESS) != 0
        # clear the readed interrupt events
        if short_press or long_press:
            reg_val = (
                _AXP192_IRQ_3_STATUS_PEK_SHORT_PRESS
                | _AXP192_IRQ_3_STATUS_PEK_LONG_PRESS
            )
            self._write_register8(_AXP192_IRQ_3_STATUS, reg_val)

        return (short_press, long_press)

    def power_off(self) -> None:
        """Switch off the AXP192 and the connected devices"""
        self._set_bit_in_register(
            _AXP192_POWER_OFF_BATT_CHGLED_CTRL, _AXP192_POWER_OFF_BATT_CHGLED_CTRL_OFF
        )

    @property
    def _exten(self) -> bool:
        """Enable/disable EXTEN output (external power boost)

        This output is meant to be connected to an external power boost
        """
        reg_val = self._read_register8(_AXP192_DCDC13_LDO23_CTRL)
        return (reg_val & _AXP192_DCDC13_LDO23_CTRL_EXTEN) != 0

    @_exten.setter
    def _exten(self, value: bool) -> None:
        if not isinstance(value, bool):
            raise ValueError("value must be a boolean True or False")

        if value:
            self._set_bit_in_register(
                _AXP192_DCDC13_LDO23_CTRL, _AXP192_DCDC13_LDO23_CTRL_EXTEN
            )
        else:
            self._clear_bit_in_register(
                _AXP192_DCDC13_LDO23_CTRL, _AXP192_DCDC13_LDO23_CTRL_EXTEN
            )

    @property
    def _dcdc1_setpoint(self) -> int:
        """DCDC1 output setpoint in V

        DCDC1 can output voltages in range 0.7-3.5V in 25mV steps
        To disable the output set DCDC1 to 0V
        """
        return self.__read_dcdcx_setpoint(1)

    @_dcdc1_setpoint.setter
    def _dcdc1_setpoint(self, value) -> None:
        self.__write_dcdcx_setpoint(1, value)

    @property
    def _dcdc2_setpoint(self) -> int:
        """DCDC2 output setpoint in V

        DCDC2 can output voltages in range 0.7-2.275V in 25mV steps
        To disable the output set DCDC2 to 0V
        """
        return self.__read_dcdcx_setpoint(2)

    @_dcdc2_setpoint.setter
    def _dcdc2_setpoint(self, value) -> None:
        self.__write_dcdcx_setpoint(2, value)

    @property
    def _dcdc3_setpoint(self) -> int:
        """DCDC3 output setpoint in V

        DCDC3 can output voltages in range 0.7-3.5V in 25mV steps
        To disable the output set DCDC3 to 0V
        """
        return self.__read_dcdcx_setpoint(3)

    @_dcdc3_setpoint.setter
    def _dcdc3_setpoint(self, value) -> None:
        self.__write_dcdcx_setpoint(3, value)

    def __read_dcdcx_setpoint(self, num: int) -> float:
        enable_bit, voltage_reg, max_value = self.__get_dcdcx_registers(num)
        if (self._read_register8(_AXP192_DCDC13_LDO23_CTRL) & enable_bit) == 0:
            return 0

        return ((self._read_register8(voltage_reg) & max_value) * 25 + 700) / 1000

    def __write_dcdcx_setpoint(self, num: int, voltage: int) -> None:
        enable_bit, voltage_reg, max_value = self.__get_dcdcx_registers(num)
        voltage -= 0.7
        if voltage <= 0:
            self._clear_bit_in_register(_AXP192_DCDC13_LDO23_CTRL, enable_bit)
        else:
            reg_value = int(voltage * 1000) // 25
            reg_value = min(reg_value, max_value)

            self._write_register8(voltage_reg, reg_value)
            self._set_bit_in_register(_AXP192_DCDC13_LDO23_CTRL, enable_bit)

    def __get_dcdcx_registers(self, num: int) -> Tuple[int, int, int]:
        if num == 1:
            return (_AXP192_DCDC13_LDO23_CTRL_DCDC1, _AXP192_DCDC1_OUT_VOLTAGE, 0x7F)
        if num == 2:
            return (_AXP192_DCDC13_LDO23_CTRL_DCDC2, _AXP192_DCDC2_OUT_VOLTAGE, 0x3F)
        if num == 3:
            return (_AXP192_DCDC13_LDO23_CTRL_DCDC3, _AXP192_DCDC3_OUT_VOLTAGE, 0x7F)

        raise ValueError("num must be 1, 2 or 3")

    @property
    def _backup_battery_charging_enable(self) -> bool:
        """Enable/disable the LDO1 backup battery charging output"""
        return (
            self._read_register8(_AXP192_BACKUP_BATT)
            & _AXP192_BACKUP_BATT_CHARGING_ENABLE
        ) != 0

    @_backup_battery_charging_enable.setter
    def _backup_battery_charging_enable(self, value: bool) -> None:
        if isinstance(value, bool):
            if value:
                self._set_bit_in_register(
                    _AXP192_BACKUP_BATT, _AXP192_BACKUP_BATT_CHARGING_ENABLE
                )
            else:
                self._clear_bit_in_register(
                    _AXP192_BACKUP_BATT, _AXP192_BACKUP_BATT_CHARGING_ENABLE
                )
        else:
            raise ValueError("value must be a boolean True or False")

    @property
    def _ldo2_setpoint(self) -> float:
        """LDO2 output setpoint in V

        LDO2 can output voltages in range 1.8-3.3V in 100mV steps
        To disable the output set LDO2 to 0V
        """
        return self.__read_ldo23_setpoint(2)

    @_ldo2_setpoint.setter
    def _ldo2_setpoint(self, value) -> None:
        self.__write_ldo23_setpoint(2, value)

    @property
    def _ldo3_setpoint(self) -> float:
        """LDO3 output setpoint in V

        LDO3 can output voltages in range 1.8-3.3V in 100mV steps
        To disable the output set LDO3 to 0V
        """
        return self.__read_ldo23_setpoint(3)

    @_ldo3_setpoint.setter
    def _ldo3_setpoint(self, value) -> None:
        self.__write_ldo23_setpoint(3, value)

    def __read_ldo23_setpoint(self, num: int) -> float:
        enable_bit, value_offset = self.__get_ldo23_registers(num)
        if (self._read_register8(_AXP192_DCDC13_LDO23_CTRL) & enable_bit) == 0:
            return 0

        reg_val = (
            self._read_register8(_AXP192_LDO23_OUT_VOLTAGE) >> value_offset
        ) & 0xF
        return (reg_val * 100 + 1800) / 1000

    def __write_ldo23_setpoint(self, num: int, voltage: float) -> float:
        enable_bit, value_offset = self.__get_ldo23_registers(num)
        voltage -= 1.8
        if voltage < 0:
            self._clear_bit_in_register(_AXP192_DCDC13_LDO23_CTRL, enable_bit)
        else:
            reg_val = int(voltage * 10)  # voltage * 10 = voltage * 1000 / 100
            reg_val = min(0x0F, reg_val)
            reg_val = reg_val << value_offset
            mask = ~(0x0F << value_offset)
            reg_val = (self._read_register8(_AXP192_LDO23_OUT_VOLTAGE) & mask) | reg_val
            self._write_register8(_AXP192_LDO23_OUT_VOLTAGE, reg_val)
            self._set_bit_in_register(_AXP192_DCDC13_LDO23_CTRL, enable_bit)

    def __get_ldo23_registers(self, num: int) -> Tuple[int, int]:
        if num == 2:
            return (_AXP192_DCDC13_LDO23_CTRL_LDO2, 4)
        if num == 3:
            return (_AXP192_DCDC13_LDO23_CTRL_LDO3, 0)

        raise ValueError("num must be 2 or 3")

    def _set_gpio_floating(self, gpio_num: int) -> None:
        """
        Set the GPIO as a floting pin

        :param int gpio_num: Number of the GPIO to set as floating pin. Allowed values: 0, 1 or 2
        """
        self.__validate_gpio_num(gpio_num)
        if 0 <= gpio_num <= 2:
            self.__set_gpio_function(gpio_num, 0x7)
        else:
            raise ValueError(f"GPIO{gpio_num} doesn't support floating mode")

    def _is_gpio_floating(self, gpio_num: int) -> bool:
        """
        Return True if the GPIO is in floating pin mode

        :param int gpio_num: Number of the GPIO to check. Allowed values: 0, 1 or 2
        :returns: True is the GPIO is in floating pin mode
        """
        self.__validate_gpio_num(gpio_num)
        if 0 <= gpio_num <= 2:
            return (self.__get_gpio_function(gpio_num) & 0x06) == 0x06

        raise ValueError(f"GPIO{gpio_num} doesn't support floating mode")

    def _set_gpio_output_low(self, gpio_num: int) -> None:
        """
        Set the GPIO as a digital low value output
        When the GPIO is set as output low it always output 0V

        :param int gpio_num: Number of the GPIO to set as output low. Allowed values: 0, 1 or 2
        """
        self.__validate_gpio_num(gpio_num)
        if 0 <= gpio_num <= 2:
            self.__set_gpio_function(gpio_num, 0x5)
        else:
            raise ValueError(f"GPIO{gpio_num} doesn't support low output mode")

    def _is_gpio_output_low(self, gpio_num: int) -> bool:
        """Return True if the GPIO is in low output mode

        :param int gpio_num: Number of the GPIO to check. Allowed values: 0, 1 or 2
        :returns: True is the GPIO is in low output mode
        """
        self.__validate_gpio_num(gpio_num)
        if 0 <= gpio_num <= 2:
            return self.__get_gpio_function(gpio_num) == 0x05

        raise ValueError(f"GPIO{gpio_num} doesn't support low output mode")

    def _set_gpio_ldo_voltage_out(self, gpio_num: int, voltage: float) -> None:
        """
        Set the GPIO as an LDO voltage output
        If the request voltage is 0V the GPIO is set to low output mode.

        :param int gpio_num: Number of the GPIO to set as LDO voltage output. Allowed value: 0
        :param float voltage: LDO output voltage in V. Output range: 1.8-3.3V in 0.1V steps
        """
        self.__validate_gpio_num(gpio_num)
        if gpio_num == 0:
            if isinstance(voltage, (int, float)):
                voltage -= 1.8
                if voltage <= 0:
                    self._set_gpio_output_low(gpio_num)
                else:
                    reg_val = int(voltage / 0.1)
                    reg_val = min(0x0F, reg_val)
                    self._write_register8(_AXP192_GPIO0_LDO_VOLTAGE, reg_val << 4)
                    self.__set_gpio_function(gpio_num, 0x2)
            else:
                raise ValueError("Voltage must be a number")
        else:
            raise ValueError(f"GPIO{gpio_num} doesn't support LDO voltage mode")

    def _get_gpio_ldo_voltage_out(self, gpio_num: int) -> float:
        """
        Return the GPIO voltage setpoint the GPIO is set as an LDO voltage output
        If the GPIO is not in LDO voltage output mode returns 0

        :param int gpio_num: Number of the GPIO to check. Allowed value: 0
        :returns: GPIO output voltage in V
        """
        if not self._is_gpio_ldo_voltage_out(gpio_num):
            return 0

        if gpio_num == 0:
            reg_value = self._read_register8(_AXP192_GPIO0_LDO_VOLTAGE) >> 4
            return reg_value * 0.1 + 1.8

        raise ValueError(f"GPIO{gpio_num} doesn't support LDO voltage mode")

    def _is_gpio_ldo_voltage_out(self, gpio_num: int) -> bool:
        """
        Returns if the GPIO is in LDO voltage output mode

        :param int gpio_num: Number of the GPIO to check. Allowed value: 0
        :returns: True when GPIO is in LDO voltage output mode
        """
        self.__validate_gpio_num(gpio_num)
        if gpio_num == 0:
            return self.__get_gpio_function(gpio_num) == 0x02

        raise ValueError(f"GPIO{gpio_num} doesn't support LDO voltage mode")

    def _set_gpio_pwm_out(self, gpio_num: int, duty_cycle: int) -> None:
        """
        Set the GPIO as a PWM output
        PWM Output voltage is VINT (2.5V)

        :param int gpio_num: Number of the GPIO to set as PWM output. Allowed values: 1 or 2
        :param int duty_cyle: PWM duty cycle. Range 0-255
        """
        self.__validate_gpio_num(gpio_num)
        if 1 <= gpio_num <= 2:
            if isinstance(duty_cycle, int):
                if 0 <= duty_cycle <= 255:
                    pwm_reg = (
                        _AXP192_PWM1_DUTY_RATIO_Y1
                        if gpio_num == 1
                        else _AXP192_PWM2_DUTY_RATIO_Y1
                    )
                    self._write_register8(pwm_reg, 0xFF)
                    self._write_register8(pwm_reg + 1, duty_cycle)
                    self.__set_gpio_function(gpio_num, 0x02)
                else:
                    raise ValueError("Duty cycle out of range. Allowed range 0-255")
            else:
                raise ValueError("Duty cycle must be an integer number from 0 to 255")
        else:
            raise ValueError(f"GPIO{gpio_num} doesn't PWM output mode")

    def _get_gpio_pwm_out(self, gpio_num: int) -> int:
        """
        Get the GPIO PWM output duty cycle

        :param int gpio_num: Number of the GPIO to check. Allowed values: 1, 2
        :returns: PWM duty_cyle in range 0-255. Returns 0 if the GPIO isn't in PWM output mode
        """
        self.__validate_gpio_num(gpio_num)
        if 1 <= gpio_num <= 2:
            if self._is_gpio_pwm_out(gpio_num):
                pwm_reg = (
                    _AXP192_PWM1_DUTY_RATIO_Y1
                    if gpio_num == 1
                    else _AXP192_PWM2_DUTY_RATIO_Y1
                )
                return self._read_register8(pwm_reg + 1)

        raise ValueError(f"GPIO{gpio_num} doesn't PWM output mode")

    def _is_gpio_pwm_out(self, gpio_num: int) -> bool:
        """Returns if the the GPIO is in PWM output mode

        :param int gpio_num: Number of the GPIO to check. Allowed values: 1, 2
        :returns: True when GPIO is in PWM output mode
        """
        self.__validate_gpio_num(gpio_num)
        if 1 <= gpio_num <= 2:
            return self.__get_gpio_function(gpio_num) == 0x02

        raise ValueError(f"GPIO{gpio_num} doesn't PWM output mode")

    def __validate_gpio_num(self, gpio_num: int) -> None:
        if not isinstance(gpio_num, int) or gpio_num < 0 or gpio_num > 4:
            raise ValueError("gpio_num must be an integer number between 0 and 4")

    def __set_gpio_function(self, gpio_num: int, function: int) -> None:
        if gpio_num == 0:
            self._write_register8(_AXP192_GPIO0_FUNCTION, function & 0x07)
        elif gpio_num == 1:
            self._write_register8(_AXP192_GPIO1_FUNCTION, function & 0x07)
        elif gpio_num == 2:
            self._write_register8(_AXP192_GPIO2_FUNCTION, function & 0x07)
        elif gpio_num == 3:
            reg_val = self._read_register8(_AXP192_GPIO34_FUNCTION)
            reg_val &= ~0x03
            reg_val |= function & 0x03
            self._write_register8(_AXP192_GPIO34_FUNCTION, reg_val)
        elif gpio_num == 4:
            reg_val = self._read_register8(_AXP192_GPIO34_FUNCTION)
            reg_val &= ~0x0C
            reg_val |= (function & 0x03) << 2
            self._write_register8(_AXP192_GPIO34_FUNCTION, reg_val)
        else:
            raise ValueError("gpio_num must be in range 0-4")

    def __get_gpio_function(self, gpio_num: int) -> int:
        if gpio_num == 0:
            return self._read_register8(_AXP192_GPIO0_FUNCTION) & 0x07
        if gpio_num == 1:
            return self._read_register8(_AXP192_GPIO1_FUNCTION) & 0x07
        if gpio_num == 2:
            return self._read_register8(_AXP192_GPIO2_FUNCTION) & 0x07
        if gpio_num == 3:
            return self._read_register8(_AXP192_GPIO34_FUNCTION) & 0x03
        if gpio_num == 4:
            return (self._read_register8(_AXP192_GPIO34_FUNCTION) >> 2) & 0x03

        raise ValueError("gpio_num must be in range 0-4")

    def _set_bit_in_register(self, register: int, bitmask: int) -> None:
        """
        Set a single or multiple bits in a 8 bit register

        :param int register: Register number. Allowed range: 0-255
        :param int bitmask: Bitmask 8 bit wide with the bits to set
        """
        val = self._read_register8(register)
        self._write_register8(register, val | bitmask)

    def _clear_bit_in_register(self, register: int, bitmask: int) -> None:
        """
        Clear a single or multiple bits in a 8 bit register

        :param int register: Register number. Allowed range: 0-255
        :param int bitmask: Bitmask 8 bit wide with the bits to clear
        """
        val = self._read_register8(register)
        self._write_register8(register, val & ~bitmask)

    def _write_register8(self, register: int, value: int) -> None:
        """
        Write an AXP192 8bit register

        :param int register: Register number. Allowed range: 0-255
        :param int value: Value to write: Allowed range: 0x0 - 0xFF
        """
        out_buf = bytearray(2)

        out_buf[0] = register
        out_buf[1] = value
        with self._device:
            self._device.write(out_buf)

    def _read_register8(self, register: int) -> int:
        """
        Read an AXP192 8bit register

        :param int register: Register number. Allowed range: 0-255
        :returns: The register value
        """
        in_buf = bytearray(1)
        out_buf = bytearray(1)

        out_buf[0] = register
        with self._device:
            self._device.write_then_readinto(out_buf, in_buf)

        return in_buf[0]

    def _read_register12(self, register: int) -> int:
        """
        Read an AXP192 12bit register

        :param int register: Register number. Allowed range: 0-255
        :returns: The register value
        """
        in_buf = bytearray(2)
        out_buf = bytearray(1)

        out_buf[0] = register
        with self._device:
            self._device.write_then_readinto(out_buf, in_buf)

        return in_buf[0] << 4 | in_buf[1]

    def _read_register24(self, register: int) -> int:
        """
        Read an AXP192 24bit register

        :param int register: Register number. Allowed range: 0-255
        :returns: The register value
        """
        in_buf = bytearray(3)
        out_buf = bytearray(1)

        out_buf[0] = register
        with self._device:
            self._device.write_then_readinto(out_buf, in_buf)

        return in_buf[0] << 16 | in_buf[1] << 8 | in_buf[2]
