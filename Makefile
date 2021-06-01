zephyr_app = os/zephyr/zephyr/samples/cpp_synchronization
os_list = zephyr nuttx
os_main = nuttx
LITEX_BOARD = arty

default: $(os_main)

litex-load:
	./litex/litex-boards/litex_boards/targets/$(LITEX_BOARD).py \
  		--toolchain vivado \
  		--cpu-type vexriscv \
  		--cpu-variant imac+debug \
  		--with-etherbone \
  		--csr-csv build/$(LITEX_BOARD)/csr.csv \
		--analyzer-csv build/$(LITEX_BOARD)/analyzer.csv \
  		--timer-uptime \
  		--with-sdcard \
  		--generated-dir os/nuttx/nuttx/arch/risc-v/src/litex/hardware/generated \
  		--jinja-templates templates \
  		--filter-templates csr_defines.h csr.h soc.h \
  		--load

litex-build:
	./litex/litex-boards/litex_boards/targets/$(LITEX_BOARD).py \
  		--toolchain vivado \
  		--cpu-type vexriscv \
  		--cpu-variant imac+debug \
  		--with-etherbone \
  		--csr-csv build/$(LITEX_BOARD)/csr.csv \
		--analyzer-csv build/$(LITEX_BOARD)/analyzer.csv \
  		--timer-uptime \
  		--with-sdcard \
  		--generated-dir os/nuttx/nuttx/arch/risc-v/src/litex/hardware/generated \
  		--jinja-templates templates \
  		--filter-templates csr_defines.h csr.h soc.h \
  		--build

zephyr:
	west build -p auto -b litex_vexriscv $(zephyr_app)

zephyr-clean:
	west build -t clean -p auto -b litex_vexriscv $(zephyr_app)

zephyr-distclean:
	west build -t pristine -p auto -b litex_vexriscv $(zephyr_app)

zephyr-flash:
	litex_term --serial-boot --kernel build/zephyr/zephyr.bin /dev/ttyUSB1

nuttx:
	@os/nuttx/nuttx/tools/configure.sh -l arty_a7:nsh
	make -C os/nuttx/nuttx

nuttx-clean:
	make -C os/nuttx/nuttx clean

nuttx-distclean:
	make -C os/nuttx/nuttx distclean

nuttx-flash:
	litex_term --serial-boot --kernel os/nuttx/nuttx/nuttx.bin /dev/ttyUSB1

clean: $(os_main)-clean

distclean: $(os_main)-distclean

flash: $(os_main)-flash
