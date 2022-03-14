import os
import sys
import time
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
    parser.add_argument("-i", "--input_dir", type=str,
                        help="You can specify the directory you want to watch for new files to be converted.",
                        default=None)
    parser.add_argument("-o", "--output_dir", type=str,
                        help="If you specify this directory, the converted files will be written into this dir.",
                        default=None)
    parser = add_db_args(parser)
    parser = add_log_args(parser)
    return parser.parse_args()


def check_args(args: Namespace):
    assert args.input_dir is not None
    assert args.output_dir is not None or args.db_connection is not None or args.log_output is True


def main(args: Namespace):
    check_args(args)
    input_dir: str = args.input_dir
    db: JsonDBStorage = JsonDBStorage(args.db_connection, args.db_database, args.db_collection)

    try:
        logger.info("Started watching for new file on: [" + input_dir + "]")
        monitor_input_dir(args, db, input_dir)
    except KeyboardInterrupt:
        exit(0)


def monitor_input_dir(args, db, input_dir):
    while True:
        for filename in os.listdir(input_dir):
            handle_file_in_input_dir(args, db, filename, input_dir)
        time.sleep(2)


def handle_file_in_input_dir(args, db, filename, input_dir):
    filepath = os.path.join(input_dir, filename)

    doc: Document = handle_incoming_file(filepath)

    write(args, db, doc, filename)
    remove_input_file(filepath)


def write(args, db, doc, filename):
    utility.write_to_log(args.log_output, doc)
    utility.write_to_db(args, doc, db)
    utility.write_to_file(os.path.join(args.output_dir, filename + ".json"), doc.to_dict())


def remove_input_file(filepath):
    os.remove(filepath)
    logger.info("removed: [" + str(filepath) + "]")


if __name__ == "__main__":
    main(parse_arguments())
