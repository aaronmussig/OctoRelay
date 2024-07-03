# -*- coding: utf-8 -*-
from typing import Optional
import gpiod
from gpiod.chip import Chip
from gpiod.line import Direction, Value
import logging

logger = logging.getLogger()


def xor(left: bool, right: bool) -> bool:
    return left is not right

class Relay():
    def __init__(self, pin: int, inverted: bool):
        logger.info(f'ZZZ instantiated {pin} {inverted}')
        self.pin = pin # GPIO pin
        self.inverted = inverted # marks the relay as normally closed

    def __repr__(self) -> str:
        return f"{type(self).__name__}(pin={self.pin},inverted={self.inverted},closed={self.is_closed()})"

    def close(self):
        """Activates the current flow through the relay."""
        self.toggle(True)

    def open(self):
        """Deactivates the current flow through the relay."""
        self.toggle(False)

    def is_closed(self) -> bool:
        """Returns the logical state of the relay."""
        # https://github.com/brgl/libgpiod/blob/master/bindings/python/examples/get_line_value.py
        print(f'checkiing closed {self.pin}')
        logger.info(f'checking closed {self.pin}')
        with gpiod.request_lines(
                "/dev/gpiochip4",
                consumer="get-line-value",
                config={self.pin:  gpiod.LineSettings(direction=Direction.INPUT)},
        ) as request:
            value = request.get_value(self.pin)
            pin_state = value is Value.ACTIVE

        #     print("{}={}".format(25, value))
        #
        #
        # with gpiod.Chip("/dev/gpiochip4") as chip:
        #
        #     info = chip.get_line_info(25)
        #     is_input = info.direction == gpiod.line.Direction.INPUT
        #     print(
        #         "line {:>3}: {:>12} {:>12} {:>8} {:>10}".format(
        #             info.offset,
        #             info.name or "unnamed",
        #             info.consumer or "unused",
        #             "input" if is_input else "output",
        #             "active-low" if info.active_low else "active-high",
        #         )
        #     )
        #
        # pin = OutputDevice(pin=self.pin, active_high=True, initial_value=None)
        # pin_state = bool(pin.value)
        return xor(self.inverted, pin_state)

    def toggle(self, desired_state: Optional[bool] = None) -> bool:
        """
        Switches the relay state to the desired one specified as an optional argument.
        If the argument is not specified then switches based on the current state.
        Returns the new logical state of the relay.
        """
        if desired_state is None:
            desired_state = not self.is_closed()

        if xor(self.inverted, desired_state):
            value = Value.ACTIVE
        else:
            value = Value.INACTIVE

        logger.info(f'toggle {self.pin} {desired_state}')

        with gpiod.request_lines("/dev/gpiochip4",
                consumer="toggle-line-value",
                config={
                    self.pin: gpiod.LineSettings(direction=Direction.OUTPUT, output_value=value)
                },
        ) as request:
            request.set_value(self.pin, value)
        return desired_state
