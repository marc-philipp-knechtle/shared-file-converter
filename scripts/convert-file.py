import sys
from argparse import Namespace

from loguru import logger

from converter.validator.reader import handle_incoming_file
from database.db import JsonDBStorage
from docrecjson.elements import Document
from scripts import utility
from utility_argparse import *

logger.remove()
# add new custom loggers
logger.add(sys.stdout, level='DEBUG')
logger.add("errors.log", level='ERROR', rotation="1 MB")


def parse_arguments() -> Namespace:
    parser: argparse.ArgumentParser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_file", type=str, help="Please specify the file you want to convert.")
    parser.add_argument("-o", "--output_file", type=str,
                        help="Please specify the file you want the created json written into. "
                             "Please note that all convent of this file will be deleted. "
                             "This has to be specified if there is no mongo database connection specified.",
                        default=None)
    parser = add_db_args(parser)
    parser = add_log_args(parser)
    return parser.parse_args()


def check_args(args: Namespace):
    assert args.input_file is not None
    assert args.output_file is not None or args.db_connection is not None or args.log_output is True


def main(args: Namespace):
    check_args(args)
    input_filepath: str = args.input_file
    output_filepath: str = args.output_file
    log_output: bool = args.log_output

    doc: Document = handle_incoming_file(input_filepath)

    utility.write_to_log(log_output, doc)
    utility.write_to_db(args, doc, JsonDBStorage(args.db_connection, args.db_database, args.db_collection))
    utility.write_to_file(output_filepath, doc.to_dict())


if __name__ == "__main__":
    main(parse_arguments())
