"""Goes burling_ down the entries in the system log to correlate timestamps.

_burling: http://www.youtube.com/watch?v=0ekqsHP9Sck

"""

import re, time

line_re = re.compile(r"(?P<abs>^... [0-9 ]\d \d\d:\d\d:\d\d) " # abs timestamp
                     r"(?P<hostname>\w+) "                     # hostname
                     r"kernel: \[(?P<rel_secs>\d+)"            # seconds
                               r"\.(?P<rel_usecs>\d+)\] "      # microseconds
                     r"(?P<message>.*)")                       # log message

output_columns = ['abs', 'abs_since_boot', 'rel_time', 'rel_offset', 'message']

output_delimiter = "\t"

def uptime(open=open):
    """Get the system uptime via /proc/uptime."""
    with open('/proc/uptime') as proc_uptime:
        return float(proc_uptime.readline().split()[0])

def boot_time(uptime=uptime, time=time):
    """Get the system boot time in seconds since epoch."""
    return time.time() - uptime()


def parse_line(log_line, line_re=line_re):
    """Parses a line into its various components.

    Returns None if the line does not contain a kernel timestamp.
    """
    match = line_re.match(log_line)
    return match.groupdict() if match else None


def parse_abs_timestamp(timestamp, current_year=2011, time=time):
    """Converts the yearless timestamp to a `time.struct_time` object.

    Injects `current_year` into the tuple.
    """
    parsed = time.strptime(timestamp, '%b %d %H:%M:%S')
    return time.struct_time([current_year] + list(parsed[1:]))


class LineData(object):
    """Encapsulates analysis functions to be run on line data."""
    def __init__(self, boot_time, line_data):
        self.boot_time = boot_time
        self.line_data = line_data

    _parse_abs = staticmethod(parse_abs_timestamp)
    time = time

    def __getattr__(self, name):
        return self.line_data[name]

    @property
    def rel_time(self):
        from decimal import Decimal
        return Decimal('.'.join([self.rel_secs, self.rel_usecs]))

    @property
    def abs_since_boot(self):
        """The # of seconds between the absolute timestamp and boot time."""
        abs_secs = self.time.mktime(self._parse_abs(self.abs))
        return abs_secs - self.boot_time

    @property
    def rel_offset(self):
        """The difference between the syslog and kernel timestamps.

        Rounded down to the tens place.
        """
        from decimal import Decimal, ROUND_DOWN
        offset = self.rel_time - Decimal(str(self.abs_since_boot))
        return (offset / 10).quantize(Decimal(1), rounding=ROUND_DOWN) * 10

def format_line_data(line_data, format_order=output_columns,
                                delimiter=output_delimiter):
    """Formats processed line data to fit on a single line."""
    columns = (str(getattr(line_data, attr)) for attr in format_order)
    return delimiter.join(columns)


if __name__ == '__main__':
    import fileinput
    from functools import partial

    print output_delimiter.join(output_columns)

    parsed = (parse_line(line) for line in fileinput.input())
    data = (line for line in parsed if line)
    LineData = partial(LineData, boot_time())

    for line in data:
        print format_line_data(LineData(line))
