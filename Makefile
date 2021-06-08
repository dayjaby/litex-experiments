zephyr_app = os/zephyr/zephyr/samples/cpp_synchronization
os_list = zephyr nuttx
os_main = nuttx
LITEX_BOARD = arty
LITEX_CMD = load
ethernet_iface = enx00e04e716421
target_ip = 192.168.1.50
usb_port = /dev/usb_ftdi_1

default: $(os_main)

litex:
	./litex/litex-boards/litex_boards/targets/$(LITEX_BOARD).py \
  		--toolchain vivado \
  		--cpu-type vexriscv \
  		--cpu-variant imac+debug \
  		--with-etherbone \
  		--csr-csv build/$(LITEX_BOARD)/csr.csv \
		--analyzer-csv build/$(LITEX_BOARD)/analyzer.csv \
  		--timer-uptime \
  		--$(LITEX_CMD)

litex-build: 
	$(MAKE) -B LITEX_CMD=build litex

litex-load:
	$(MAKE) -B LITEX_CMD=load litex

litex-flash:
	$(MAKE) -B LITEX_CMD=flash litex

litex-scope:
	./litescope_analyzer.py
	gtkwave dump.vcd
	rm dump.vcd

litex-shell:
	litex_term --serial-boot $(usb_port)

litex-server:
	litex_server --uart --uart-port $(usb_port)

litex-server-udp:
	litex_server --udp --udp-ip $(target_ip)

litex-gdb-server:
	wishbone-tool --ethernet-host $(target_ip) --csr-csv build/$(LITEX_BOARD)/csr.csv -s gdb

litex-gdb-client:
	riscv32-unknown-linux-gnu-gdb build/$(LITEX_BOARD)/software/bios/bios.elf -ex "target remote :3333"

zephyr:
	west build -p auto -b litex_vexriscv $(zephyr_app)

zephyr-clean:
	west build -t clean -p auto -b litex_vexriscv $(zephyr_app)

zephyr-distclean:
	west build -t pristine -p auto -b litex_vexriscv $(zephyr_app)

zephyr-flash:
	litex_term --serial-boot --kernel build/zephyr/zephyr.bin $(usb_port)

nuttx:
	@os/nuttx/nuttx/tools/configure.sh -l arty_a7:nsh
	make -C os/nuttx/nuttx

nuttx-clean:
	make -C os/nuttx/nuttx clean

nuttx-distclean:
	make -C os/nuttx/nuttx distclean

nuttx-flash:
	litex_term --serial-boot --kernel os/nuttx/nuttx/nuttx.bin $(usb_port)

clean: $(os_main)-clean

distclean: $(os_main)-distclean

flash: $(os_main)-flash
