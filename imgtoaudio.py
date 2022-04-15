# You may have to run `pip install scipy`

print("Hello")

# https://matplotlib.org/3.5.0/api/_as_gen/matplotlib.pyplot.specgram.html
# Audio libraries
# from scipy.io import wavfile
# from scipy.fft import fftshift
# from scipy import signal

# Plotting libraries
import matplotlib.pyplot as plt

import numpy as np
import math
from tqdm import tqdm
import threading
import time

from curses import wrapper

# importing OpenCV(cv2) module
# You may need to run `pip install opencv-python`
import cv2

import testgui

waveLock = threading.Lock()
waves = []

doneLock = threading.Lock()
done = 0;

def main(stdscr):
    global done

    scrLock = threading.Lock()

    def addstr(x, y, str):
        with scrLock:
            stdscr.addstr(x, y, str)
            stdscr.refresh()

    # Plotting constants
    VERT_RES = 64 # Image height in px
    MINFREQ = 1000 # The frequency for the bottom of the image
    MAXFREQ = 10e3 # The frequency for the top of the image
    USE_LOG = False # Use a log scale for frequency
    PX_DURATION = 100 # Make each pixel 100ms long
    SAMPLE_RATE = 44100 # How many samples per second
    MAX_AMPL = 1 # Maximum amplitude if brightness is 255
    WORKER_THREADS = 32

    # Load the audio file
    # print("Loading ...")
    # samplerate, adata = wavfile.read('../testsong.wav')
    #
    # print(f"number of channels = {adata.shape[1]}")
    #
    # length = adata.shape[0] / samplerate
    # print(f"length = {length}s")

    # Python program to read image using OpenCV

    # Save image in set directory
    # Read RGB image
    img = cv2.imread('tux.png', -1)

    width = int((VERT_RES / len(img)) * len(img[0]))
    height = VERT_RES

    img = cv2.resize(img, (width, height))

    addstr(0, 0, "Graying ...        ")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.bitwise_not(gray)
    img_data = gray2

    addstr(0, 0, "Filling ...        ")

    for y in range(len(img)):
        for x in range(len(img[y])):
            if img[y][x][3] == 0:
                gray2[y][x] = 0

    addstr(0, 0, "Generating ...        ")
    freqs = []

    samplecount = int(SAMPLE_RATE * (PX_DURATION/1000))

    times = np.linspace(0, PX_DURATION/1000, samplecount)

    zro = np.zeros(samplecount)

    if USE_LOG:
        minlog = np.log10(MINFREQ)
        maxlog = np.log10(MAXFREQ)
        logvals = np.linspace(minlog, maxlog, VERT_RES, False)
        freqs = np.power(10, logvals)
    else:
        freqs = np.linspace(MINFREQ, MAXFREQ, VERT_RES, False)

    waves = []

    for f in freqs:
        waves.append(np.sin(2 * np.pi * f * times))

    def setRowCh(y, ch):
        with scrLock:
            stdscr.addch((y // WORKER_THREADS) + 1, (y % WORKER_THREADS) + 1, ch)
            stdscr.refresh()

    for y in range(height):
        waves.append([])

    blockdata = []

    for i in range(width):
        blockdata.append(None)

    x = 0

    print(times)
    sinewave = np.sin(2 * np.pi * MAXFREQ * times)

    rows, cols = stdscr.getmaxyx()

    # mw = testgui.MainWindow(width, height)
    # mw.show()

    def calcCol(num, tq):
        block = np.copy(zro)
        for row in range(VERT_RES):
            frequency = VERT_RES - row - 1
            dta = img_data[row][num]
            amplitude = (dta / 255) # 255 is the max pixel value
            thiswave = amplitude * waves[frequency]
            block += thiswave

            # mw.setBtnColor(row,num,dta)
            # mw.setBtnInfo(row,num,dta,amplitude)

        blockdata[num] = block

    alldone = 0
    startnum = 0

    def useThreads(max, target, text):
        stdscr.clear()
        # Calculate the thingies
        # print("Working ...")
        global done
        global alldone
        done = 0
        alldone = 0

        for y in range(max):
            setRowCh(y, '.')

        for y in range(max):
        # for y in range(height):
            try:
                def threadFunc(num, arg2):
                    setRowCh(num, '+')
                    global done
                    global alldone
                    target(num, arg2)
                    with doneLock:
                        done += 1
                        alldone += 1
                    setRowCh(num, '#')
                t1 = threading.Thread(target=threadFunc, args=(y,(y == WORKER_THREADS - 1)))
                t1.start()
            except:
                print("Error: unable to start thread")
            if y % WORKER_THREADS == WORKER_THREADS - 1:
                addstr(0, 0, f"{text} ...        ")
                while done < WORKER_THREADS:
                    pass
                done = 0;
                addstr(0, 0, "Starting ...        ")

        while alldone < max:
            time.sleep(0.5)

    # useThreads(height, calcRow, "Drawing")
    useThreads(width, calcCol, "Rendering")

    addstr(0, 0, "Combining ...        ")
    data = []
    for blocknum in range(width):
        data = np.append(data, blockdata[blocknum])

    addstr(0, 0, "Showing ...        ")
    # Plot only the left channel
    plt.specgram(data, Fs=SAMPLE_RATE)
    ax = plt.gca()
    # ax.set_yscale('log')
    ax.set_ylim([0, MAXFREQ])
    # plt.specgram(sinewave, Fs=SAMPLE_RATE)
    # plt.plot(data[0:20])
    # plt.plot(sinewave[0:200])
    # plt.ylabel('Frequency [Hz]')
    # plt.xlabel('Time [sec]')


    # Output img with window name as 'image'
    cv2.imshow('image', cv2.resize(gray2, (512, 512), interpolation= cv2.INTER_NEAREST))

    # QT_QPA_PLATFORM=wayland
    plt.show()

    # Maintain output window utill
    # user presses a key
    print("Press any key to continue")
    cv2.waitKey(0)

    # Destroying present windows on screen
    cv2.destroyAllWindows()

    print("Plotting ...")

wrapper(main)
