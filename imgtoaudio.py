# You may have to run `pip install scipy`

print("Hello")

# https://matplotlib.org/3.5.0/api/_as_gen/matplotlib.pyplot.specgram.html
# Audio libraries
# from scipy.io import wavfile
# from scipy.fft import fftshift
# from scipy import signal
from scipy.io.wavfile import write

# Plotting libraries
import matplotlib.pyplot as plt

import numpy as np
import math
from tqdm import tqdm
import threading
import time

import curses

# importing OpenCV(cv2) module
# You may need to run `pip install opencv-python`
import cv2

import testgui

from os.path import exists

waveLock = threading.Lock()
waves = []

doneLock = threading.Lock()
done = 0;

# Plotting constants
VERT_RES = 64 # Image height in px
MINFREQ = 1000 # The frequency for the bottom of the image
MAXFREQ = 10000 # The frequency for the top of the image
USE_LOG = False # Use a log scale for frequency
PX_DURATION = 100 # Make each pixel 100ms long
SAMPLE_RATE = 44100 # How many samples per second
MAX_AMPL = 1 # Maximum amplitude if brightness is 255
WORKER_THREADS = 32 # Number of worker threads

abc = 2

def main(stdscr):
    global done

    scrLock = threading.Lock()

    def addstr(x, y, str):
        with scrLock:
            stdscr.addstr(x, y, str)
            stdscr.refresh()

    def move(pos, max, dir):
        if 0 <= pos + dir < max:
            return pos + dir
        return pos

    global VERT_RES, MINFREQ, MAXFREQ, USE_LOG, PX_DURATION, SAMPLE_RATE, WORKER_THREADS

    inSettings = False;

    # Ask the user to give a filename
    addstr(0,0,"Image file to convert:")
    stdscr.move(1, 0)
    filepath = ""
    pathValid = False

    # Set up settings
    settingNum = 0;
    posy = 0;

    lablestr = [f"Vertical Resolution [px ]",
                f"Minimum frequency   [Hz ]",
                f"Maximum frequency   [Kz ]",
                f"Use log frequencies [T/F]",
                f"Pixel duration      [ms ]",
                f"Sample rate         [Hz ]",
                f"Worker threads      [num]"]
    valtype = [int, int, int, bool, int, int, int]
    q = abc + 1
    valstr = [VERT_RES, MINFREQ, MAXFREQ, USE_LOG, PX_DURATION, SAMPLE_RATE, WORKER_THREADS]

    settingsY = 4
    settingsX = 31
    afterSettingsY = 4

    addstr(settingsY-1,0,f"Settings:") # Image height in px
    for i in range(len(lablestr)):
        addstr(i+settingsY,0,f" {i}. {lablestr[i]} - {str(valstr[i])}") # Image height in px
        settingNum = i
    afterSettingsY = settingNum+settingsY+1
    stdscr.move(settingNum+settingsY, settingsX+len(str(valstr[settingNum])))

    addstr(afterSettingsY+1, 0, "Your file will be stored as .wav")
    addstr(afterSettingsY+3, 0, "Press ENTER to convert image")

    settingNum = 0;

    addstr(1,0,f"{filepath} .png")
    stdscr.move(1, len(filepath))

    # Respond to keypresses
    while not pathValid:
        # Get the key
        key = stdscr.getch()
        # Try to load the file if the key is enter
        if key == curses.KEY_ENTER or key == 10 or key == 13:
            addstr(2,0,f"Loading {filepath}.png ...")
            settingsOK = True
            for i in range(len(lablestr)):
                if not (type(valstr[i]) is valtype[i]):
                    settingsOK = False
                    errno = i
            if exists(filepath + ".png") and settingsOK:
                stdscr.move(2, 0)
                stdscr.clrtoeol()
                addstr(2,0,f"It works! ...")
                pathValid = True
            else:
                if settingsOK:
                    addstr(2,0,f"{filepath}.png does not exist. Please try again.")
                else:
                    addstr(2,0,f"Settings error, please try again. Error on line {errno}")
                stdscr.move(1, 0)
                curses.curs_set(0)
        # If we are in the settings menu ...
        elif inSettings:
            stdscr.move(settingNum+settingsY, settingsX+len(str(valstr[settingNum])))
            if key == curses.KEY_UP:
                if settingNum == 0:
                    inSettings = False;
                    stdscr.move(1, len(filepath))
                else:
                    settingNum = move(settingNum, len(lablestr), -1)
            elif key == curses.KEY_DOWN:
                settingNum = move(settingNum, len(lablestr),  1)
            elif key == 27:
                break;
            else:
                if valtype[settingNum] is int:
                    if key == curses.KEY_BACKSPACE or key == 127:
                        ist = str(valstr[settingNum])[0:-1]
                        if len(ist) > 0:
                            valstr[settingNum] = int(ist)
                        else:
                            valstr[settingNum] = ''
                    else:
                        if '0' <= chr(key) <= '9':
                            valstr[settingNum] = int(str(valstr[settingNum]) + chr(key))
                elif valtype[settingNum] is bool:
                    if chr(key) in "0fF":
                        valstr[settingNum] = False
                    elif chr(key) in "1tT":
                        valstr[settingNum] = True
                else:
                    if key == curses.KEY_BACKSPACE or key == 127:
                        valstr[settingNum] = valstr[settingNum][0:-1]
                    else:
                        if ' ' <= chr(key) <= '~':
                            valstr[settingNum] += chr(key)
                stdscr.move(settingNum+settingsY, settingsX+len(str(valstr[settingNum])))
                stdscr.clrtoeol()
                addstr(settingNum+settingsY,0,f" {lablestr[settingNum]} - {str(valstr[settingNum])}") # Image height in px
            stdscr.move(settingNum+settingsY, settingsX+len(str(valstr[settingNum])))
        # If we are typing the file name ...
        else:
            curses.curs_set(1)
            if key == curses.KEY_DOWN:
                inSettings = True;
                settingNum = 0
                stdscr.move(settingNum+settingsY, settingsX+len(str(valstr[settingNum])))
            else:
                if key == curses.KEY_BACKSPACE or key == 127:
                    filepath = filepath[0:-1]
                elif chr(key) in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_ ./":
                    filepath += chr(key)
                stdscr.move(2, 0)
                stdscr.clrtoeol()
                stdscr.move(afterSettingsY+1, 0)
                stdscr.clrtoeol()
                addstr(afterSettingsY+1, 0, f"Your file will be stored as {filepath}.wav")
                stdscr.move(1, 0)
                stdscr.clrtoeol()
                addstr(1,0,f"{filepath} .png")
                stdscr.move(1, len(filepath))
                stdscr.refresh()

    img = cv2.imread(filepath + '.png', -1)

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

    scaled = np.int16(data/np.max(np.abs(data)) * 32767)
    write(filepath + '.wav', 44100, scaled)

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

curses.wrapper(main)
