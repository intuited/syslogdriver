"""Goes burling_ down the entries in the system log to correlate timestamps.

_burling: http://www.youtube.com/watch?v=0ekqsHP9Sck

"""

import re
line_re = re.compile(r"(?P<abs>^... [0-9 ]\d \d\d:\d\d:\d\d) " # abs timestamp
                     r"(?P<hostname>\w+) "                     # hostname
                     r"kernel: \[(?P<rel_secs>\d+)"            # seconds
                               r"\.(?P<rel_usecs>\d+)\] "      # microseconds
                     r"(?P<message>.*)")                       # log message

output_columns = ['abs', 'rel_secs', 'message']

output_delimiter = "\t"


def secs_since_uptime(uptime, abs_timestamp):
    """Translates an absolute timestamp into seconds since uptime."""

def parse_line(log_line, line_re=line_re):
    """Parses a line into its various components.

    Returns None if the line does not contain a kernel timestamp.
    """
    match = line_re.match(log_line)
    return match.groupdict() if match else None

def format_line_data(line_data, format_order=output_columns,
                                delimiter=output_delimiter):
    """Formats processed line data to fit on a single line."""
    elements = (line_data[key] for key in format_order)
    return delimiter.join(elements)
    

if __name__ == '__main__':
    import fileinput
    print output_delimiter.join(output_columns)
    parsed = (parse_line(line) for line in fileinput.input())
    data = (line for line in parsed if line)
    for line in data:
        print format_line_data(line)
