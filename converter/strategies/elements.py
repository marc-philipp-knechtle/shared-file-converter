from abc import abstractmethod, ABC


class ConversionStrategy(ABC):
    @abstractmethod
    def add_baselines(self):
        pass

    @abstractmethod
    def add_lines(self):
        pass


class PageXMLStrategy(ConversionStrategy):
    def add_baselines(self):
        pass

    def add_lines(self):
        pass
