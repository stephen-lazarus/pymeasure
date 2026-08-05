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

from pymeasure.instruments import Instrument, SCPIMixin
from pymeasure.instruments.validators import strict_discrete_set, truncated_range


class DL3021A(SCPIMixin, Instrument):
    """Represents a Rigol DL3021A DC Electronic Load
    and provides a high-level for interacting with the instrument
    """

    def __init__(self, adapter, name="DL3021A", **kwargs):
        super().__init__(adapter, name, **kwargs)

    operation_mode = Instrument.control(
        ":SOUR:FUNC?", ":SOUR:FUNC %s",
        """Sets the static operation mode of the electronic load.
           Queries the static operation mode of the electronic load.

        :type : string
        """,
        validator=strict_discrete_set,
        values=['CURR', 'RES', 'VOLT', 'POW'],
        cast=str
    )

    current_range = Instrument.control(
        ":SOUR:CURR:RANG?", ":SOUR:CURR:RANG %g",
        """Sets the current range in CC mode and transient operation mode to be a high range or a
            low one.
            Queries the current range set in CC mode and transient operation mode.

        :type : float
        """,
        validator=truncated_range,
        values=[0, 40],
    )

    current_vlim = Instrument.control(
        ":SOUR:CURR:VLIM?", ":SOUR:CURR:VLIM %g",
        """Sets the voltage limit in CC mode.
           Queries the voltage limit set in CC mode.

        :type : float
        """,
        validator=truncated_range,
        values=[0, 150],
    )

    set_current = Instrument.control(
        ":SOUR:CURR:LEV:IMM?", ":SOUR:CURR:LEV:IMM %g",
        """Sets the load's regulated current in CC mode.
           Queries the load's regulated current set in CC mode.

        :type : float
        """,
        validator=truncated_range,
        values=[0, 40],
        dynamic=True
    )

    input = Instrument.control(
        ":SOUR:INP:STAT?", ":SOUR:INP:STAT %d",
        """Sets the input of the electronic load to be on or off.
           Queries whether the input of the electronic load is on or off.

        :type : int
        """,
        validator=strict_discrete_set,
        values=[0, 1],
    )

    voltage = Instrument.measurement(
        ":MEASure:VOLTage:DC?",
        """Reads the input voltage of the instrument.

        :type : float
        """
    )

    def shutdown(self):
        """ Ensure that the voltage is turned to zero
        and disable the output. """
        self.set_current = 0
        self.input       = 0
        super().shutdown()
