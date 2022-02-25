import os

import xmltodict
from loguru import logger
from lxml import etree, objectify


def read_xml(filepath: str) -> str:
    with open(filepath, "r") as file:
        content: str = file.read()
        validation_result: bool = validate(filepath,
                                           "/home/makn/Downloads/2017-07-15.xsd")
        if not validation_result:
            logger.error("The read XML File does not match to the specified schema.")
        return content


# = ObjectfiedElement?
def read_and_convert_to_object(filepath: str):
    validation_result: bool = validate(filepath,
                                       "/home/makn/Downloads/2017-07-15.xsd")
    if not validation_result:
        logger.error("The read XML File does not match to the specified schema.")
    return objectify.parse(filepath)
    # return objectify.fromstring(read_xml(filepath))


def read_and_convert_to_dict(filepath: str) -> dict:
    return xmltodict.parse(read_xml(filepath))


def validate(xml_path: str, xsd_path: str) -> bool:
    xmlschema_doc = etree.parse(os.path.join(xsd_path))
    xmlschema = etree.XMLSchema(xmlschema_doc)

    xml_doc = etree.parse(xml_path)

    return xmlschema.validate(xml_doc)
