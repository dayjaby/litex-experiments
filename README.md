Generate arty gateware and software in litex_boards folder:

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

Example call:

```
renode scripts/single-node/arty_litex_nuttx.resc
(monitor) start
```

More examples in /opt/renode.
