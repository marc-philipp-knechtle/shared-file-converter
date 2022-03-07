import argparse
import json
import sys
from argparse import Namespace

from loguru import logger

from converter.validator.reader import handle_incoming_file
from docrecjson.elements import Document

logger.remove()
# add new custom loggers
logger.add(sys.stdout, level='DEBUG')
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
    parser.add_argument("-log", "--log_output", type=bool, default=False,
                        help="Only info-logs the output instead of writing it to a file or database.")
    return parser.parse_args()


def check_args(args: Namespace):
    assert args.input_file is not None
    assert args.output_file is not None or args.db_connection is not None or args.log_output is True


def main(args: Namespace):
    check_args(args)
    input_filepath: str = args.input_file
    output_filepath: str = args.output_file
    db_connection: str = args.db_connection
    db_collection: str = args.db_collection
    log_output: bool = args.log_output

    # todo read file and convert to dict

    doc: Document = handle_incoming_file(input_filepath)
    if log_output:
        logger.info(json.dumps(doc.to_dict(), indent=4))

    # todo write to file or database


# def test_generate_ds_conversion(input_filepath):
#     xml: str = reader.read_xml(input_filepath)
#     doc: ConverterDocument = ConverterDocument(input_filepath, xml,
#                                                tmp_type=generate_ds_2017.parse(input_filepath, silence=True))
#     logger.info("Started processing on file: [" + input_filepath + "]")
#     context = ConversionContext(PageXML2017StrategyGenerateDS(), doc)
#     document: Document = context.convert()


if __name__ == "__main__":
    main(parse_arguments())
