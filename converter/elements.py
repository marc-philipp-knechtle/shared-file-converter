import os.path
from abc import abstractmethod, ABC
from dataclasses import dataclass
from enum import Enum

from loguru import logger

from docrecjson.elements import Document


# todo it may be necessary to differentiate between different PageXML versions
class SupportedTypes(Enum):
    page_xml = 1


# todo construct here the available types
def _get_type() -> SupportedTypes:
    logger.info("Resolved original type for document: [" + str(SupportedTypes.page_xml) + "]")
    return SupportedTypes.page_xml


@dataclass
class ConverterDocument:
    filepath: str
    filename: str
    previous_type: SupportedTypes

    original: str
    tmp_type = None
    _shared_file_format_document: Document

    def __init__(self, filepath: str, original, tmp_type):
        self.filepath = filepath
        self.filename = os.path.basename(filepath)
        self.previous_type = _get_type()

        self.original = original
        self.tmp_type = tmp_type

    @property
    def shared_file_format_document(self) -> Document:
        return self._shared_file_format_document

    @shared_file_format_document.setter
    def shared_file_format_document(self, shared_file_format_document: Document):
        self._shared_file_format_document = shared_file_format_document


class ConversionStrategy(ABC):
    @abstractmethod
    def initialize(self, original) -> ConverterDocument:
        pass

    @abstractmethod
    def add_baselines(self, converter_doc: ConverterDocument) -> ConverterDocument:
        pass

    @abstractmethod
    def add_lines(self, converter_doc: ConverterDocument) -> ConverterDocument:
        pass


class PageXMLStrategyObjectify(ConversionStrategy):
    def initialize(self, original) -> ConverterDocument:
        pass

    def add_baselines(self, converter_doc: ConverterDocument) -> ConverterDocument:
        pass

    def add_lines(self, converter_doc: ConverterDocument) -> ConverterDocument:
        pass


class PageXMLStrategyPyXB(ConversionStrategy):
    def initialize(self, original) -> ConverterDocument:
        pass

    def add_baselines(self, converter_doc: ConverterDocument) -> ConverterDocument:
        pass

    def add_lines(self, converter_doc: ConverterDocument) -> ConverterDocument:
        pass


class ConversionContext:
    _strategy: ConversionStrategy
    _converter_doc: ConverterDocument

    def __init__(self, strategy: ConversionStrategy, doc: ConverterDocument):
        self._strategy = strategy
        self._converter_doc = doc

    @property
    def strategy(self) -> ConversionStrategy:
        return self._strategy

    @strategy.setter
    def strategy(self, strategy: ConversionStrategy):
        self._strategy = strategy

    def convert(self) -> Document:
        self._converter_doc = self._strategy.initialize(self._converter_doc)
        self._converter_doc = self._strategy.add_lines(self._converter_doc)
        self._converter_doc = self._strategy.add_baselines(self._converter_doc)
        return self._converter_doc.shared_file_format_document
