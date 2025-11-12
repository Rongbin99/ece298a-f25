import wave, array, math

sample_rate = 28160 # Hz

freq = 220
half_step = pow(2, 1/12)
duration = 1.0 # seconds

accumulator = 0

samples = []
for i in range(37):
    accumulator_step = round((freq * (2 ** 14)) / sample_rate)
    print(accumulator_step)

    for n in range(int(sample_rate * duration)):
        accumulator = (accumulator + accumulator_step) % (2 ** 14)
        angle = round(accumulator / (2 ** 5)) / (2 ** 9) * 2 * math.pi
        x = math.sin(angle)
        samples.append(round(x * 32 + 32))
    
    freq *= half_step

# Write to WAV (8-bit PCM)
with wave.open("test.wav", "wb") as f:
    f.setnchannels(1)
    f.setsampwidth(1) # 1 byte = 8 bits
    f.setframerate(sample_rate)
    f.writeframes(array.array('B', samples).tobytes())
