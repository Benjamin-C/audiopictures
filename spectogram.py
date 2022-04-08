# You may have to run `pip install scipy`
from scipy.io import wavfile
from scipy.fft import fftshift
from scipy import signal

import matplotlib.pyplot as plt

samplerate, data = wavfile.read('../testsong.wav')

print(f"number of channels = {data.shape[1]}")

length = data.shape[0] / samplerate
print(f"length = {length}s")

print("Plotting ...")

plt.specgram(data[:,0], samplerate)

plt.ylabel('Frequency [Hz]')
plt.xlabel('Time [sec]')

plt.show()
