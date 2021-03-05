Gateware
========

Generate arty gateware:

```
export LITEX_BOARD=arty
./litex-boards/litex_boards/targets/$LITEX_BOARD.py \
  --toolchain vivado \
  --cpu-type vexriscv \
  --cpu-variant imac+debug \
  --with-etherbone \
  --csr-csv build/$LITEX_BOARD/csr.csv \
  --timer-uptime \
  --with-sdcard \
  --build
```

Generate resc and repl files:

```
./litex-renode/generate-renode-scripts.py \
  build/$LITEX_BOARD/csr.csv \
  --resc scripts/single-node/${LITEX_BOARD}_litex.resc \
  --repl platforms/cpus/${LITEX_BOARD}_litex.repl \
  --bios-binary build/$LITEX_BOARD/software/bios/bios.bin
```

Software
========

Baremetal
---------

Creating the baremetal demo:

```
litex_bare_metal_demo --build-path=build/arty
cp demo/demo.elf firmwares/
rm -rf demo*
```

Simulate in renode

```
renode scripts/single-node/arty_litex_demo.resc
(monitor) start
```

NuttX
-----

```
git submodule update --init --recursive
export LITEX_PATH=$(python -c "import litex; print(litex.__path__[0])")
make nuttx
```

Simulate in renode

```
renode scripts/single-node/arty_litex_nuttx.resc
(monitor) start
```

WIP: write SD card driver. Create the csr.h file for nuttx:

```
./litex-boards/litex_boards/targets/$LITEX_BOARD.py \
  --toolchain vivado \
  --cpu-type vexriscv \
  --cpu-variant imac+debug \
  --with-etherbone \
  --csr-csv build/$LITEX_BOARD/csr.csv \
  --timer-uptime \
  --with-sdcard \
  --generated-dir os/nuttx/nuttx/arch/risc-v/src/litex/hardware \
  --jinja-templates templates \
  --filter-templates csr_defines.h csr.h soc.h \
  --load
```

Zephyr
------

Simulate in renode

```
renode scripts/single-node/arty_litex_zephyr.resc
(monitor) start
```

More examples in /opt/renode.
