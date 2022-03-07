import os.path
from abc import abstractmethod, ABC
from ctypes import Union
from dataclasses import dataclass
from datetime import date
from typing import List

from loguru import logger
from pyxb.binding.content import _PluralBinding

from converter.strategies.page_xml.py_xb_2017 import PcGtsType, UserDefinedType, TextRegionType
from docrecjson.commontypes import Points
from docrecjson.elements import Document, GroupRef


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
    def add_regions(self, original: ConverterDocument) -> ConverterDocument:
        pass


class PageConversionStrategy(ConversionStrategy, ABC):

    @abstractmethod
    def handle_text_region(self, text_region_type):
        pass

    @abstractmethod
    def handle_image_region(self, image_region_type) -> dict:
        pass

    @abstractmethod
    def handle_line_drawing_region(self, line_drawing_region_type) -> dict:
        pass


class PageXML2017StrategyPyXB(PageConversionStrategy):

    # This is not inspected because moving this out of the strategy may be very confusing
    # Furthermore this may be necessary to implement for each strategy and be moved therefore into ConversionStrategy
    #   or a page subclass.
    # noinspection PyMethodMayBeStatic
    def _execute_if_present(self, py_xb_object_condition, func, *args):
        if not py_xb_object_condition:
            logger.debug("[" + str(type(py_xb_object_condition)) + "] is not present in the currently created object.")
        else:
            func(*args)

    # noinspection PyMethodMayBeStatic
    def _create_user_defined_metadata(self, user_defined_metadata: UserDefinedType) -> dict:
        # todo mitigate the necessity for this behaviour or create an abstract function which performs this check
        if user_defined_metadata is None:
            return {}
        dct = {}
        for attribute in user_defined_metadata.UserAttribute:
            dct[str(attribute.name)] = str(attribute.value_)
        return dct

    def initialize(self, original: ConverterDocument) -> ConverterDocument:
        pyxb_object: PcGtsType = original.tmp_type
        document: Document = Document.empty(pyxb_object.Page.imageFilename,
                                            (pyxb_object.Page.imageHeight, pyxb_object.Page.imageWidth))
        document.add_creator(pyxb_object.Metadata.Creator, "2017-07-15")
        document.add_creator("shared-file-converter", str(date.today()))
        original.shared_file_format_document = document
        return original

    def add_metadata(self, original: ConverterDocument) -> ConverterDocument:
        pyxb_object: PcGtsType = original.tmp_type
        document: Document = original.shared_file_format_document

        document.add_metadata({"LastChange": str(pyxb_object.Metadata.LastChange)})
        self._execute_if_present(pyxb_object.Metadata.Comments, document.add_metadata,
                                 {"Comments": str(pyxb_object.Metadata.Comments)})
        self._execute_if_present(pyxb_object.Metadata.UserDefined, document.add_metadata,
                                 self._create_user_defined_metadata(pyxb_object.Metadata.UserDefined))
        self._execute_if_present(pyxb_object.Metadata.externalRef, document.add_metadata,
                                 {"externalRef": str(pyxb_object.Metadata.externalRef)})

        original.shared_file_format_document = document
        return original

    def add_regions(self, original: ConverterDocument) -> ConverterDocument:
        pyxb_object: PcGtsType = original.tmp_type
        document: Document = original.shared_file_format_document

        self._execute_if_present(pyxb_object.Page.TextRegion, document.add_region,
                                 self.handle_text_region(pyxb_object.Page.TextRegion), "text")

        original.shared_file_format_document = document
        return original

    def handle_text_region(self, text_region_type: _PluralBinding):
        print(str(type(text_region_type)))
        for test_region in text_region_type:
            text_line = test_region.TextLine
            # points = text_line.Coords.points
            # baseline = text_line.Baseline.points
            # text_equiv = text_line.TextEquiv.Unicode
            print("hello")
        pass

    def handle_image_region(self, image_region_type) -> dict:
        pass

    def handle_line_drawing_region(self, line_drawing_region_type) -> dict:
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

    def add_regions(self, original: ConverterDocument) -> ConverterDocument:
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

    def add_regions(self, original: ConverterDocument) -> ConverterDocument:
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
        self._converter_doc = self._strategy.add_metadata(self._converter_doc)
        self._converter_doc = self._strategy.add_regions(self._converter_doc)
        return self._converter_doc.shared_file_format_document
