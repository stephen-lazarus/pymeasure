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

import logging

from pymeasure.instruments import Instrument
from pymeasure.instruments.channel import Channel
from pymeasure.instruments.generic_types import SCPIUnknownMixin
from pymeasure.instruments.validators import strict_discrete_set, truncated_range

log = logging.getLogger(__name__)  # https://docs.python.org/3/howto/logging.html#library-config
log.addHandler(logging.NullHandler())

BOOL_MAPPINGS = {True: 1, False: 0}


class SDM3065XScanChannel(Channel):
    """A channel of the SDM3065X's optional scan card.

    The scan card provides 16 channels (1-16). Each channel's switch state,
    measurement mode, range and integration speed are all set together with a
    single ``ROUTe:CHANnel`` command, and read back together as well.
    """

    MODES = ["DCV", "DCI", "ACV", "ACI", "2W", "4W", "CAP", "FRQ", "CONT", "DIO", "TEMP"]
    SPEEDS = ["SLOW", "FAST"]

    configuration = Instrument.measurement(
        "ROUT:CHAN? {ch}",
        """Get this channel's configuration as ``[channel, switch, mode, range, speed]``,
        e.g. ``['1', 'ON', 'DCV', 'AUTO', 'SLOW']``.
        """,
        cast=str,
    )

    last_value = Instrument.measurement(
        "ROUT:DATA? {ch}",
        """Get the last scanned measurement value of this channel, in its configured unit.""",
        separator=None,
        cast=str,
        get_process_list=lambda values: float(values[0]),
    )

    def configure(self, mode, enabled=True, range="AUTO", speed="FAST"):
        """Configure this scan channel's measurement mode, range, speed and switch state.

        :param mode: measurement mode, one of 'DCV', 'DCI', 'ACV', 'ACI', '2W', '4W',
            'CAP', 'FRQ', 'CONT', 'DIO', 'TEMP'
        :param enabled: ``True`` (default) to close (include) the channel in the scan,
            ``False`` to open (exclude) it
        :param range: the measurement range for `mode`, or 'AUTO' (default); see the
            SDM3065X programming guide for the valid values for each mode
        :param speed: 'SLOW' or 'FAST' (default)
        """
        mode = strict_discrete_set(mode, self.MODES)
        speed = strict_discrete_set(speed, self.SPEEDS)
        switch = "ON" if enabled else "OFF"
        self.write(f"ROUT:CHAN {{ch}},{switch},{mode},{range},{speed}")

    def enable(self):
        """Close (include in the scan) this channel, keeping its current mode/range/speed."""
        _, _, mode, range, speed = self.configuration
        self.configure(mode, enabled=True, range=range, speed=speed)

    def disable(self):
        """Open (exclude from the scan) this channel, keeping its current mode/range/speed."""
        _, _, mode, range, speed = self.configuration
        self.configure(mode, enabled=False, range=range, speed=speed)


class SDM3065X(SCPIUnknownMixin, Instrument):
    """Represents the Siglent SDM3065X digital multimeter and provides a high-level
    interface for interacting with the instrument, including its optional scan card.

    .. code-block:: python

        dmm = SDM3065X("TCPIP::192.168.1.1::INSTR")

        dmm.configure_voltage(ac=False)     # configure a DC voltage measurement
        print(dmm.trigger_reading())        # trigger and read a measurement

        print(dmm.voltage_dc)               # one-shot DC voltage measurement (autorange)

        # Optional scan card: configure and close channel 1 for 2-wire resistance,
        # then read its last scanned value.
        dmm.scan_enabled = True
        dmm.ch_1.configure("2W", enabled=True, range="2KOHM", speed="SLOW")
        dmm.scanning = True
        print(dmm.ch_1.last_value)

    """

    channels = Instrument.MultiChannelCreator(SDM3065XScanChannel, list(range(1, 17)))

    def __init__(self, adapter, name="Siglent Technologies SDM3065X Multimeter", **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs
        )

    # ==========================================================================================
    # MEASure Subsystem - one-shot measurements using default (autorange) settings
    # ==========================================================================================

    voltage_dc = Instrument.measurement(
        "MEAS:VOLT:DC?",
        """Measure the DC voltage in Volts, using autorange.""",
    )

    voltage_ac = Instrument.measurement(
        "MEAS:VOLT:AC?",
        """Measure the AC voltage in Volts, using autorange.""",
    )

    current_dc = Instrument.measurement(
        "MEAS:CURR:DC?",
        """Measure the DC current in Amps, using autorange.""",
    )

    current_ac = Instrument.measurement(
        "MEAS:CURR:AC?",
        """Measure the AC current in Amps, using autorange.""",
    )

    resistance = Instrument.measurement(
        "MEAS:RES?",
        """Measure the 2-wire resistance in Ohms, using autorange.""",
    )

    resistance_4w = Instrument.measurement(
        "MEAS:FRES?",
        """Measure the 4-wire resistance in Ohms, using autorange.""",
    )

    frequency = Instrument.measurement(
        "MEAS:FREQ?",
        """Measure the frequency in Hz.""",
    )

    period = Instrument.measurement(
        "MEAS:PER?",
        """Measure the period in seconds.""",
    )

    capacitance = Instrument.measurement(
        "MEAS:CAP?",
        """Measure the capacitance in Farads, using autorange.""",
    )

    continuity = Instrument.measurement(
        "MEAS:CONT?",
        """Measure the continuity resistance in Ohms. Returns +9.9E37 when open.""",
    )

    diode = Instrument.measurement(
        "MEAS:DIOD?",
        """Measure the diode forward voltage drop in Volts. Returns +9.9E37 when open.""",
    )

    def measure_temperature(self, probe_type="RTD", sensor_type="PT100"):
        """Measure the temperature once, using the given sensor.

        :param probe_type: 'RTD' (default) or 'THER' (thermocouple)
        :param sensor_type: for 'RTD': 'PT100' (default) or 'PT1000'; for 'THER':
            one of 'BITS90', 'EITS90', 'JITS90', 'KITS90', 'NITS90', 'RITS90',
            'SITS90', 'TITS90'
        :return: the measured temperature, in the unit set by :attr:`temperature_unit`
        """
        return self.values(f"MEAS:TEMP? {probe_type},{sensor_type}")[0]

    configuration = Instrument.measurement(
        "CONF?",
        """Get the present measurement function, range and (on the SDM3065X) resolution
        as a raw reply string, e.g. ``'VOLT +2.00000000E-01,+1.00000000E-07'``.
        """,
        cast=str,
        separator=None,
        maxsplit=0,
        get_process_list=lambda values: values[0],
    )

    # ==========================================================================================
    # CONFigure Subsystem - set up a measurement function without triggering a reading
    # ==========================================================================================

    def configure_voltage(self, range="AUTO", ac=False):
        """Configure the instrument for a voltage measurement.

        :param range: full-scale range, or 'AUTO' (default), 'MIN', 'MAX', 'DEF'
        :param ac: ``True`` for AC voltage, ``False`` (default) for DC voltage
        """
        self.write(f"CONF:VOLT:{'AC' if ac else 'DC'} {range}")

    def configure_current(self, range="AUTO", ac=False):
        """Configure the instrument for a current measurement.

        :param range: full-scale range, or 'AUTO' (default), 'MIN', 'MAX', 'DEF'
        :param ac: ``True`` for AC current, ``False`` (default) for DC current
        """
        self.write(f"CONF:CURR:{'AC' if ac else 'DC'} {range}")

    def configure_resistance(self, range="AUTO", wires=2):
        """Configure the instrument for a resistance measurement.

        :param range: full-scale range, or 'AUTO' (default), 'MIN', 'MAX', 'DEF'
        :param wires: 2 (default) for 2-wire resistance, 4 for 4-wire resistance
        """
        wires = strict_discrete_set(wires, [2, 4])
        self.write(f"CONF:{'FRES' if wires == 4 else 'RES'} {range}")

    def configure_frequency(self):
        """Configure the instrument for a frequency measurement."""
        self.write("CONF:FREQ")

    def configure_period(self):
        """Configure the instrument for a period measurement."""
        self.write("CONF:PER")

    def configure_capacitance(self, range="AUTO"):
        """Configure the instrument for a capacitance measurement.

        :param range: full-scale range, or 'AUTO' (default), 'MIN', 'MAX', 'DEF'
        """
        self.write(f"CONF:CAP {range}")

    def configure_temperature(self, probe_type="THER", sensor_type="DEF"):
        """Configure the instrument for a temperature measurement.

        :param probe_type: 'RTD' or 'THER' (default, thermocouple)
        :param sensor_type: for 'RTD': 'PT100' or 'PT1000'; for 'THER': one of
            'BITS90', 'EITS90', 'JITS90', 'KITS90', 'NITS90', 'RITS90', 'SITS90',
            'TITS90'. 'DEF' (default) uses the instrument's default sensor.
        """
        self.write(f"CONF:TEMP {probe_type},{sensor_type}")

    def configure_continuity(self):
        """Configure the instrument for a continuity measurement."""
        self.write("CONF:CONT")

    def configure_diode(self):
        """Configure the instrument for a diode measurement."""
        self.write("CONF:DIOD")

    # ==========================================================================================
    # Sampling / triggering
    # ==========================================================================================

    sample_count = Instrument.control(
        "SAMP:COUN?", "SAMP:COUN %d",
        """Control the number of measurements (samples) taken per trigger, from 1 to
        599999999.
        """,
        validator=truncated_range,
        values=[1, 599999999],
        cast=int,
    )

    trigger_count = Instrument.control(
        "TRIG:COUN?", "TRIG:COUN %s",
        """Control the number of triggers accepted before the instrument returns to the
        idle trigger state. Accepts an integer, or 'MIN', 'MAX', 'DEF', 'INF' (infinite).
        """,
    )

    trigger_delay = Instrument.control(
        "TRIG:DEL?", "TRIG:DEL %s",
        """Control the delay between the trigger signal and the start of the measurement,
        in seconds. Accepts a numeric value, or 'MIN', 'MAX', 'DEF'.
        """,
    )

    trigger_delay_auto_enabled = Instrument.control(
        "TRIG:DEL:AUTO?", "TRIG:DEL:AUTO %d",
        """Control whether the trigger delay is selected automatically by the instrument.""",
        validator=strict_discrete_set,
        values=BOOL_MAPPINGS,
        map_values=True,
    )

    trigger_slope = Instrument.control(
        "TRIG:SLOP?", "TRIG:SLOP %s",
        """Control the trigger slope: 'POS' (positive) or 'NEG' (negative).""",
        validator=strict_discrete_set,
        values=["POS", "NEG"],
        cast=str,
    )

    trigger_source = Instrument.control(
        "TRIG:SOUR?", "TRIG:SOUR %s",
        """Control the trigger source: 'IMM' (immediate), 'EXT' (external) or 'BUS'.""",
        validator=strict_discrete_set,
        values=["IMM", "EXT", "BUS"],
        cast=str,
    )

    temperature_unit = Instrument.control(
        "UNIT:TEMP?", "UNIT:TEMP %s",
        """Control the unit used for temperature measurements: 'C' (default), 'F' or 'K'.""",
        validator=strict_discrete_set,
        values=["C", "F", "K"],
        cast=str,
    )

    beeper_enabled = Instrument.control(
        "SYST:BEEP:STAT?", "SYST:BEEP:STAT %d",
        """Control whether the beeper sounds for continuity, diode, and probe hold
        measurements.
        """,
        validator=strict_discrete_set,
        values=BOOL_MAPPINGS,
        map_values=True,
    )

    data_points = Instrument.measurement(
        "DATA:POIN?",
        """Get the number of measurements currently stored in reading memory.""",
        cast=int,
    )

    def data_last(self):
        """Get the last measurement taken, with its unit, even mid-measurement."""
        return self.ask("DATA:LAST?").strip()

    def data_remove(self, count):
        """Read and erase the oldest measurements from reading memory.

        :param count: number of readings to remove, from 1 to 10000
        :return: a list of the removed readings
        """
        return self.values(f"DATA:REM? {count}")

    def system_preset(self):
        """Restore the instrument's power-up configuration (see also :meth:`reset`)."""
        self.write("SYST:PRES")

    def initiate(self):
        """Set the trigger state to 'wait for trigger', clearing reading memory."""
        self.write("INIT")

    def abort(self):
        """Abort a measurement in progress and return to the idle trigger state."""
        self.write("ABOR")

    def fetch(self):
        """Wait for measurements to complete and return them, without erasing reading memory."""
        return self.values("FETC?")

    def trigger_reading(self):
        """Trigger and return measurements, per the current trigger/sample configuration.

        This sends the ``READ?`` command. It is named :meth:`trigger_reading` rather than
        ``read`` to avoid shadowing :meth:`~.CommonBase.read`, which is used internally for
        low-level adapter communication.
        """
        return self.values("READ?")

    # ==========================================================================================
    # ROUTe Subsystem - optional scan card
    #
    # Only takes effect once the scan card is installed and `scan_enabled` is True.
    # ==========================================================================================

    scan_card_installed = Instrument.measurement(
        "ROUT:STAT?",
        """Get whether the optional scan card is installed.""",
        cast=int,
        get_process=bool,
    )

    scan_enabled = Instrument.control(
        "ROUT:SCAN?", "ROUT:SCAN %d",
        """Control whether the scan card function is enabled. Scan card write commands
        only take effect once this is enabled.
        """,
        validator=strict_discrete_set,
        values=BOOL_MAPPINGS,
        map_values=True,
    )

    scanning = Instrument.control(
        "ROUT:STAR?", "ROUT:STAR %d",
        """Control whether scan card measurement is running.""",
        validator=strict_discrete_set,
        values=BOOL_MAPPINGS,
        map_values=True,
    )

    scan_mode = Instrument.control(
        "ROUT:FUNC?", "ROUT:FUNC %s",
        """Control the scan card cycle mode: 'SCAN' (continuous loop) or 'STEP'
        (single-step).
        """,
        validator=strict_discrete_set,
        values=["SCAN", "STEP"],
        cast=str,
    )

    scan_delay = Instrument.control(
        "ROUT:DEL?", "ROUT:DEL %s",
        """Control the scan card's per-channel delay time, in seconds. Accepts a numeric
        value, or 'MIN', 'MAX', 'DEF'.
        """,
    )

    scan_count_auto_enabled = Instrument.control(
        "ROUT:COUN:AUTO?", "ROUT:COUN:AUTO %d",
        """Control whether the scan card cycles automatically.""",
        validator=strict_discrete_set,
        values=BOOL_MAPPINGS,
        map_values=True,
    )

    scan_count = Instrument.control(
        "ROUT:COUN?", "ROUT:COUN %s",
        """Control the number of scan card cycle measurements. Accepts a numeric value,
        or 'MIN', 'MAX', 'DEF'.
        """,
    )

    scan_limit_high = Instrument.control(
        "ROUT:LIMI:HIGH?", "ROUT:LIMI:HIGH %d",
        """Control the highest channel number included in the scan, from 1 to 16.""",
        validator=truncated_range,
        values=[1, 16],
        cast=int,
    )

    scan_limit_low = Instrument.control(
        "ROUT:LIMI:LOW?", "ROUT:LIMI:LOW %d",
        """Control the lowest channel number included in the scan, from 1 to 16.""",
        validator=truncated_range,
        values=[1, 16],
        cast=int,
    )

    scan_impedance = Instrument.control(
        "ROUT:IMP?", "ROUT:IMP %s",
        """Control the scan card's input impedance for DC voltage measurements:
        '10M' or '10G'.
        """,
        validator=strict_discrete_set,
        values=["10M", "10G"],
        cast=str,
    )

    scan_temperature_unit = Instrument.control(
        "ROUT:TEMP:UNIT?", "ROUT:TEMP:UNIT %s",
        """Control the unit used for scan card temperature measurements: 'C' (default),
        'F' or 'K'.
        """,
        validator=strict_discrete_set,
        values=["C", "F", "K"],
        cast=str,
    )

    scan_temperature_transducer = Instrument.measurement(
        "ROUT:TEMP:TRAN?",
        """Get the configured scan card temperature sensor as e.g. ``['RTD', 'PT100']``.""",
        cast=str,
    )

    dcv_auto_zero_enabled = Instrument.control(
        "ROUT:DCV:AZ?", "ROUT:DCV:AZ %d",
        """Control auto-zero for scan card DC voltage measurements. SDM3065X only.""",
        validator=strict_discrete_set,
        values=BOOL_MAPPINGS,
        map_values=True,
    )

    dci_auto_zero_enabled = Instrument.control(
        "ROUT:DCI:AZ?", "ROUT:DCI:AZ %d",
        """Control auto-zero for scan card DC current measurements. SDM3065X only.""",
        validator=strict_discrete_set,
        values=BOOL_MAPPINGS,
        map_values=True,
    )

    resistance_auto_zero_enabled = Instrument.control(
        "ROUT:RES:AZ?", "ROUT:RES:AZ %d",
        """Control auto-zero for scan card 2-wire resistance measurements.""",
        validator=strict_discrete_set,
        values=BOOL_MAPPINGS,
        map_values=True,
    )

    fresistance_auto_zero_enabled = Instrument.control(
        "ROUT:FRES:AZ?", "ROUT:FRES:AZ %d",
        """Control auto-zero for scan card 4-wire resistance measurements.""",
        validator=strict_discrete_set,
        values=BOOL_MAPPINGS,
        map_values=True,
    )

    frequency_aperture = Instrument.control(
        "ROUT:FREQ:APER?", "ROUT:FREQ:APER %g",
        """Control the gate time (in seconds) for scan card frequency measurements:
        1, 0.1, 0.01, or 0.001.
        """,
        validator=strict_discrete_set,
        values=[1, 0.1, 0.01, 0.001],
    )

    period_aperture = Instrument.control(
        "ROUT:PER:APER?", "ROUT:PER:APER %g",
        """Control the gate time (in seconds) for scan card period measurements:
        1, 0.1, 0.01, or 0.001.
        """,
        validator=strict_discrete_set,
        values=[1, 0.1, 0.01, 0.001],
    )

    def configure_scan_rtd_sensor(self, sensor_type="PT100"):
        """Configure the RTD sensor model used by scan channels in 'TEMP' mode.

        :param sensor_type: 'PT100' (default) or 'PT1000'
        """
        sensor_type = strict_discrete_set(sensor_type, ["PT100", "PT1000"])
        self.write(f"ROUT:TEMP:RTD {sensor_type}")

    def configure_scan_thermocouple_sensor(self, sensor_type="KITS90"):
        """Configure the thermocouple sensor model used by scan channels in 'TEMP' mode.

        :param sensor_type: one of 'BITS90', 'EITS90', 'JITS90', 'KITS90' (default),
            'NITS90', 'RITS90', 'SITS90', 'TITS90'
        """
        sensor_type = strict_discrete_set(
            sensor_type,
            ["BITS90", "EITS90", "JITS90", "KITS90", "NITS90", "RITS90", "SITS90", "TITS90"],
        )
        self.write(f"ROUT:TEMP:THER {sensor_type}")

    def scan_relative_enabled(self, mode, enabled=None):
        """Get or set the relative-value (null) switch for a scan card measurement mode.

        :param mode: one of 'DCV', 'DCI', 'ACV', 'ACI', '2W', '4W', 'CAP', 'FRQ', 'TEMP'
        :param enabled: ``True``/``False`` to set the relative switch for `mode`; leave
            as ``None`` (default) to query its current state instead.
        :return: ``True``/``False`` when querying (``enabled=None``); ``None`` when setting.
        """
        mode = strict_discrete_set(
            mode, ["DCV", "DCI", "ACV", "ACI", "2W", "4W", "CAP", "FRQ", "TEMP"]
        )
        if enabled is None:
            return self.ask(f"ROUT:RELA? {mode}").strip() == "ON"
        self.write(f"ROUT:RELA {mode},{'ON' if enabled else 'OFF'}")
        return None
