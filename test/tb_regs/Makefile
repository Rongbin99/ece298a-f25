# Sub-block tests will be run for RTL sim only

SIM = icarus
TOPLEVEL_LANG = verilog
SRC_DIR = $(PWD)/../../src
PROJECT_SOURCES = register_interface.v sync.v

# RTL simulation:
SIM_BUILD		= sim_build/rtl
VERILOG_SOURCES += $(addprefix $(SRC_DIR)/,$(PROJECT_SOURCES))

# Include the testbench sources:
VERILOG_SOURCES += $(PWD)/tb.v
TOPLEVEL = tb

# MODULE is the basename of the Python test file
MODULE = regs_test

# include cocotb's make rules to take care of the simulator setup
include $(shell cocotb-config --makefiles)/Makefile.sim
