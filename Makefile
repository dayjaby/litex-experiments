nuttx:
	os/nuttx/nuttx/tools/configure.sh -E -l arty_a7:nsh
	cp build/arty/software/include/generated/csr_defines.h os/nuttx/nuttx/arch/risc-v/src/litex/hardware
	make -C os/nuttx/nuttx

nuttx-clean:
	make -C os/nuttx/nuttx distclean

clean: nuttx-clean

