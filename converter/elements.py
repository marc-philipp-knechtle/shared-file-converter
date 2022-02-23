from dataclasses import dataclass
from enum import Enum

from docrecjson.elements import Document


class SupportedTypes(Enum):
    page_xml = 1


@dataclass
class SharedDocument:
    filepath: str
    filename: str
    document: Document

    previous_representation = None
    previous_representation_removed = None
    previous_type: SupportedTypes

    def __init__(self, filepath: str, previous_representation, previous_type):
        self.filepath = filepath
        self.previous_representation = previous_representation
        self.previous_type = previous_type

