#!/usr/bin/env python
# encoding: utf-8
from __future__ import print_function
from __future__ import division
"""
broadband_cap
==============
Calculate time to reach broadband cap with specified bandwidth speeds

Usage::

    python ./broadband_cap.py --help

    python ./broadband_cap.py --cap 250 --speed 1000

    python ./broadband_cap.py --print-table


"""
import collections

# one megabyte == 8 megabits
MEGABYTES_IN_A_MEGABIT = 0.125  # 1/8
# one gigabyte == 1000 megabytes (*)
MEGABYTES_IN_A_GIGABYTE = 1000  # 1000/1


def seconds_to_cap(cap_in_gigabytes, speed_in_megabits):
    """
    Args:
        speed (int): speed in megabits/second
        cap (int): cap in megabytes

    Returns:
        float: seconds to reach cap with the given bandwidth

    """
    seconds_one = (
        (cap_in_gigabytes * MEGABYTES_IN_A_GIGABYTE)
        /
        (MEGABYTES_IN_A_MEGABIT * speed_in_megabits))

    speed_in_megabytes = speed_in_megabits  * MEGABYTES_IN_A_MEGABIT
    speed_in_gigabytes = speed_in_megabytes / MEGABYTES_IN_A_GIGABYTE
    seconds_two = (
        cap_in_gigabytes
        /
        speed_in_gigabytes)

    assert seconds_one == seconds_two

    return seconds_one


_Time = collections.namedtuple('Time', (
    'years',
    'days',
    'hours',
    'minutes',
    'seconds'))
class Time(_Time):
    @staticmethod
    def from_seconds(t):
        """
        Args:
            t (int/float): number of seconds

        Returns:
            (days, hours, minutes, seconds)
        """
        year_in_seconds   = 60*60*24*365.25
        day_in_seconds    = 60*60*24
        hour_in_seconds   = 60*60
        minute_in_seconds = 60
        _t = t
        years, _t   = divmod(_t, year_in_seconds)
        days, _t    = divmod(_t, day_in_seconds)
        hours, _t   = divmod(_t, hour_in_seconds)
        minutes, _t = divmod(_t, minute_in_seconds)
        seconds = _t
        return Time(years, days, hours, minutes, seconds)

    def __str__(self):
        s = "{days:02n} days, {hours:02n} hours, {minutes:02n} minutes, {seconds:02n} seconds"
        if self.years > 0:
            s = '{years} years, %s' % s
        return s.format(**self._asdict())

    def __str__(self):
        def _(self):
            fields = self._fields
            if self.years == 0:
                fields = fields[1:]
            for field in fields:
                n = getattr(self, field)
                if n > 0:
                    yield ('%2d %s' % (n, field)).ljust(10)
                else:
                    yield ' ' * 10
        return ' '.join(tuple(_(self)))


def print_time_to_cap(cap, speed):
    print("%d GB cap @ %d megabits:" % (cap, speed))
    seconds = seconds_to_cap(cap, speed)
    t = Time.from_seconds(seconds)
    print("    %s" % str(t))


def print_cap_table(figures):
    print(  "cap (GB)  speed (mb/s)  time to reach cap (at advertised capacity)\n"
            "--------  ------------  ------------------------------------------")
    for cap, speed in figures:
        seconds = seconds_to_cap(cap, speed)
        t = Time.from_seconds(seconds)
        s = "%8s  %12s  %s" % (cap, speed, str(t))
        print(s)


# (cap in GB, speed in mb/s), seconds
SECONDS_TO_CAP_CHECK_FIGURES = (
    ((1,   1),      8000),
    ((250, 1),   2000000),
    ((250, 5),    400000),
    ((250, 25),    80000),
    ((250, 50),    40000),
    ((250, 100),   20000),
    ((250, 250),    8000),
    ((250, 1000),   2000),
    ((250, 10000),   200),
    ((300, 1),   2400000),
    ((300, 5),    480000),
    ((300, 25),    96000),
    ((300, 50),    48000),
    ((300, 100),   24000),
    ((300, 300),    8000),
    ((300, 1000),   2400),
    ((300, 10000),   240),
)


import unittest
class Test_broadband_cap_time(unittest.TestCase):
    def test_seconds_to_timetuple(self):
        IO = (
            (1,       (0, 0, 0,  0, 1)),
            (60,      (0, 0, 0,  1, 0)),
            (3600,    (0, 0, 1,  0, 0)),
            (86400,   (0, 1, 0,  0, 0)),
            (31557600,(1, 0, 0,  0, 0)),
            (31647661,(1, 1, 1,  1, 1)),
            (2000,    (0, 0, 0, 33, 20)),
        )
        for input_, expected_output in IO:
            output = Time.from_seconds(input_)
            self.assertEqual(expected_output, output)

    def test_seconds_to_cap(self):
        for input_, expected_output in SECONDS_TO_CAP_CHECK_FIGURES:
            output = seconds_to_cap(*input_)
            self.assertEqual(expected_output, output)


    def test_broadband_cap_time(self):
        for input_, expected_t_seconds in SECONDS_TO_CAP_CHECK_FIGURES:
            print_time_to_cap(*input_)


def main(*args):
    import logging
    import optparse
    import sys

    prs = optparse.OptionParser(usage="%prog : args")

    prs.add_option('--cap',
                   dest='cap',
                   type=float,
                   action='store',
                   help='Size of cap in Megabytes')
    prs.add_option('--speed',
                   '--bandwidth',
                   dest='speed',
                   type=float,
                   action='store',
                   help='Speed of connection in Megabits/s (bandwidth)')

    prs.add_option('--print-table',
                   dest='print_table',
                   action='store_true',
                   help='Print a table of figures')

    prs.add_option('-v', '--verbose',
                    dest='verbose',
                    action='store_true',)
    prs.add_option('-q', '--quiet',
                    dest='quiet',
                    action='store_true',)
    prs.add_option('-t', '--test',
                    dest='run_tests',
                    action='store_true',)

    args = args and list(args) or sys.argv[1:]
    (opts, args) = prs.parse_args()

    if not opts.quiet:
        logging.basicConfig()

        if opts.verbose:
            logging.getLogger().setLevel(logging.DEBUG)

    if opts.run_tests:
        sys.argv = [sys.argv[0]] + args
        import unittest
        sys.exit(unittest.main())

    if opts.print_table:
        print_cap_table(x[0] for x in SECONDS_TO_CAP_CHECK_FIGURES)
        return 0

    if None in (opts.cap, opts.speed):
        prs.print_help()
        prs.error("Must specify --cap and --speed")

    print_time_to_cap(opts.cap, opts.speed)
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())

