from abc import abstractmethod, ABC

from converter.elements import ConverterDocument


class ConversionStrategy(ABC):
    @abstractmethod
    def initialize(self, original) -> ConverterDocument:
        pass

    @abstractmethod
    def add_baselines(self, converter_doc: ConverterDocument) -> ConverterDocument:
        pass

    @abstractmethod
    def add_lines(self, converter_doc: ConverterDocument) -> ConverterDocument:
        pass


class PageXMLStrategyObjectify(ConversionStrategy):
    def initialize(self, original) -> ConverterDocument:
        pass

    def add_baselines(self, converter_doc: ConverterDocument) -> ConverterDocument:
        pass

    def add_lines(self, converter_doc: ConverterDocument) -> ConverterDocument:
        pass


class PageXMLStrategyPyXB(ConversionStrategy):
    def initialize(self, original) -> ConverterDocument:
        pass

    def add_baselines(self, converter_doc: ConverterDocument) -> ConverterDocument:
        pass

    def add_lines(self, converter_doc: ConverterDocument) -> ConverterDocument:
        pass
