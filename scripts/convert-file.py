import argparse
import sys
from argparse import Namespace

from loguru import logger

from converter import reader

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
    content_to_dict: dict = reader.read_and_convert_to_dict(input_filepath)
    logger.info("Started processing on file with name: [" + input_filepath + "]")

    # todo process dict to shared-file-format

    # todo write to file or database


if __name__ == "__main__":
    main(parse_arguments())
