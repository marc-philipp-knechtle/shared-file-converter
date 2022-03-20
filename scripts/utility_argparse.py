import argparse


def initialize() -> argparse.ArgumentParser:
    return argparse.ArgumentParser()


def add_db_args(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    parser.add_argument("-dbcon", "--db_connection", type=str,
                        help="Please specify this if you want to write the converted contents "
                             "into a mongo database instance. "
                             "This has to be specified if there is no output-file given."
                             "The connection string should look like this: "
                             "mongodb://user:password@ip:dbport/",
                        default=None)
    parser.add_argument("-dbdat", "--db_database", type=str,
                        help="This denotes the database where the created json should be written into.", default=None)
    parser.add_argument("-dbcol", "--db_collection", type=str,
                        help="This denotes the collection where the created json should be written into.", default=None)
    return parser


def add_log_args(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    parser.add_argument("-log", "--log_output", type=bool, default=False,
                        help="Info-logs the computed json-dict file.")
    return parser


def add_force_args(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    parser.add_argument("-f", "--force_strategy", type=str,
                        help="This argument overrides the file matcher and validator to a already specified strategy."
                             "Please be aware that skipping those steps in the conversion process may lead to "
                             "unintended errors. Available options are:"
                             "page2019",
                        default=None)
    return parser
