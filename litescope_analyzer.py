#!/usr/bin/env python3 
import sys
import argparse 
from litex import RemoteClient
from litescope import LiteScopeAnalyzerDriver

parser = argparse.ArgumentParser()
parser.add_argument("--ibus_adr",  default=0x00000000,  help="Trigger on IBus Adr value.")
parser.add_argument("--offset",    default=128,         help="Capture Offset.")
parser.add_argument("--length",    default=1024,         help="Capture Length.")
args = parser.parse_args()

wb = RemoteClient(csr_csv="build/arty/csr.csv")
wb.open()

# # #

analyzer = LiteScopeAnalyzerDriver(wb.regs, "analyzer", debug=True, config_csv="build/arty/analyzer.csv")
#analyzer.configure_subsampler(10)
analyzer.configure_group(0)
#analyzer.add_rising_edge_trigger("basesoc_spimaster_status_status")

analyzer.add_rising_edge_trigger("dw1000_spi_clk")
#analyzer.add_rising_edge_trigger("dw1000_spi_cs_n")
#analyzer.add_rising_edge_trigger("main_basesoc_spimaster_cs_storage")
#analyzer.add_falling_edge_trigger("spi_miso")

#analyzer.configure_trigger(cond={"main_basesoc_cpu_ibus_ibus_adr": hex(args.ibus_adr)})
#analyzer.configure_trigger(cond={"main_basesoc_ibus_ibus_adr": bin(0xea0)})
#analyzer.configure_trigger(cond={"spi_mosi": bin(ord("h"))})
analyzer.run(offset=int(args.offset), length=int(args.length))

analyzer.wait_done()
analyzer.upload()
analyzer.save("dump.vcd")

# # #

wb.close()
