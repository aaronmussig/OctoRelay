# -*- coding: utf-8 -*-
from typing import Optional
import re
import subprocess


RE_OUTPUT = re.compile(r'.+ \| ([hilo]{2}) \/\/.+')

def xor(left: bool, right: bool) -> bool:
    return left is not right

class Relay():
    def __init__(self, pin: int, inverted: bool, logger):
        self.logger = logger
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
        self.logger.debug(f'>>> is_closed(pin={self.pin})')
        result = subprocess.check_output(["pinctrl", "get", str(self.pin)], encoding='utf-8')
        self.logger.debug(f'>>>     result = {result}')
        hits = RE_OUTPUT.findall(result)
        if hits:
            pin_state = hits[0] == 'hi'
        else:
            pin_state = False
        self.logger.debug(f'>>>     pin_state = {pin_state}')
        out = xor(self.inverted, pin_state)
        self.logger.debug(f'>>>     out = {out}')
        return out

    def toggle(self, desired_state: Optional[bool] = None) -> bool:
        """
        Switches the relay state to the desired one specified as an optional argument.
        If the argument is not specified then switches based on the current state.
        Returns the new logical state of the relay.
        """
        self.logger.debug(f'>>> toggle(pin={self.pin}, {desired_state})')
        if desired_state is None:
            desired_state = not self.is_closed()
            self.logger.debug(f'>>>     since desired_state is None, its now {desired_state}')

        xor_value = xor(self.inverted, desired_state)
        self.logger.debug(f'>>>     xor_value = {xor_value}')
        if xor_value:
            value = "dh"
        else:
            value = "dl"

        self.logger.debug(f'>>>    pin {self.pin} is now getting set to {value}')
        result = subprocess.check_output(["pinctrl", "set", str(self.pin), "op", value, "pd"], encoding='utf-8')
        self.logger.debug(f'    result = {result}')
        self.logger.debug(f'>>>     returning {desired_state}')
        return desired_state
