from abc import abstractmethod, ABC

from docrecjson.elements import Document


class ConversionStrategy(ABC):
    @abstractmethod
    def initialize(self, original) -> Document:
        pass

    @abstractmethod
    def add_baselines(self, prev: Document, original) -> Document:
        pass

    @abstractmethod
    def add_lines(self, prev: Document, original) -> Document:
        pass


class PageXMLStrategyObjectify(ConversionStrategy):
    def initialize(self, original) -> Document:
        pass

    def add_baselines(self, prev: Document, original) -> Document:
        pass

    def add_lines(self, prev: Document, original) -> Document:
        pass


class PageXMLStrategyPyXB(ConversionStrategy):
    def initialize(self, original) -> Document:
        pass

    def add_baselines(self, prev: Document, original) -> Document:
        pass

    def add_lines(self, prev: Document, original) -> Document:
        pass
