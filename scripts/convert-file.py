import json
import os
import sys
from argparse import Namespace

from loguru import logger

from utility_argparse import *
from converter.validator.reader import handle_incoming_file
from database.db import JsonDBStorage
from docrecjson.elements import Document

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

    write_to_log(log_output, doc)
    write_to_db(args, doc)
    write_to_file(output_filepath, doc.to_dict())


def write_to_db(args: Namespace, doc: Document):
    if args.db_connection is not None:
        db = JsonDBStorage(args.db_connection, args.db_database, args.db_collection)
        db.get_collection().insert_one(doc.to_dict())


def write_to_log(log_output: bool, doc: Document):
    if log_output:
        logger.info(json.dumps(doc.to_dict(), indent=4))


def write_to_file(filepath: str, dct: dict):
    if filepath is not None:
        with open(filename_considered_duplicates(filepath), "w") as file:
            json.dump(dct, file)


def filename_considered_duplicates(filepath: str) -> str:
    """
    :param filepath: a full filepath
    :return: a new filepath if the specified filepath already exists, else the specified filepath with filepath
    """
    counter: int = 1
    filepath, file_extension = os.path.splitext(os.path.basename(filepath))
    base_filepath: str = filepath
    while os.path.isfile(filepath + file_extension):
        filepath = os.path.join(base_filepath + " (" + str(counter) + ")")
        counter += 1
    return filepath + file_extension


if __name__ == "__main__":
    main(parse_arguments())
