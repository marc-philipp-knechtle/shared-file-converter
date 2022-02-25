import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

from docrecjson.elements import Document
from loguru import logger

from converter.strategies.elements import PageXMLStrategyObjectify, ConversionStrategy


# todo it may be necessary to differentiate between different PageXML versions
class SupportedTypes(Enum):
    page_xml = 1


# todo construct here the available types
def _get_type() -> SupportedTypes:
    logger.info("Resolved original type for document: [" + str(SupportedTypes.page_xml) + "]")
    return SupportedTypes.page_xml


@dataclass
class SharedDocument:
    filepath: str
    filename: str
    document: Document

    previous_representation: dict
    previous_representation_removed = None
    previous_type: SupportedTypes

    def __init__(self, filepath: str, previous_representation):
        self.filepath = filepath
        self.previous_representation = previous_representation

        self.previous_type = _get_type()

        context: ConversionContext = ConversionContext(PageXMLStrategyObjectify())
        context.convert()


class ConversionContext:
    _strategy: ConversionStrategy

    def __init__(self, strategy: ConversionStrategy):
        self._strategy = strategy

    @property
    def strategy(self) -> ConversionStrategy:
        return self._strategy

    @strategy.setter
    def strategy(self, strategy: ConversionStrategy):
        self._strategy = strategy

    def convert(self):
        self._strategy.add_lines()
        self._strategy.add_baselines()
