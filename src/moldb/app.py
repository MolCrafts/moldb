from typing import Literal

class MolDB:

    def __init__(self, ):
        self._adapter_list = []

    def _init_adapter(self, backend:str):
        if backend == 'sqlite':
            from .adapter.sqlite import SQLiteAdapter
            return SQLiteAdapter()
        elif backend == 'h5py':
            from .adapter.h5py import H5pyAdapter
            return H5pyAdapter()
        else:
            raise ValueError('Invalid backend')

    def connect(self, name:str, backend:str):
        adapter = self._init_adapter(backend)
        adapter.connect(name)
        self._adapter_list.append(adapter)
        