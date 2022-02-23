from abc import ABC, abstractmethod


class ConversionStrategy(ABC):
    @abstractmethod
    def add_baselines(self):
        pass

    @abstractmethod
    def add_lines(self):
        pass


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
