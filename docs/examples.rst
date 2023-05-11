Simple test
------------

Ensure your device works with this simple test, it show the battery voltage
if a battery is connected to AXP192

.. literalinclude:: ../examples/axp192_simpletest.py
    :caption: examples/axp192_simpletest.py
    :linenos:

Power key pressed test
----------------------

Simple test to show how to read the power key button status

.. literalinclude:: ../examples/axp192_power_key_press.py
    :caption: examples/axp192_power_key_press.py
    :linenos:

Extending AXP192 library
------------------------

A more complex example that show how to extend the AXP192 library. This example extend
the AXP192 library and create a :py:class:`PMIC` for the  `M5Stack Core2 <https://docs.m5stack.com/en/core/core2>`_

.. literalinclude:: ../examples/axp192_m5stack_core2_pmic.py
    :caption: examples/axp192_m5stack_core2_pmic.py
    :linenos:
