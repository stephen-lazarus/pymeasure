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
from pymeasure.instruments.instrument import Instrument
from pymeasure.instruments.siglenttechnologies.siglent_spdbase import (
    SPDBase,
    SPDChannel,
)
from pymeasure.instruments.validators import (
    strict_discrete_set,
)


class SPD3303XE(SPDBase):
    """Represent the Siglent SPD3303X-E Power Supply.
    """

    voltage_range = [0, 32]
    current_range = [0, 3]
    ch_1 = Instrument.ChannelCreator(SPDChannel, 1,
                                     voltage_range=voltage_range,
                                     current_range=current_range)
    ch_2 = Instrument.ChannelCreator(SPDChannel, 2,
                                     voltage_range=voltage_range,
                                     current_range=current_range)

    def __init__(self, adapter, name="Siglent Technologies SPD3303X-E Power Supply", **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs
        )

        self.selected_channel_values={1: "CH1", 2: "CH2"} #add the channels
        self.ch_1.voltage_setpoint_values = self.voltage_range
        self.ch_1.current_limit_values = self.current_range
        self.ch_2.voltage_setpoint_values = self.voltage_range
        self.ch_2.current_limit_values = self.current_range

    select_opmode = Instrument.setting(
            "OUTPut:TRACK %d",
            """Select operation mode. Parameters {0|1|2} mean independent, series and
                parallel respectively.

            :type : int
            """,
            validator=strict_discrete_set,
            values=[0, 1, 2]
    )
