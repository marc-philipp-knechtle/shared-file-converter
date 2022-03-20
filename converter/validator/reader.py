import os
from enum import unique, Enum
from pathlib import Path

import pyxb
from lxml import etree

from converter.elements import *
from converter.strategies.generated.page_xml import py_xb_2017
from converter.strategies.page_xml_2017_pyxb import PageXML2017StrategyPyXB


@unique
class SupportedTypes(Enum):
    PAGE_XML_2019 = PageXML2019Strategy()
    PAGE_XML_2017 = PageXML2017StrategyPyXB()


def read_xml(filepath: str) -> str:
    with open(filepath, "r") as file:
        content: str = file.read()
        return content


def _validate_xsd_schema(xml_path: str, xsd_path: str) -> bool:
    xmlschema_doc = etree.parse(os.path.join(xsd_path))
    xmlschema = etree.XMLSchema(xmlschema_doc)

    xml_doc = etree.parse(xml_path)

    # xmlschema.assert_(xml_doc)
    return_val = xmlschema.validate(xml_doc)
    if not return_val:
        _log_xsd_validation_error(xmlschema, xsd_path)
    return return_val


def _log_xsd_validation_error(xmlschema, xsd_path):
    log = xmlschema.error_log
    error = log.last_error
    logger.debug("Validation with [" + str(xsd_path) + "] resulted in:\n" + str(error))


class IncomingFileHandler(ABC):

    @abstractmethod
    def set_next(self, handler):
        pass

    @abstractmethod
    def handle(self, request) -> Document:
        pass

    @abstractmethod
    def is_instance_of(self, filepath: str) -> bool:
        pass


class AbstractIncomingFileHandler(IncomingFileHandler):
    _next_handler: IncomingFileHandler = None

    def set_next(self, handler: IncomingFileHandler) -> IncomingFileHandler:
        self._next_handler = handler
        return handler

    @abstractmethod
    def handle(self, request: str) -> Document:
        if self._next_handler:
            return self._next_handler.handle(request)
        else:
            logger.error("The read file [" + request + "] did not match any of the possible files.\n"
                                                       "Possible options are: [" + str(list(SupportedTypes)) + "]")

    @abstractmethod
    def handle_with_force(self, request: str) -> Document:
        pass


class PageXML2019Handler(AbstractIncomingFileHandler):
    _TYPE: SupportedTypes = SupportedTypes.PAGE_XML_2019
    _VALIDATION_FILEPATH: str = Path(__file__).parent / "page-xml/2019-07-15.xsd"

    def is_instance_of(self, filepath: str) -> bool:
        return _validate_xsd_schema(filepath, self._VALIDATION_FILEPATH)

    def handle(self, request: str):
        if self.is_instance_of(request):
            logger.info("[" + request + "] validated successfully for [" + self._TYPE.name + "]")
        else:
            return super().handle(request)

    def handle_with_force(self, request: str) -> Document:
        pass


class PageXML2017Handler(AbstractIncomingFileHandler):
    _TYPE: SupportedTypes = SupportedTypes.PAGE_XML_2017
    _VALIDATION_FILEPATH: str = Path(__file__).parent / "page-xml/2017-07-15.xsd"

    def is_instance_of(self, filepath: str) -> bool:
        return _validate_xsd_schema(filepath, self._VALIDATION_FILEPATH)

    def handle(self, request) -> Document:
        if self.is_instance_of(request):
            logger.info("[" + request + "] validated successfully for [" + self._TYPE.name + "]")
            xml: str = read_xml(request)
            converter_document: ConverterDocument = ConverterDocument(filepath=request, original=xml,
                                                                      tmp_type=py_xb_2017.CreateFromDocument(xml))
            context = ConversionContext(self._TYPE.value, converter_document)
            return context.convert()
        else:
            return super().handle(request)

    def handle_with_force(self, request: str) -> Document:
        logger.info("[" + request + "] was forced to be processed with [ " + self._TYPE.name + "]")
        xml: str = read_xml(request)
        try:
            tmp_conversion_type = py_xb_2017.CreateFromDocument(xml)
        except pyxb.UnrecognizedContentError as e:
            logger.error("ERROR converting given document!")
            logger.error(e.details())
            pyxb.RequireValidWhenParsing(False)
            tmp_conversion_type = py_xb_2017.CreateFromDocument(xml)

        converter_document: ConverterDocument = ConverterDocument(filepath=request, original=xml,
                                                                  tmp_type=tmp_conversion_type)
        context = ConversionContext(self._TYPE.value, converter_document)
        return context.convert()


def handle_incoming_file(filepath: str) -> Document:
    logger.info("Start processing on: [" + filepath + "]")
    page_xml_2019 = PageXML2019Handler()
    page_xml_2019.set_next(PageXML2017Handler())
    return page_xml_2019.handle(filepath)


def handle_force_incoming_file(filepath: str, force_arg: str) -> Document:
    if force_arg == "page2017":
        page_xml_2017 = PageXML2017Handler()
        return page_xml_2017.handle_with_force(filepath)
    else:
        raise ValueError(
            "The specified forced strategy does not match the available strategies. "
            "Please look at the --help output for further information.")
