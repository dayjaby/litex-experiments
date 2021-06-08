#!/usr/bin/env python3

import os
import sys
import subprocess
import shutil
import hashlib
from collections import OrderedDict

import urllib.request

current_path = os.path.abspath(os.curdir)
# Check location (is litex_setup.py executed inside a cloned LiteX repository or alongside?)
if os.path.exists(".gitignore"):
    current_path = os.path.join(current_path, "../")

# Repositories -------------------------------------------------------------------------------------

# name,  (url, recursive clone, develop, sha1)
repos = [
    # HDL
    ("migen",        ("https://github.com/m-labs/",        True,  True, 0x7014bdccc11270764186e6a4441fb58238c612aa)),
    ("nmigen",       ("https://github.com/nmigen/",        True,  True, 0xf7c2b9419f9de450be76a0e9cf681931295df65f)),

    # LiteX SoC builder
    ("pythondata-software-compiler_rt", ("https://github.com/litex-hub/",     False, True, 0xfcb03245613ccf3079cc833a701f13d0beaae09d)),
    ("litex",                           ("https://github.com/dayjaby/", False, True, 0x98836a5e130552d8245752f5251c48d7ea84634e)),

    # LiteX cores ecosystem
    ("liteeth",      ("https://github.com/enjoy-digital/", False, True, 0x89b197d1a05e9d3049ae53a40cb4294202a9f6c1)),
    ("litedram",     ("https://github.com/enjoy-digital/", False, True, 0x5ce6bf782458ad6ec86a94b2c14be033e0856ce8)),
    ("litepcie",     ("https://github.com/enjoy-digital/", False, True, 0x01d7b584e8c222ba986b4c8f939d690b9c6f6f7c)),
    ("litesata",     ("https://github.com/enjoy-digital/", False, True, 0xbaf5dc60711f68fa99b53a928dc60e35edb1bb13)),
    ("litesdcard",   ("https://github.com/enjoy-digital/", False, True, 0x17f6216caa1dc156546ebd4208082aca35b16221)),
    ("liteiclink",   ("https://github.com/enjoy-digital/", False, True, 0x0980a7cf4ffcb0b69a84fa0343a66180408b2a91)),
    ("litevideo",    ("https://github.com/enjoy-digital/", False, True, 0x41f30143075ece3fff5c33a332ed067d1837cbb3)),
    ("litescope",    ("https://github.com/dayjaby/", False, True, 0xe4ed47deb51790ebfa47e06205da3d8ad1a34afa)),
    ("litejesd204b", ("https://github.com/enjoy-digital/", False, True, 0xc7d4892cb75129b953f91d6ee575c87b697e04ef)),
    ("litespi",      ("https://github.com/litex-hub/",     False, True, 0x55926a6c035da37123fa467779a6b72cdd26d061)),
    ("litehyperbus", ("https://github.com/litex-hub/",     False, True, 0x5282d5167c4c91984b614febdb062450b26aec52)),

    # LiteX boards support
    ("litex-boards", ("https://github.com/dayjaby/",     False, True, 0xc6ad002464efc9a847d0da8af3d15f2a78c0a6de)),

    # Optional LiteX data
    ("pythondata-misc-tapcfg",     ("https://github.com/litex-hub/", False, True, 0x0e6809132b7a42d26fc148b2b5e54ede8d6021ab)),
    ("pythondata-misc-opentitan",  ("https://github.com/litex-hub/", False, True, 0x26c58de6e8521f0eba3d71dfbbce8abd679cdf7c)),
    ("pythondata-cpu-lm32",        ("https://github.com/litex-hub/", False, True, 0xcac2e4178e4ca44e60a368a22d5ea828b2647197)),
    ("pythondata-cpu-mor1kx",      ("https://github.com/litex-hub/", False, True, 0xc64530f429a2387ec2e11b79debd30cb8ff1bf76)),
    ("pythondata-cpu-picorv32",    ("https://github.com/litex-hub/", False, True, 0xb6b3f4b1c3e94efba9500d8fcfe523f12e0dae39)),
    ("pythondata-cpu-serv",        ("https://github.com/litex-hub/", False, True, 0xaad920fb4b4da33a4e08184882dc2e8498553f93)),
    ("pythondata-cpu-vexriscv",    ("https://github.com/litex-hub/", False, True, 0x7f9db486d402066f6adee5028ae031f09145f4be)),
    ("pythondata-cpu-vexriscv-smp",("https://github.com/litex-hub/", True,  True, 0x26cf32e65008e086f2a3051204927e4d472b8866)),
    ("pythondata-cpu-rocket",      ("https://github.com/litex-hub/", False, True, 0x8a34e1316ebf5588d9bea7dc930e89165bd94e54)),
    ("pythondata-cpu-minerva",     ("https://github.com/litex-hub/", False, True, 0x2d584d998132d773e3b02c325351734733d60bab)),
    ("pythondata-cpu-microwatt",   ("https://github.com/litex-hub/", False, True, 0xf9807b6de50aab8b264f0bc9a945e42f1a636456)),
    ("pythondata-cpu-blackparrot", ("https://github.com/litex-hub/", False, True, 0x4264d9b0ee43dbb04a94260a6cf9063202996537)),
    ("pythondata-cpu-cv32e40p",    ("https://github.com/litex-hub/", True,  True, 0x91748b7ebc36e1d3a34c1173420510d7c788b651)),
]

repos = OrderedDict(repos)

# RISC-V toolchain download ------------------------------------------------------------------------

def sifive_riscv_download():
    base_url  = "https://static.dev.sifive.com/dev-tools/"
    base_file = "riscv64-unknown-elf-gcc-8.3.0-2019.08.0-x86_64-"

    # Windows
    if (sys.platform.startswith("win") or sys.platform.startswith("cygwin")):
        end_file = "w64-mingw32.zip"
    # Linux
    elif sys.platform.startswith("linux"):
        end_file = "linux-ubuntu14.tar.gz"
    # Mac OS
    elif sys.platform.startswith("darwin"):
        end_file = "apple-darwin.tar.gz"
    else:
        raise NotImplementedError(sys.platform)
    fn = base_file + end_file

    if not os.path.exists(fn):
        url = base_url + fn
        print("Downloading", url, "to", fn)
        urllib.request.urlretrieve(url, fn)
    else:
        print("Using existing file", fn)

    print("Extracting", fn)
    shutil.unpack_archive(fn)

# Setup --------------------------------------------------------------------------------------------

if os.environ.get("TRAVIS", "") == "true":
    # Ignore `ssl.SSLCertVerificationError` on CI.
    import ssl
    ssl._create_default_https_context = ssl._create_unverified_context

if len(sys.argv) < 2:
    print("Available commands:")
    print("- init")
    print("- update")
    print("- install (add --user to install to user directory)")
    print("- gcc")
    print("- dev (dev mode, disable automatic litex_setup.py update)")
    exit()

# Repositories cloning
if "init" in sys.argv[1:]:
    for name in repos.keys():
        os.chdir(os.path.join(current_path))
        if not os.path.exists(name):
            url, need_recursive, need_develop, sha1 = repos[name]
            # clone repo (recursive if needed)
            print("[cloning " + name + "]...")
            full_url = url + name
            opts = "--recursive" if need_recursive else ""
            subprocess.check_call("git clone " + full_url + " " + opts, shell=True)
            if sha1 is not None:
                os.chdir(os.path.join(current_path, name))
                os.system("git checkout {:7x}".format(sha1))

# Repositories cloning as submodules
if "submodules" in sys.argv[1:]:
    for name in repos.keys():
        os.chdir(os.path.join(current_path))
        if not os.path.exists(name):
            url, need_recursive, need_develop, sha1 = repos[name]
            # clone repo (recursive if needed)
            print("[adding submodule " + name + "]...")
            full_url = url + name
            subprocess.check_call("git submodule add " + full_url + " " + name, shell=True)
            if sha1 is not None:
                os.chdir(os.path.join(current_path, name))
                os.system("git checkout {:7x}".format(sha1))

# Repositories update
if "update" in sys.argv[1:]:
    for name in repos.keys():
        os.chdir(os.path.join(current_path))
        url, need_recursive, need_develop, sha1 = repos[name]
        print(url)
        if not os.path.exists(name):
            raise Exception("{} not initialized, please (re)-run init and install first.".format(name))
        # update
        print("[updating " + name + "]...")
        os.chdir(os.path.join(current_path, name))
        subprocess.check_call("git checkout master", shell=True)
        subprocess.check_call("git pull --ff-only", shell=True)
        if need_recursive:
            subprocess.check_call("git submodule update --init --recursive", shell=True)
        if sha1 is not None:
            os.chdir(os.path.join(current_path, name))
            os.system("git checkout {:7x}".format(sha1))

# Repositories installation
if "install" in sys.argv[1:]:
    for name in repos.keys():
        os.chdir(os.path.join(current_path))
        url, need_recursive, need_develop, sha1 = repos[name]
        # develop if needed
        print("[installing " + name + "]...")
        if need_develop:
            os.chdir(os.path.join(current_path, name))
            """
            if sys.prefix == sys.base_prefix:
            else:
                source_cmd = "source {}/bin/activate && ".format(sys.prefix)
            """
            source_cmd = ""
            if "--user" in sys.argv[1:]:
                subprocess.check_call(source_cmd + "python3 setup.py develop --user", shell=True)
            else:
                subprocess.check_call(source_cmd + "python3 setup.py develop", shell=True)

    if "--user" in sys.argv[1:]:
        if ".local/bin" not in os.environ.get("PATH", ""):
            print("Make sure that ~/.local/bin is in your PATH")
            print("export PATH=$PATH:~/.local/bin")

# RISC-V GCC installation
if "gcc" in sys.argv[1:]:
    os.chdir(os.path.join(current_path))
    sifive_riscv_download()
    if "riscv64" not in os.environ.get("PATH", ""):
        print("Make sure that the downloaded RISC-V compiler is in your $PATH.")
        print("export PATH=$PATH:$(echo $PWD/riscv64-*/bin/)")
