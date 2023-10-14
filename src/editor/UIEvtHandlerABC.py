from abc import ABC, abstractmethod


class UIEvtHandlerABC(ABC):
    @staticmethod
    @abstractmethod
    def handle_event(*args, **kwargs):
        pass
