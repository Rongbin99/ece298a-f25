import wave, array, csv, sys

filename = sys.argv[1]  # CSV file name

sample_rate = 48000 # Hz
sample_period = 1.0 / sample_rate

samples = []
with open(filename, "r") as f:
    reader = csv.reader(f, delimiter=';')
    reader.__next__()  # skip header
    for row in reader:
        timestamp = float(row[0])  # in seconds
        voltage = float(row[1])    # in volts
        sample_value = int((voltage / 3.3) * 32767)  # scale to 16-bit
        if timestamp > len(samples) * sample_period:
            num_samples = int((timestamp - len(samples) * sample_period) / sample_period)
            samples.extend([sample_value] * num_samples)

# Write to WAV (16-bit PCM)
wavname = filename.rsplit('.', 1)[0] + ".wav"
with wave.open(wavname, "wb") as f:
    f.setnchannels(1)
    f.setsampwidth(2) # 2 byte samples
    f.setframerate(sample_rate)
    f.writeframes(array.array('h', samples).tobytes())
