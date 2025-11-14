from vcd.reader import TokenKind
import vcd.reader
import sys

step = int(sys.argv[1])
print("time step (ns):", step)

vcd_file = "../test/tb.vcd"
VDD = 3.3                  # logic high voltage

# Open VCD
with open(vcd_file, "rb") as f:
    tokens = list(vcd.reader.tokenize(f))

print(f"file tokenized")

# Extract time/value changes
time = 0
pwl_data = []
for t in tokens:
    if t.kind == TokenKind.CHANGE_TIME:
        time = t.time_change * 1e-12  # convert ps to s
    elif t.kind == TokenKind.CHANGE_SCALAR:
        val = t.scalar_change.value
        if val == "0":
            pwl_data.append((time-step*1e-9, VDD))
            pwl_data.append((time, 0))
        elif val == "1":
            pwl_data.append((time-step*1e-9, 0))
            pwl_data.append((time, VDD))
        else:
            print("unexpected value:", val)

# Write to PWL file
with open("input_waveform.txt", "w") as f:
    for t, v in pwl_data:
        f.write(f"{t:.9f} {v:.6f}\n")

print("PWL file generated: input_waveform.txt")