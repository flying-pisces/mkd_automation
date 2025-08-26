import platform

from mkd.platform.base import BasePlatform
from mkd.platform.macos import MacOSPlatform
from mkd.platform.windows import WindowsPlatform
from mkd.platform.linux import LinuxPlatform

def get_platform() -> BasePlatform:
    """Returns the platform-specific implementation."""
    system = platform.system()
    if system == "Darwin":
        return MacOSPlatform()
    elif system == "Windows":
        return WindowsPlatform()
    elif system == "Linux":
        return LinuxPlatform()
    else:
        raise NotImplementedError(f"Platform {system} is not supported.")
