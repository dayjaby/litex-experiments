test_include:
	riscv64-unknown-elf-gcc test_include.c -o test_include
	riscv64-unknown-elf-gdb -batch -ex "disassemble/rs main" test_include
test_include_with_subdir:
	riscv64-unknown-elf-gcc -I test_include_subdir test_include.c -o test_include_with_subdir
	riscv64-unknown-elf-gdb -batch -ex "disassemble/rs main" test_include_with_subdir
all: test_include
