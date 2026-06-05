# Agentic RTL Verification Harness — AXI4-Stream
# Simulator: Icarus Verilog (iverilog)

SIM ?= icarus
TOPLEVEL_LANG ?= verilog
COCOTB_REDUCED_LOG_FMT ?= 1

TOPLEVEL := tb_top
MODULE ?= test_single_packet
DUT ?= stub

ifeq ($(DUT),reference)
  VERILOG_SOURCES := rtl/reference/axi4_stream_packet_monitor_ref.sv sim/tb_top.sv
  COMPILE_ARGS += -DUSE_REFERENCE_DUT
else
  VERILOG_SOURCES := rtl/axi4_stream_packet_monitor.sv sim/tb_top.sv
endif

SIM_BUILD := sim_build/$(DUT)/$(MODULE)

export PYTHONPATH := $(PWD)/tb:$(PYTHONPATH)
export COCOTB_TEST_MODULES := $(MODULE)

include $(shell cocotb-config --makefiles)/Makefile.sim

.PHONY: test test-ref clean-all

test:
	$(MAKE) sim MODULE=test_single_packet DUT=stub
	$(MAKE) sim MODULE=test_back_to_back DUT=stub
	$(MAKE) sim MODULE=test_async_reset DUT=stub

test-ref:
	$(MAKE) sim MODULE=test_single_packet DUT=reference
	$(MAKE) sim MODULE=test_back_to_back DUT=reference
	$(MAKE) sim MODULE=test_async_reset DUT=reference

clean-all: clean
	rm -rf sim_build
