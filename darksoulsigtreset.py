import struct
from datetime import timedelta
from pathlib import Path

# Byte locations
CHARTIME = 0x02dc  # Index of IGT
# CHARTIME_MENU = 0x3c0460 # Incorrect(?)


def find_time(savefile, hours, minutes, seconds):
    """
    Attempt to find the savefile time in Dark Souls

    :param savefile: file path of savefile to analyse
    :param hours: hours in save
    :param minutes: minutes in save
    :param seconds: seconds in save
    :return:
    """
    savepath = Path(savefile)
    timestruct = struct.Struct('I')

    size = savepath.stat().st_size
    data = savepath.read_bytes()

    # Get the search time in seconds
    search_time = hours * (60 ** 2) + minutes * 60 + seconds

    for idx in range(0, size):
        packet = data[idx:idx + timestruct.size]
        if len(packet) == timestruct.size:
            time_int = timestruct.unpack(packet)[0]
            time_s = time_int // 1000
            if search_time == time_s:
                td = timedelta(milliseconds=time_int)
                print(f'Index: {idx}\nTime: {td}')


def read_time(savefile):
    """
    Read and return the time from the first save in a dark souls savefile
    """
    with open(savefile, 'rb') as f:
        f.seek(CHARTIME, 0)
        bin_time = f.read(4)
        time_ms, = struct.unpack('I', bin_time)
        return str(timedelta(milliseconds=time_ms))


def reset_time(savefile):
    """
    Write zero to the time data value in a dark souls savefile
    """
    zero_val = b'\x00\x00\x00\x00'
    with open(savefile, 'r+b') as f:
        f.seek(CHARTIME, 0)
        f.write(zero_val)

    print('Written zero value to IGT')
