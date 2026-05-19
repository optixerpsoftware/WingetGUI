import platform

_OS_COMPATIBLE: list[str] = ["Windows"]
_VERSION_COMPATIBLE: list[str] = ["10", "11"]


def check_compatibility() -> bool:
    os_name = platform.system()
    os_version = platform.release()

    return os_name in _OS_COMPATIBLE and os_version in _VERSION_COMPATIBLE

