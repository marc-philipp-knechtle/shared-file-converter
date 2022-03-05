import os.path
from abc import abstractmethod, ABC
from dataclasses import dataclass

from loguru import logger

from converter.strategies.page_xml.py_xb_2017 import PcGtsType
from docrecjson.elements import Document


@dataclass
class ConverterDocument:
    filepath: str
    filename: str

    original: str
    tmp_type = None
    _shared_file_format_document: Document

    def __init__(self, filepath: str, original, tmp_type):
        self.filepath = filepath
        self.filename = os.path.basename(filepath)

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
    def initialize(self, original: ConverterDocument) -> ConverterDocument:
        pass

    @abstractmethod
    def add_metadata(self, original: ConverterDocument) -> ConverterDocument:
        pass

    @abstractmethod
    def add_baselines(self, converter_doc: ConverterDocument) -> ConverterDocument:
        pass

    @abstractmethod
    def add_lines(self, converter_doc: ConverterDocument) -> ConverterDocument:
        pass


class PageXML2017StrategyObjectify(ConversionStrategy):
    def initialize(self, original: ConverterDocument) -> ConverterDocument:
        pass

    def add_baselines(self, converter_doc: ConverterDocument) -> ConverterDocument:
        pass

    def add_metadata(self, original: ConverterDocument) -> ConverterDocument:
        pass

    def add_lines(self, converter_doc: ConverterDocument) -> ConverterDocument:
        pass


class PageXML2017StrategyPyXB(ConversionStrategy):
    def initialize(self, original: ConverterDocument) -> ConverterDocument:
        pyxb_object: PcGtsType = original.tmp_type
        document: Document = Document.empty(pyxb_object.Page.imageFilename,
                                            (pyxb_object.Page.imageHeight, pyxb_object.Page.imageWidth))
        document.add_creator(pyxb_object.Metadata.Creator, "2017-07-15")
        original.shared_file_format_document = document
        return original

    def add_metadata(self, original: ConverterDocument) -> ConverterDocument:
        pass

    def add_baselines(self, converter_doc: ConverterDocument) -> ConverterDocument:
        pass

    def add_lines(self, converter_doc: ConverterDocument) -> ConverterDocument:
        pass


class PageXML2017StrategyGenerateDS(ConversionStrategy):
    """
    The GenerateDS handling seems to be very similar to the PyXB handling, if not identical.
    I will therefore continue implementing the desired functionality with PyXB, not because of any knowledge of the
    inner workings, but only because of preference.
    But I'll leave this approach in this repository for an eventual later evaluation.
    """

    def initialize(self, original: ConverterDocument):
        print("hello there from initialyze")
        generate_ds_object = original.tmp_type
        print(generate_ds_object.Metadata.Creator)
        pass

    def add_metadata(self, original: ConverterDocument) -> ConverterDocument:
        pass

    def add_baselines(self, converter_doc: ConverterDocument) -> ConverterDocument:
        pass

    def add_lines(self, converter_doc: ConverterDocument) -> ConverterDocument:
        pass


class PageXML2019Strategy(ConversionStrategy):

    def initialize(self, original: ConverterDocument) -> ConverterDocument:
        pass

    def add_metadata(self, original: ConverterDocument) -> ConverterDocument:
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
        logger.info("Loaded strategy: " + self._strategy.__class__.__name__)
        self._converter_doc = doc

    @property
    def strategy(self) -> ConversionStrategy:
        return self._strategy

    @strategy.setter
    def strategy(self, strategy: ConversionStrategy):
        self._strategy = strategy

    def convert(self) -> Document:
        self._converter_doc = self._strategy.initialize(self._converter_doc)
        # self._converter_doc = self._strategy.add_lines(self._converter_doc)
        # self._converter_doc = self._strategy.add_baselines(self._converter_doc)
        return self._converter_doc.shared_file_format_document
