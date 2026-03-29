"""Application-wide constants."""

SUPPORTED_IMAGE_EXTENSIONS: set[str] = {
    ".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp",
}

SUPPORTED_IMAGE_FORMATS: set[str] = {
    "jpg", "jpeg", "png", "webp", "gif", "bmp",
}

SUPPORTED_ARCHIVE_EXTENSIONS: set[str] = {".cbz", ".zip"}

MAX_IMAGE_SIZE_MB: int = 100
MAX_IMAGE_SIZE_BYTES: int = MAX_IMAGE_SIZE_MB * 1024 * 1024

ILLEGAL_FILENAME_CHARS: str = '<>:"/\\|?*'

WINDOWS_RESERVED_NAMES: set[str] = {
    "CON", "PRN", "AUX", "NUL",
    "COM1", "COM2", "COM3", "COM4", "COM5",
    "COM6", "COM7", "COM8", "COM9",
    "LPT1", "LPT2", "LPT3", "LPT4", "LPT5",
    "LPT6", "LPT7", "LPT8", "LPT9",
}

MAX_FILENAME_LENGTH: int = 255
MAX_PATH_LENGTH: int = 260

DEFAULT_ZIP_FORMATS: set[str] = {"jpg"}

DEV_SERVER_PORT: int = 8901
