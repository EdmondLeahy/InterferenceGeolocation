import numpy as np
import numpy.random as rnd
import matplotlib.pyplot as plt

rnd.seed(0)

PIT = 1  # Process Time
Fs = 10e3  # Sampling Freq
Freq = 100  # Jammer Freq
NumSamples = PIT * Fs  # Number of samples to process
t = np.arange(0, NumSamples - 1, 1) / Fs  # time samples
f = np.arange(0, NumSamples - 1, 1) / PIT  # Frequency Samples
CW = 1 * np.exp(2j * np.pi * Freq * t)  # Simulate a complex sin signal with frequency of 500

##################################
var = 10
InputSignal = CW + np.sqrt(var) * rnd.randn(len(CW)) + np.sqrt(var) * 1j * rnd.randn(
    len(CW))  ## Adding noise to the CW signal with Variance of var

PythonFFT = abs(np.fft.fft(InputSignal))

## Correaltion process

Corroutput = [abs(sum(InputSignal * np.exp(-2j * np.pi * f_k * t))) for f_k in f]
# for k in np.arange(len(t)):
#     Corroutput.append(abs(sum(InputSignal * np.exp(-2j * np.pi * f[k] * t))))

### plot
plt.figure(1)
plt.plot(t, InputSignal.real)
plt.plot(t, CW.real)
plt.legend(['Received', 'Transmitted'])
plt.ylim(-15, 15)

plt.figure(2)
plt.plot(f, PythonFFT)
plt.plot(f, Corroutput)
plt.legend(['FFT', 'Correlation Process'])
plt.xlabel('Frequency (Hz)')

plt.show()

