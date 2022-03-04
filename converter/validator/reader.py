import os
from pathlib import Path

import xmltodict
from lxml import etree

from converter.elements import *


@unique
class SupportedTypes(Enum):
    PAGE_XML_2019 = PageXML2019Strategy()
    PAGE_XML_2017 = PageXML2017StrategyPyXB()


def read_xml(filepath: str) -> str:
    with open(filepath, "r") as file:
        content: str = file.read()
        return content


def read_and_convert_to_dict(filepath: str) -> dict:
    return xmltodict.parse(read_xml(filepath))


def validate_xsd_schema(xml_path: str, xsd_path: str) -> bool:
    xmlschema_doc = etree.parse(os.path.join(xsd_path))
    xmlschema = etree.XMLSchema(xmlschema_doc)

    xml_doc = etree.parse(xml_path)

    return xmlschema.validate(xml_doc)


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


class PageXML2019Handler(AbstractIncomingFileHandler):
    _TYPE: SupportedTypes = SupportedTypes.PAGE_XML_2019
    _VALIDATION_FILEPATH: str = Path(__file__).parent / "page-xml/2019-07-15.xsd"

    def is_instance_of(self, filepath: str) -> bool:
        return validate_xsd_schema(filepath, self._VALIDATION_FILEPATH)

    def handle(self, request: str):
        if self.is_instance_of(request):
            logger.info("[" + request + "] validated successfully for [" + self._TYPE.name + "]")
        else:
            super().handle(request)


class PageXML2017Handler(AbstractIncomingFileHandler):
    _TYPE: SupportedTypes = SupportedTypes.PAGE_XML_2017
    _VALIDATION_FILEPATH: str = Path(__file__).parent / "page-xml/2017-07-15.xsd"

    def is_instance_of(self, filepath: str) -> bool:
        return validate_xsd_schema(filepath, self._VALIDATION_FILEPATH)

    def handle(self, request):
        if self.is_instance_of(request):
            logger.info("[" + request + "] validated successfully for [" + self._TYPE.name + "]")
        else:
            super().handle(request)


def handle_incoming_file(filepath: str) -> Document:
    logger.info("Start processing on: [" + filepath + "]")
    page_xml_2019 = PageXML2019Handler()
    page_xml_2019.set_next(PageXML2017Handler())
    return page_xml_2019.handle(filepath)
