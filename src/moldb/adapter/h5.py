import h5py
from pathlib import Path
from adapter.base import BaseNonSQLAdapter
import molpy as mp

class H5PYAdapter(BaseNonSQLAdapter):

    def __init__(self, ):
        pass

    def connect(self, name: str, root: str|Path):
        self._fpath = Path(root) / name
        self._file = h5py.File(self._fpath, 'r+')

    def add_struct(self, struct:mp.Struct):
        pass

    def add_frame(self, frame:mp.Frame):
        pass


    def disconnect(self):
        return super().disconnect()
        