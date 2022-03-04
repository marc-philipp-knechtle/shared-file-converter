import os

import xmltodict
from lxml import etree, objectify

from converter.elements import *


@unique
class SupportedTypes(Enum):
    PAGE_XML_2019 = PageXML2019Strategy()
    PAGE_XML_2017 = PageXML2017StrategyPyXB()


# todo construct here the available types
def _get_type() -> SupportedTypes:
    logger.info("Resolved original type for document: [" + str(SupportedTypes.PAGE_XML_2019) + "]")
    return SupportedTypes.PAGE_XML_2019


def read_xml(filepath: str) -> str:
    with open(filepath, "r") as file:
        content: str = file.read()
        validation_result: bool = validate(filepath,
                                           "/home/makn/Downloads/2017-07-15.xsd")
        if not validation_result:
            logger.error("The read XML File does not match to the specified schema.")
        else:
            logger.info("[" + filepath + "] validated successfully.")
        return content


# = ObjectfiedElement?
def read_and_convert_to_object(filepath: str):
    validation_result: bool = validate(filepath,
                                       "/home/makn/Downloads/2017-07-15.xsd")
    if not validation_result:
        logger.error("The read XML File does not match to the specified schema.")
    else:
        logger.info("[" + filepath + "] validated successfully.")
    return objectify.parse(filepath)
    # return objectify.fromstring(read_xml(filepath))


def read_and_convert_to_dict(filepath: str) -> dict:
    return xmltodict.parse(read_xml(filepath))


def validate(xml_path: str, xsd_path: str) -> bool:
    logger.info("Validation started on: [" + xml_path + "] with schema: [" + xsd_path + "]")
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


class AbstractIncomingFileHandler(IncomingFileHandler):
    _next_handler: IncomingFileHandler = None

    def set_next(self, handler: IncomingFileHandler) -> IncomingFileHandler:
        self._next_handler = handler
        return handler

    @abstractmethod
    def handle(self, request) -> Document:
        if self._next_handler:
            return self._next_handler.handle(request)
        else:
            print("reached end of all handlers!")


class PageXML2019Handler(AbstractIncomingFileHandler):

    def handle(self, request):
        if False:
            print("aoeu")
        else:
            logger.info("PageXML2019 did not match, returning to PageXML2017")
            super().handle(request)


class PageXML2017Handler(AbstractIncomingFileHandler):

    def handle(self, request):
        if False:
            print("aoesnuh")
        else:
            logger.info("PageXML2017 did not match, returning to PageXML2016")
            super().handle(request)


class PageXML2016Handler(AbstractIncomingFileHandler):

    def handle(self, request):
        if False:
            print("aonset")
        else:
            logger.info("PageXML2016 did not match, defaultinf to False")
            super().handle(request)


def handle_incoming_file(filepath: str) -> Document:
    page_xml_2019 = PageXML2019Handler()
    page_xml_2019.set_next(PageXML2017Handler()).set_next(PageXML2016Handler())
    return page_xml_2019.handle(filepath)
