import argparse
import sys
from argparse import Namespace

from loguru import logger

import converter.strategies.page_xml.generate_ds_2017 as generate_ds_2017
import converter.strategies.page_xml.py_xb_2017 as py_xb_2017
from converter.elements import ConverterDocument, ConversionContext, PageXML2017StrategyPyXB, \
    PageXML2017StrategyGenerateDS
from converter.validator import reader
from converter.validator.reader import handle_incoming_file
from docrecjson.elements import Document

# remove the default loguru logger
logger.remove()
# add new custom loggers
logger.add(sys.stdout, level='INFO')
logger.add("errors.log", level='ERROR', rotation="1 MB")


def parse_arguments() -> Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_file", type=str, help="Please specify the file you want to convert.")
    parser.add_argument("-o", "--output_file", type=str,
                        help="Please specify the file you want the created json written into. "
                             "Please note that all convent of this file will be deleted. "
                             "This has to be specified if there is no mongo database connection specified.",
                        default=None)
    parser.add_argument("-dbcon", "--db_connection", type=str,
                        help="Please specify this if you want to write the converted contents "
                             "into a mongo database instance. "
                             "This has to be specified if there is no output-file given."
                             "The connection string should look like this: "
                             "mongodb://user:password@ip:dbport/",
                        default=None)
    parser.add_argument("-dbcol", "--db_collection", type=str,
                        help="This denotes the collection where the created json should be written into.", default=None)
    return parser.parse_args()


def check_args(args: Namespace):
    assert args.input_file is not None
    assert args.output_file is not None or args.db_connection is not None


def main(args: Namespace):
    check_args(args)
    input_filepath: str = args.input_file
    output_filepath: str = args.output_file
    db_connection: str = args.db_connection
    db_collection: str = args.db_collection

    # todo read file and convert to dict

    handle_incoming_file(input_filepath)

    # test_py_xb_conversion(input_filepath)
    # test_generate_ds_conversion(input_filepath)

    # content_to_dict: dict = reader.read_and_convert_to_dict(input_filepath)
    # xml_object = reader.read_and_convert_to_object(input_filepath)
    # print("instance?:")
    # print(isinstance(xml_object.getroot(), objectify.ObjectifiedElement))
    # print(str(xml_object.getroot()))
    # # print(str(objectify.dump(xml_object.getroot())))
    # # objectify.xsiannotate(xml_object)
    # objectify.deannotate(xml_object)
    # print(str(objectify.dump(xml_object.getroot())))
    #
    # print("Direct Access attempt:")
    # print(str(xml_object.getroot().Metadata.Creator))
    # print(str(xml_object.getroot().Page.TextRegion[0].Coords.get("points")))
    # print(type(xml_object.getroot().Page.TextRegion[0].Coords.get("points")))

    # todo write to file or database


def test_py_xb_conversion(input_filepath):
    doc: ConverterDocument = ConverterDocument(input_filepath, reader.read_xml(input_filepath),
                                               tmp_type=py_xb_2017.CreateFromDocument(reader.read_xml(input_filepath)))
    logger.info("Started processing on file: [" + input_filepath + "]")
    context = ConversionContext(PageXML2017StrategyPyXB(), doc)
    # document: Document = context.convert()


def test_generate_ds_conversion(input_filepath):
    xml: str = reader.read_xml(input_filepath)
    doc: ConverterDocument = ConverterDocument(input_filepath, xml,
                                               tmp_type=generate_ds_2017.parse(input_filepath, silence=True))
    logger.info("Started processing on file: [" + input_filepath + "]")
    context = ConversionContext(PageXML2017StrategyGenerateDS(), doc)
    document: Document = context.convert()


if __name__ == "__main__":
    main(parse_arguments())
