import sys
import ctypes
import platform
import struct
from pathlib import Path

LUP_MAP = { # Credit: thanks chatGPT for typing up the (architecture, platform) lookup table - Im too lazy to type it myself
    ("Windows", "x86"):     "windows/x86/renderer.dll",
    ("Windows", "x86_64"): "windows/x86_64/renderer.dll",
    ("Windows", "arm"):    "windows/arm/renderer.dll",
    ("Windows", "arm64"):  "windows/arm64/renderer.dll",

    ("Linux", "x86"):      "linux/x86/librenderer.so",
    ("Linux", "x86_64"):  "linux/x86_64/librenderer.so",
    ("Linux", "arm"):     "linux/arm/librenderer.so",
    ("Linux", "arm64"):   "linux/arm64/librenderer.so",

    ("macOS", "x86_64"):  "macos/x86_64/librenderer.dylib",
    ("macOS", "arm64"):   "macos/arm64/librenderer.dylib",
}

OS_MAP = {
    "win32": "Windows",
    "linux": "Linux",
    "darwin": "macOS"
}

ARCH_MAP = {
    "i386": "x86",
    "i686": "x86",
    "AMD64": "x86_64",
    "x86_64": "x86_64",
    "x86": "x86",
    "armv6l": "arm",
    "armv7l": "arm",
    "aarch64": "arm64",
    "arm64": "arm64",
}

os_name = OS_MAP.get(sys.platform)

architecture = ARCH_MAP.get(platform.machine())

bits = struct.calcsize("P") * 8

if bits == 32:
    if architecture == "x86_64":
        architecture = "x86"
    elif architecture == "arm64":
        architecture = "arm"

elif bits != 64:
    raise RuntimeError(f"Unsupported bitness: {bits}")

if os_name is None or architecture is None:
    raise RuntimeError("Unsupported platform")

library = LUP_MAP.get((os_name, architecture))

if library is None:
    raise RuntimeError(f"No renderer for {os_name} {architecture}")

ROOT = Path(__file__).resolve().parent

library_path = ROOT / "renderer" / "bin" / library

if not library_path.is_file():
    raise FileNotFoundError(f"Renderer not found: {library_path}")

renderer = ctypes.CDLL(str(library_path))