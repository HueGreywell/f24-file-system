from enum import Enum


class EntryType(str, Enum):
    FOLDER = "Folder"
    FILE = "File"

