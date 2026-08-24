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
from pymeasure.instruments.siglenttechnologies.siglent_sdm3065x import SDM3065X
from pymeasure.test import expected_protocol


def test_voltage_dc():
    with expected_protocol(
        SDM3065X,
        [("MEAS:VOLT:DC?", "+4.23450000E-03")]
    ) as inst:
        assert inst.voltage_dc == 4.23450000e-03


def test_configure_voltage_ac():
    with expected_protocol(
        SDM3065X,
        [("CONF:VOLT:AC 200", None)]
    ) as inst:
        inst.configure_voltage(range=200, ac=True)


def test_configure_resistance_4w():
    with expected_protocol(
        SDM3065X,
        [("CONF:FRES 200", None)]
    ) as inst:
        inst.configure_resistance(range=200, wires=4)


def test_measure_temperature():
    with expected_protocol(
        SDM3065X,
        [("MEAS:TEMP? RTD,PT100", "-2.00000000E+02")]
    ) as inst:
        assert inst.measure_temperature("RTD", "PT100") == -200.0


def test_sample_count_truncated():
    with expected_protocol(
        SDM3065X,
        [("SAMP:COUN 599999999", None),
         ("SAMP:COUN?", "599999999")]
    ) as inst:
        inst.sample_count = 700000000  # too large, gets truncated
        assert inst.sample_count == 599999999


def test_trigger_source():
    with expected_protocol(
        SDM3065X,
        [("TRIG:SOUR IMM", None),
         ("TRIG:SOUR?", "IMM")]
    ) as inst:
        inst.trigger_source = "IMM"
        assert inst.trigger_source == "IMM"


def test_trigger_reading():
    with expected_protocol(
        SDM3065X,
        [("READ?", "+1.23006735E-03,+1.30991641E-03")]
    ) as inst:
        assert inst.trigger_reading() == [1.23006735e-03, 1.30991641e-03]


def test_scan_enabled():
    with expected_protocol(
        SDM3065X,
        [("ROUT:SCAN 1", None),
         ("ROUT:SCAN?", "1")]
    ) as inst:
        inst.scan_enabled = True
        assert inst.scan_enabled is True


def test_scan_card_installed():
    with expected_protocol(
        SDM3065X,
        [("ROUT:STAT?", "1")]
    ) as inst:
        assert inst.scan_card_installed is True


def test_scan_limit_high_truncated():
    with expected_protocol(
        SDM3065X,
        [("ROUT:LIMI:HIGH 16", None),
         ("ROUT:LIMI:HIGH?", "16")]
    ) as inst:
        inst.scan_limit_high = 20  # too large, gets truncated
        assert inst.scan_limit_high == 16


def test_channel_configure():
    with expected_protocol(
        SDM3065X,
        [("ROUT:CHAN 1,ON,2W,2KOHM,SLOW", None)]
    ) as inst:
        inst.ch_1.configure("2W", enabled=True, range="2KOHM", speed="SLOW")


def test_channel_configuration_query():
    with expected_protocol(
        SDM3065X,
        [("ROUT:CHAN? 1", "1,ON,DCV,AUTO,SLOW")]
    ) as inst:
        assert inst.ch_1.configuration == ["1", "ON", "DCV", "AUTO", "SLOW"]


def test_channel_last_value():
    with expected_protocol(
        SDM3065X,
        [("ROUT:DATA? 2", "1.79221344E-04    VDC")]
    ) as inst:
        assert inst.ch_2.last_value == 1.79221344e-04


def test_channel_enable_disable():
    with expected_protocol(
        SDM3065X,
        [("ROUT:CHAN? 1", "1,OFF,CONT,AUTO,FAST"),
         ("ROUT:CHAN 1,ON,CONT,AUTO,FAST", None)]
    ) as inst:
        inst.ch_1.enable()


def test_scan_relative_enabled_query():
    with expected_protocol(
        SDM3065X,
        [("ROUT:RELA? DCV", "ON")]
    ) as inst:
        assert inst.scan_relative_enabled("DCV") is True


def test_scan_relative_enabled_set():
    with expected_protocol(
        SDM3065X,
        [("ROUT:RELA DCV,ON", None)]
    ) as inst:
        inst.scan_relative_enabled("DCV", True)


def test_configure_scan_rtd_sensor():
    with expected_protocol(
        SDM3065X,
        [("ROUT:TEMP:RTD PT100", None)]
    ) as inst:
        inst.configure_scan_rtd_sensor("PT100")
