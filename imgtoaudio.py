# imagetoaudio.py
#
# Converts a png image into an audio signal whos spectogram strongly resembles the image.
# Only supports PNG inputs and WAV outputs. Need something else? Convert!
#
# Author: Benjamin Crall
# This program is liscensed under GNU GENERAL PUBLIC LICENSE Version 3
#
# This program requires several Python libraries that are not standard.
# This is (at a minimum)
#   scipy
#   matplotlib
#   numpy
#   OpenCV
# You may have to run `pip install scipy matplotlib numpy opencv-python`

# Load and process image files
import cv2
# Process data faster
import numpy as np
# Save audio file
from scipy.io.wavfile import write
# Use multiple threads for rendering
import threading
# Pretty display
import curses
# Plot spectogram
import matplotlib.pyplot as plt
# Sleep sometimes
import time
# Check if files exist
from os.path import exists

# Count how many of the threads are done
doneLock = threading.Lock()
done = 0;

# Plotting paramaters
VERT_RES = 64 # Image height in px
MINFREQ = 1000 # The frequency for the bottom of the image
MAXFREQ = 10000 # The frequency for the top of the image
USE_LOG = False # Use a log scale for frequency
PX_DURATION = 100 # Make each pixel 100ms long
SAMPLE_RATE = 44100 # How many samples per second
WORKER_THREADS = 32 # Number of worker threads
SHOW_IMAGE = False # To show the modified image that is converted
SHOW_RESULT = False # To show the converted spectogram

# ███    ███  █████  ██ ███    ██
# ████  ████ ██   ██ ██ ████   ██
# ██ ████ ██ ███████ ██ ██ ██  ██
# ██  ██  ██ ██   ██ ██ ██  ██ ██
# ██      ██ ██   ██ ██ ██   ████
# Do da thingy
def main(stdscr):
    # Global vars including settings and thread counter
    global done, VERT_RES, MINFREQ, MAXFREQ, USE_LOG, PX_DURATION, SAMPLE_RATE, WORKER_THREADS, SHOW_IMAGE, SHOW_RESULT

    # Lock the screen from being written to by multiple threads simultaionusly
    screenLock = threading.Lock()

    # Adds a string to the screen somewhere and refresh
    def addstr(x, y, str):
        with screenLock:
            stdscr.addstr(x, y, str)
            stdscr.refresh()

# ██    ██ ███████ ███████ ██████      ██ ███    ██ ██████  ██    ██ ████████
# ██    ██ ██      ██      ██   ██     ██ ████   ██ ██   ██ ██    ██    ██
# ██    ██ ███████ █████   ██████      ██ ██ ██  ██ ██████  ██    ██    ██
# ██    ██      ██ ██      ██   ██     ██ ██  ██ ██ ██      ██    ██    ██
#  ██████  ███████ ███████ ██   ██     ██ ██   ████ ██       ██████     ██
# Get the input filename and settings from the user

    # If the user is in the settings menu
    inSettings = False;

    # Ask the user to give a filename
    addstr(0,0,"Image file to convert:")
    stdscr.move(1, 0)
    filepath = ""
    pathValid = False

    # Set up settings
    settingNum = 0;

    # The labels for the settings. Must be 20 characters text, then " [UUU]" where UUU is the unit
    lablestr = [f"Vertical Resolution  [px ]",
                f"Minimum frequency    [Hz ]",
                f"Maximum frequency    [Kz ]",
                f"Use log frequencies  [T/F]",
                f"Pixel duration       [ms ]",
                f"Sample rate          [Hz ]",
                f"Worker threads       [num]",
                f"Show image           [T/F]",
                f"Show result          [T/F]",]
    # The types of the values the settings can allow. Can be int, bool, or anything else means string
    valtype = [int, int, int, bool, int, int, int, bool, bool]
    # The variables that hold the settings
    valstr = [VERT_RES, MINFREQ, MAXFREQ, USE_LOG, PX_DURATION, SAMPLE_RATE, WORKER_THREADS, SHOW_IMAGE, SHOW_RESULT]

    # How many rows down to start settings
    settingsY = 4
    # How wide the settings labels are
    settingsX = 33
    # The first row after the settings section. Autoset later
    afterSettingsY = 4

    # Prints a row of settings
    def printSettingsRow(row):
        addstr(row+settingsY,0,f" {row}. {lablestr[row]} - {str(valstr[row])}") # Image height in px

    addstr(settingsY-1,0,f"Settings:")
    # Print all settings
    for i in range(len(lablestr)):
        printSettingsRow(i)
        settingNum = i
    afterSettingsY = settingNum+settingsY+1
    stdscr.move(settingNum+settingsY, settingsX+len(str(valstr[settingNum])))

    addstr(afterSettingsY+1, 0, "Your file will be stored as .wav")
    addstr(afterSettingsY+3, 0, "Press ENTER to convert image")

    settingNum = 0;

    # Always have .png as the end of the filepath
    addstr(1,0,f"{filepath} .png")
    stdscr.move(1, len(filepath))

    # Respond to keypresses
    while not pathValid:
        # Get the key
        key = stdscr.getch()
        curses.curs_set(1)
        # Try to load the file if the key is enter
        if key == curses.KEY_ENTER or key == 10 or key == 13:
            addstr(2,0,f"Loading {filepath}.png ...")
            # Check if all settings are of the right type
            settingsOK = True
            for i in range(len(lablestr)):
                if not (type(valstr[i]) is valtype[i]):
                    settingsOK = False
                    errno = i
            # Break out of the loop if the file and settings are OK
            if exists(filepath + ".png") and settingsOK:
                stdscr.move(2, 0)
                stdscr.clrtoeol()
                addstr(2,0,f"It works! ...")
                pathValid = True
                break
            else:
                # If filename or settings are not OK, say why
                if settingsOK:
                    addstr(2,0,f"{filepath}.png does not exist. Please try again.")
                else:
                    addstr(2,0,f"Settings error, please try again. Error on line {errno}")
                stdscr.move(1, 0)
                curses.curs_set(0)
        # If we are in the settings menu ...
        elif inSettings:
            # Move up and down
            if key == curses.KEY_UP:
                if settingNum == 0:
                    # Go to file name
                    inSettings = False;
                    stdscr.move(1, len(filepath))
                else:
                    if settingNum > 0:
                        settingNum -= 1
            elif key == curses.KEY_DOWN:
                if settingNum < len(lablestr) - 1:
                    settingNum += 1
            # Type
            else:
                # Validate key based on allowed types
                if valtype[settingNum] is int:
                    if key == curses.KEY_BACKSPACE or key == 127:
                        # String magic to remove the last character
                        ist = str(valstr[settingNum])[0:-1]
                        # Hackery to allow int fields to be empty sometimes
                        if len(ist) > 0:
                            valstr[settingNum] = int(ist)
                        else:
                            valstr[settingNum] = ''
                    else:
                        if '0' <= chr(key) <= '9':
                            # String magic to add a character
                            valstr[settingNum] = int(str(valstr[settingNum]) + chr(key))
                elif valtype[settingNum] is bool:
                    # Allow changing bools with only a few specific keys
                    if chr(key) in "0fF":
                        valstr[settingNum] = False
                    elif chr(key) in "1tT":
                        valstr[settingNum] = True
                else: # If we don't know what it is, assume a string
                    if key == curses.KEY_BACKSPACE or key == 127:
                        valstr[settingNum] = valstr[settingNum][0:-1]
                    else:
                        if ' ' <= chr(key) <= '~':
                            valstr[settingNum] += chr(key)
                # Print the new value of the setting
                stdscr.move(settingNum+settingsY, settingsX+len(str(valstr[settingNum])))
                stdscr.clrtoeol()
                printSettingsRow(settingNum);
            # Make sure the cursor is at the end of the line
            stdscr.move(settingNum+settingsY, settingsX+len(str(valstr[settingNum])))
        # If we are typing the file name ...
        else:
            if key == curses.KEY_DOWN:
                # Go to settings
                inSettings = True;
                settingNum = 0
                stdscr.move(settingNum+settingsY, settingsX+len(str(valstr[settingNum])))
            else: # Type
                if key == curses.KEY_BACKSPACE or key == 127:
                    filepath = filepath[0:-1]
                elif chr(key) in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_ ./":
                    filepath += chr(key)
                # Remove error message
                stdscr.move(2, 0)
                stdscr.clrtoeol()
                # Update the result filename
                stdscr.move(afterSettingsY+1, 0)
                stdscr.clrtoeol()
                addstr(afterSettingsY+1, 0, f"Your file will be stored as {filepath}.wav")
                # Update the input filename
                stdscr.move(1, 0)
                stdscr.clrtoeol()
                addstr(1,0,f"{filepath} .png")
                stdscr.move(1, len(filepath))
                stdscr.refresh()

# ██       ██████   ██████ ██████  ██ ███    ██  ██████
# ██      ██    ██ ██      ██   ██ ██ ████   ██ ██
# ██      ██    ██ ██      ██   ██ ██ ██ ██  ██ ██   ███
# ██      ██    ██ ██      ██   ██ ██ ██  ██ ██ ██    ██
# ███████  ██████   ██████ ██████  ██ ██   ████  ██████
# Once the user gets here, they have provided (probably) valid settings and a filename, so load the file

    # Load the image
    img = cv2.imread(filepath + '.png', -1)

    # Resize the image to the specified height keeping aspect ratio
    width = int((VERT_RES / len(img)) * len(img[0]))
    height = VERT_RES
    img = cv2.resize(img, (width, height))

    # Convert the image to greyscale and invert it for better spectograms
    addstr(0, 0, "Graying ...        ")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.bitwise_not(gray)
    img_data = gray2

    # Fill any transparent areas with blackness
    addstr(0, 0, "Filling ...        ")
    for y in range(len(img)):
        for x in range(len(img[y])):
            if img[y][x][3] == 0:
                gray2[y][x] = 0

    # Generate the lists of frequencies and pregenerated sine waves
    addstr(0, 0, "Generating ...        ")

    # Calculate the set of freqencies for each row
    freqs = []
    if USE_LOG:
        minlog = np.log10(MINFREQ)
        maxlog = np.log10(MAXFREQ)
        logvals = np.linspace(minlog, maxlog, VERT_RES, False)
        freqs = np.power(10, logvals)
    else:
        freqs = np.linspace(MINFREQ, MAXFREQ, VERT_RES, False)

    # How many samples each pixel is
    samplecount = int(SAMPLE_RATE * (PX_DURATION/1000))
    # The time in seconds that each sample is at to be used in sine calculations later
    times = np.linspace(0, PX_DURATION/1000, samplecount)

    # Pregenerate sine waves that can just be added in fast later
    waves = []
    for f in freqs:
        waves.append(np.sin(2 * np.pi * f * times))

# ████████ ██   ██ ██████  ███████  █████  ██████  ██ ███    ██  ██████
#    ██    ██   ██ ██   ██ ██      ██   ██ ██   ██ ██ ████   ██ ██
#    ██    ███████ ██████  █████   ███████ ██   ██ ██ ██ ██  ██ ██   ███
#    ██    ██   ██ ██   ██ ██      ██   ██ ██   ██ ██ ██  ██ ██ ██    ██
#    ██    ██   ██ ██   ██ ███████ ██   ██ ██████  ██ ██   ████  ██████
# Helper functions to make multithreading easier. Maybe should be their own file? If so, too bad.

    # Sets a character representing the threaded task so the user can see what's going on
    def setRowCh(y, ch):
        with screenLock:
            width = WORKER_THREADS if WORKER_THREADS < 32 else 32
            stdscr.addch((y // width) + 1, (y % width) + 1, ch)
            stdscr.refresh()

    # Counting how many threads have completed in total
    alldone = 0

    # Spawn a bunch of threads doing work
    def useThreads(max, target, text):
        stdscr.clear()

        # Use the global version so it matches with the version the threads use
        global done, alldone
        done = 0
        alldone = 0

        # Start with everything as dots
        for y in range(max):
            setRowCh(y, '.')

        for y in range(max):
            try:
                # What will actually be run
                def threadFunc(num):
                    # Mark the thread as in progress
                    setRowCh(num, '+')
                    global done, alldone
                    # Do whatever the work is that needs to be done
                    target(num)
                    # Mark that we're done
                    with doneLock:
                        done += 1
                        alldone += 1
                    setRowCh(num, '#')
                # Create and start the thread, passing its number as the argument
                t1 = threading.Thread(target=threadFunc, args=(y,))
                t1.start()
            except:
                # AAAAAAAAAAA that's not good
                print("Error: unable to start thread")
            # Wait so these threads can finish before spawning more
            if y % WORKER_THREADS == WORKER_THREADS - 1:
                addstr(0, 0, f"{text} ...        ")
                while done < WORKER_THREADS:
                    time.sleep(0.01) # Take a very short nap
                done = 0;
                addstr(0, 0, "Starting ...        ")

        # Wait for everyone to be done before returning
        addstr(0, 0, f"{text} ...        ")
        while alldone < max:
            time.sleep(0.5)

# ██████  ███████ ███    ██ ██████  ███████ ██████  ██ ███    ██  ██████
# ██   ██ ██      ████   ██ ██   ██ ██      ██   ██ ██ ████   ██ ██
# ██████  █████   ██ ██  ██ ██   ██ █████   ██████  ██ ██ ██  ██ ██   ███
# ██   ██ ██      ██  ██ ██ ██   ██ ██      ██   ██ ██ ██  ██ ██ ██    ██
# ██   ██ ███████ ██   ████ ██████  ███████ ██   ██ ██ ██   ████  ██████
# Actually combine the sine waves

    # Start each column with the right amount of nothing
    zro = np.zeros(samplecount)

    # Use threading to render the image as audio
    # Calculates the frequencies for each column
    # List to hold each block (column of pixels) to be comboned later
    # Not combining now lets us render in paralell
    blockdata = []
    for i in range(width):
        blockdata.append(None)

    # Function that actually renders
    def calcCol(num):
        # Start with empty
        block = np.copy(zro)
        for row in range(VERT_RES):
            # Figure out which frequency index this pixel should be
            frequency = VERT_RES - row - 1
            # Scale this pixels intensity to 0-1
            amplitude = (img_data[row][num] / 255) # 255 is the max pixel value
            # Scale the sine wave to the right size
            # This assummes that scaling should be linear. If not, too bad.
            thiswave = amplitude * waves[frequency]
            # Add this sine wave to the current block
            block += thiswave
        # Store the block for later combining
        blockdata[num] = block

    # Use many threads to render the image
    useThreads(width, calcCol, "Rendering")
    stdscr.clear()

    # Combine the segments into one massive array
    addstr(0, 0, "Combining ...        ")
    data = []
    for blocknum in range(width):
        data = np.append(data, blockdata[blocknum])

# ███████  █████  ██    ██ ██ ███    ██  ██████
# ██      ██   ██ ██    ██ ██ ████   ██ ██
# ███████ ███████ ██    ██ ██ ██ ██  ██ ██   ███
#      ██ ██   ██  ██  ██  ██ ██  ██ ██ ██    ██
# ███████ ██   ██   ████   ██ ██   ████  ██████
# Save the data

    # Scale the wave file to full scale and save it
    addstr(0, 0, "Saving ...        ")
    scaled = np.int16(data/np.max(np.abs(data)) * 32767)
    write(filepath + '.wav', SAMPLE_RATE, scaled)
    addstr(0, 0, f"Image saved to {filepath}.wav")

    # Show the image the user provided if they want it
    if SHOW_IMAGE:
        cv2.imshow('image', cv2.resize(gray2, (512, 512), interpolation= cv2.INTER_NEAREST))

    # Show the spectogram if the user wants it
    if SHOW_RESULT:
        plt.specgram(data, Fs=SAMPLE_RATE)
        ax = plt.gca()
        ax.set_ylim([0, MAXFREQ])
        plt.show()

    # Let the user see the filename before exiting
    addstr(1, 0, "Press any key to exit")
    stdscr.getch()

if __name__ == '__main__':
    curses.wrapper(main)
    print("Done.")
