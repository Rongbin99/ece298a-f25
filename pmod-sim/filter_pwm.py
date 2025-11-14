# apply a filter curve to a pwm signal
# python filter_pwm.py ../test/pwm_edges.log ./freq_response.csv output.wav

import sys
import csv
import numpy as np
from scipy.interpolate import make_interp_spline
import wave
import array

WAV_SAMPLE_RATE = 48000
PWM_SAMPLE_RATE = 28835840 # output sample rate

pwm_data = sys.argv[1]  # ../test/pwm_edges.log   format: time_ns,value
freq_data = sys.argv[2] # ./freq_response.csv   format: frequency;V(/Vout) (phase);V(/Vout) (gain);
out_name = sys.argv[3]  # output WAV filename

times = []
values = []
with open(pwm_data, 'r') as f:
    r = csv.reader(f)
    for t, v in r:
        times.append(float(t) * 1e-9)  # convert ns to s
        values.append(float(v))
times = np.array(times)
values = np.array(values)

duration = times[-1]

N = int(duration * PWM_SAMPLE_RATE)
t_uniform = np.linspace(0, duration, N)

# PWM is piecewise-constant, so use zero-order hold
# interp1d with 'previous' gives step function
interp = make_interp_spline(times, values, k=0)
x = interp(t_uniform)

freq = []
gain_db = []
phase_deg = []

with open(freq_data, 'r') as f:
    r = csv.reader(f, delimiter=';')
    for f_hz, p, g, _ in r:
        freq.append(float(f_hz))
        phase_deg.append(float(p))
        gain_db.append(float(g))

freq = np.array(freq)
gain = 10 ** (np.array(gain_db) / 20.0)
phase = np.deg2rad(phase_deg)

f_fft = np.fft.rfftfreq(N, 1/PWM_SAMPLE_RATE)

# Interpolate magnitude & phase separately
gain_interp = np.interp(f_fft, freq, gain)
phase_interp = np.interp(f_fft, freq, phase)

H_fft = gain_interp * np.exp(1j * phase_interp)

print("Starting FFT filtering...")

# apply filter in frequency domain
X = np.fft.rfft(x)
Y = X * H_fft
y = np.fft.irfft(Y)

print("Done FFT filtering...")

# interp Fs down to WAV_SAMPLE_RATE
num_wav_samples = int(len(y) * WAV_SAMPLE_RATE / PWM_SAMPLE_RATE)
y = np.interp(np.linspace(0, len(y), num_wav_samples, endpoint=False),
              np.arange(len(y)),
              y)

y_norm = y / np.max(np.abs(y)) * 0.95
samples = [int(v * 32767) for v in y_norm]

# Write to WAV (16-bit PCM)
wavname = out_name.rsplit('.', 1)[0] + ".wav"
with wave.open(wavname, "wb") as f:
    f.setnchannels(1)
    f.setsampwidth(2) # 2 byte samples
    f.setframerate(WAV_SAMPLE_RATE)
    f.writeframes(array.array('h', samples).tobytes())