import os.path
from dataclasses import dataclass
from enum import Enum

from loguru import logger

from converter.strategies.elements import ConversionStrategy
from docrecjson.elements import Document


# todo it may be necessary to differentiate between different PageXML versions
class SupportedTypes(Enum):
    page_xml = 1


# todo construct here the available types
def _get_type() -> SupportedTypes:
    logger.info("Resolved original type for document: [" + str(SupportedTypes.page_xml) + "]")
    return SupportedTypes.page_xml


@dataclass
class SharedDocument:
    filepath: str
    filename: str
    previous_type: SupportedTypes

    original: str
    tmp_type = None

    def __init__(self, filepath: str, original, tmp_type):
        self.filepath = filepath
        self.filename = os.path.basename(filepath)
        self.previous_type = _get_type()

        self.original = original
        self.tmp_type = tmp_type


class ConversionContext:
    _strategy: ConversionStrategy
    _original = None
    _document: Document

    def __init__(self, strategy: ConversionStrategy, original):
        self._strategy = strategy
        self._original = original

    @property
    def strategy(self) -> ConversionStrategy:
        return self._strategy

    @strategy.setter
    def strategy(self, strategy: ConversionStrategy):
        self._strategy = strategy

    def convert(self) -> Document:
        _document = self._strategy.initialize(self._original)
        _document = self._strategy.add_lines(_document, self._original)
        _document = self._strategy.add_baselines(_document, self._original)
        return _document
