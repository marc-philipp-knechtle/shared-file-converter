import argparse
from argparse import Namespace


def parse_arguments() -> Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input-file", type=str, help="Please specify the file you want to convert.")
    parser.add_argument("-o", "--output-file", type=str,
                        help="Please specify the file you want the created json written into. "
                             "Please note that all convent of this file will be deleted. "
                             "This has to be specified if there is no mongo database connection specified.",
                        default=None)
    parser.add_argument("-dbcon", "--db-connection", type=str,
                        help="Please specify this if you want to write the converted contents "
                             "into a mongo database instance. "
                             "This has to be specified if there is no output-file given."
                             "The connection string should look like this: "
                             "mongodb://user:password@ip:dbport/",
                        default=None)
    parser.add_argument("-dbcol", "--db-collection", type=str,
                        help="This denotes the collection where the created json should be written into.", default=None)
    return parser.parse_args()


def check_args(args: Namespace):
    # todo
    pass


def main(args: Namespace):
    check_args(args)


if __name__ == "__main__":
    main(parse_arguments())
