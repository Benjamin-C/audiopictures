# You may have to run `pip install scipy`

# https://matplotlib.org/3.5.0/api/_as_gen/matplotlib.pyplot.specgram.html
from scipy.io import wavfile
from scipy.fft import fftshift
from scipy import signal

import matplotlib.pyplot as plt

samplerate, data = wavfile.read('../testsong.wav')

print(f"number of channels = {data.shape[1]}")

length = data.shape[0] / samplerate
print(f"length = {length}s")

print("Plotting ...")

plt.specgram(data[:,0], Fs=samplerate)

plt.ylabel('Frequency [Hz]')
plt.xlabel('Time [sec]')

plt.show()
