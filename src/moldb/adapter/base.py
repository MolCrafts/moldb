from abc import ABC, abstractmethod

class BaseAdapter(ABC):

    @abstractmethod
    def connect(self, name:str):
        pass

    @abstractmethod
    def disconnect(self):
        pass

class BaseSQLAdapter(BaseAdapter):
    pass

class BaseNonSQLAdapter(BaseAdapter):
    pass

