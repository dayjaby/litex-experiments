nuttx:
	@os/nuttx/nuttx/tools/configure.sh -l arty_a7:nsh
	make -C os/nuttx/nuttx

nuttx-clean:
	make -C os/nuttx/nuttx distclean

clean: nuttx-clean

