import json
import os
from argparse import Namespace
from typing import Union

from loguru import logger

from converter.validator.reader import handle_incoming_file, handle_force_incoming_file
from database.db import JsonDBStorage
from docrecjson.elements import Document


def write_to_db(args: Namespace, doc: Document, db: JsonDBStorage):
    if args.db_connection is not None:
        db.get_collection().insert_one(doc.to_dict())


def write_to_log(log_output: bool, doc: Document):
    if log_output:
        logger.info(json.dumps(doc.to_dict(), indent=4))


def write_to_file(filepath: str, dct: dict):
    if filepath is not None:
        path_considered_duplicates: str = file_considered_duplicates(filepath)
        with open(path_considered_duplicates, "w") as file:
            json.dump(dct, file, indent=2)
            logger.info("wrote processed contents into: [" + filepath + "]")


def file_considered_duplicates(filepath: str) -> str:
    """
    :param filepath: a full filepath
    :return: a new filepath if the specified filepath already exists, else the given filepath
    """
    counter: int = 1
    filepath, file_extension = os.path.splitext(filepath)
    if file_extension != ".json":
        raise RuntimeError(
            "The specified file doesn't have the correct extension for this application. "
            "The file extension should be [.json], but it is: [" + file_extension + "]")
    base_filepath: str = filepath
    while os.path.isfile(filepath + file_extension):
        filepath = os.path.join(base_filepath + " (" + str(counter) + ")")
        counter += 1
    return filepath + file_extension


def handle_incoming_file_with_optional_force(input_filepath: str, force_strategy: Union[str, None]) -> Document:
    if force_strategy is None:
        return handle_incoming_file(input_filepath)
    elif isinstance(force_strategy, str):
        return handle_force_incoming_file(input_filepath, force_strategy)
    else:
        raise ValueError("The specified strategy has to be either str or None for no forced strategy.")
