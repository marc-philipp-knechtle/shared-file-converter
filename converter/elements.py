import os.path
from abc import abstractmethod, ABC
from dataclasses import dataclass

from loguru import logger

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
    def add_regions(self, original: ConverterDocument) -> ConverterDocument:
        pass


class PageConversionStrategy(ConversionStrategy, ABC):

    @abstractmethod
    def handle_text_regions(self, document: Document, text_regions) -> Document:
        pass

    @abstractmethod
    def handle_image_region(self, document: Document, image_region) -> Document:
        pass

    @abstractmethod
    def handle_line_drawing_region(self, document: Document, line_drawing_region) -> Document:
        pass

    @abstractmethod
    def handle_graphic_region(self, document: Document, graphic_region) -> Document:
        pass

    @abstractmethod
    def handle_table_region(self, document: Document, table_region) -> Document:
        pass

    @abstractmethod
    def handle_chart_region(self, document: Document, chart_region) -> Document:
        pass

    @abstractmethod
    def handle_separator_region(self, document: Document, separator_region) -> Document:
        pass

    @abstractmethod
    def handle_maths_region(self, document: Document, maths_region) -> Document:
        pass

    @abstractmethod
    def handle_chem_region(self, document: Document, chem_region) -> Document:
        pass

    @abstractmethod
    def handle_music_region(self, document: Document, music_region) -> Document:
        pass

    @abstractmethod
    def handle_advert_region(self, document: Document, advert_region) -> Document:
        pass

    @abstractmethod
    def handle_noise_region(self, document: Document, noise_region) -> Document:
        pass

    @abstractmethod
    def handle_unknown_region(self, document: Document, unknown_region) -> Document:
        pass


class PageXML2017StrategyGenerateDS(ConversionStrategy):
    """
    The GenerateDS handling seems to be very similar to the PyXB handling, if not identical.
    I will therefore continue implementing the desired functionality with PyXB, not because of any knowledge of the
    inner workings, but only because of preference.
    But I'll leave this approach in this repository for an eventual later evaluation.

    def test_generate_ds_conversion(input_filepath):
    xml: str = reader.read_xml(input_filepath)
    doc: ConverterDocument = ConverterDocument(input_filepath, xml,
                                               tmp_type=generate_ds_2017.parse(input_filepath, silence=True))
    logger.info("Started processing on file: [" + input_filepath + "]")
    context = ConversionContext(PageXML2017StrategyGenerateDS(), doc)
    document: Document = context.convert()

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
