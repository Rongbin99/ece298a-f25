from vcd.reader import TokenKind, Token
import vcd.reader
import sys

vcd_file = "tb.vcd"
# $var wire 8 - uo_out [7:0] $end
signal_name = "uo_out"  # the signal to extract
signal_scope = "tb"  # the signal to extract
VDD = 3.3                  # logic high voltage

# Open VCD
with open(vcd_file, "rb") as f:
    tokens = list(vcd.reader.tokenize(f))

# Find the signal identifier
signal_id = None
for t in tokens:
    if t.kind == TokenKind.DECLARE:
        if t.reference == signal_name and t.scope == signal_scope:
            signal_id = t.identifier
            break
if signal_id is None:
    raise ValueError(f"Signal {signal_name} not found in VCD.")

# Extract time/value changes
time = 0
pwl_data = []
for t in tokens:
    if t.kind == TokenKind.TIMESTAMP:
        time = t.tv * 1e-9  # convert ns → s if needed
    elif t.kind == TokenKind.CHANGE and t.identifier == signal_id:
        val = t.tv
        if val == '0':
            voltage = 0.0
        elif val == '1':
            voltage = VDD
        else:
            voltage = 0.0  # or skip/NaN
        pwl_data.append((time, voltage))

# Write to PWL file
with open("input_waveform.txt", "w") as f:
    for t, v in pwl_data:
        f.write(f"{t:.9f} {v:.6f}\n")

print("PWL file generated: input_waveform.txt")
