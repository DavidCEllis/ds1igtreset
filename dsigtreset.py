import struct
from datetime import timedelta
from hashlib import md5
from pathlib import Path


CHARTIME = 0x02dc  # Index of IGT


def find_time(savefile, hours, minutes, seconds):
    """
    Attempt to find the savefile time in Dark Souls (stored in ms)

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
    fix the game savefile hashes

    :param savefile: input dark souls savefile
    """
    zero_val = b'\x00\x00\x00\x00'
    with open(savefile, 'r+b') as f:
        f.seek(CHARTIME, 0)
        f.write(zero_val)

        # Reset the hashes (thanks AndrovT)
        f.seek(0x2c0 + 0x14)
        hash1 = md5(f.read(0x5fff0))
        f.seek(0x2c0 + 0x60004)
        f.write(hash1.digest())

        f.seek(0x2c0 + 0x10)
        hash2 = md5(f.read(0x60004))
        f.seek(0x2c0)
        f.write(hash2.digest())

    print('Written zero value to IGT and fixed hashes.')


def reset_time_gui():
    from tkinter import Tk, filedialog

    root = Tk()
    root.withdraw()
    savefile = filedialog.askopenfilename(
        initialdir='.',
        title='Select Dark Souls Savefile for IGT reset',
        filetypes=(('all files', '*.*'), )
    )
    root.destroy()

    savepath = Path(savefile)

    if savepath.is_file():
        print(f'Resetting time for {savepath}')
        reset_time(savefile)
    else:
        print('No Savefile Selected')


if __name__ == '__main__':
    reset_time_gui()
    input('Press return to close')
