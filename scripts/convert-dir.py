import sys
from argparse import Namespace

from loguru import logger

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
