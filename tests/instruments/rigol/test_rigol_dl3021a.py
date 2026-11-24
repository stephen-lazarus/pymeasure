#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2026 PyMeasure Developers
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import pytest

from pymeasure.test import expected_protocol
from pymeasure.instruments.rigol.rigol_dl3021a import DL3021A


def test_operation_mode_cv():
    with expected_protocol(DL3021A, [(":SOUR:FUNC VOLT", None)]) as inst:
        inst.operation_mode = "VOLT"


@pytest.mark.parametrize("value", [5, 12.5])
def test_set_voltage(value):
    with expected_protocol(
        DL3021A,
        [(f":SOUR:VOLT:LEV:IMM {value:g}", None),
         (":SOUR:VOLT:LEV:IMM?", f"{value}")],
    ) as inst:
        inst.set_voltage = value
        assert inst.set_voltage == value


def test_voltage_range():
    with expected_protocol(DL3021A, [(":SOUR:VOLT:RANG 150", None)]) as inst:
        inst.voltage_range = 150


def test_voltage_ilim():
    with expected_protocol(
        DL3021A,
        [(":SOUR:VOLT:ILIM 2.5", None),
         (":SOUR:VOLT:ILIM?", "2.5")],
    ) as inst:
        inst.voltage_ilim = 2.5
        assert inst.voltage_ilim == 2.5


def test_current_measurement():
    with expected_protocol(DL3021A, [(":MEAS:CURR:DC?", "1.234")]) as inst:
        assert inst.current == 1.234
