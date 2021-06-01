Virtual Environment
===================

It's recommended to run everything in a virtualenv:
```
sudo pip3 install virtualenvwrapper
source /usr/local/bin/virtualenvwrapper.sh
mkvirtualenv litex-env
echo "export ZEPHYR_BASE=$(pwd)/os/zephyr/zephyr" >> $VIRTUAL_ENV/bin/postactivate
deactivate
workon litex-env
# for zephyr support, please install:
pip3 install west pyelftools
cd litex
python3 litex_setup.py submodules
python3 litex_setup.py install
cd ..
```

Gateware
========

Generate arty gateware:

```
export LITEX_BOARD=arty
./litex/litex-boards/litex_boards/targets/$LITEX_BOARD.py \
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

Running NuttX on the Arty A7 has been tested with:

```
./litex/litex-boards/litex_boards/targets/$LITEX_BOARD.py \
  --toolchain vivado \
  --cpu-type vexriscv \
  --cpu-variant imac+debug \
  --with-etherbone \
  --csr-csv build/$LITEX_BOARD/csr.csv \
  --timer-uptime \
  --with-sdcard \
  --generated-dir os/nuttx/nuttx/arch/risc-v/src/litex/hardware/generated \
  --jinja-templates templates \
  --filter-templates csr_defines.h csr.h soc.h \
  --load

make nuttx
litex_term --serial-boot --kernel os/nuttx/nuttx/nuttx.bin /dev/ttyUSB1
```

Zephyr
------

Simulate in renode

```
renode scripts/single-node/arty_litex_zephyr.resc
(monitor) start
```

Running Zephyr OS on the Arty A7 has been tested with:

```
make zephyr
litex_term --serial-boot --kernel build/zephyr/zephyr.bin /dev/ttyUSB1
```

More examples in /opt/renode.
