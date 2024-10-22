import ase.db
import requests
from pathlib import Path
from pony.orm import *
from functools import cached_property
import numpy as np


def get_field_from_dict(dict_like):
    attrs = {}
    for field, (typ, kind) in dict_like.items():
        attrs[field] = kind(typ)
    return attrs

def get_value_from_row(keys):
    def _get_value(row):
        dict_row = {
            key: row[key] for key in keys if key in row
        }
        for key, value in dict_row.items():
            if isinstance(value, np.ndarray):
                dict_row[key] = value.flatten()
                if value.dtype == np.bool:
                    dict_row[key] = dict_row[key].astype(int)
            if value is None:
                dict_row.pop(key)
        return dict_row

    return _get_value

class AseDBLoader:

    # https://wiki.fysik.dtu.dk/ase/ase/db/db.html#description-of-a-row
    DEFAULT_FIELDS = {
        "id": (int, PrimaryKey),
        "unique_id": (str, Required),
        "ctime": (float, Required),
        "mtime": (float, Required),
        "user": (str, Required),
        "numbers": (IntArray, Required),
        "pbc": (IntArray, Required),
        "cell": (FloatArray, Required),
        "positions": (FloatArray, Required),
        # # optional
        "tags": (IntArray, Optional),
        "momenta": (FloatArray, Optional),
        "masses": (FloatArray, Optional),
        "magmoms": (FloatArray, Optional),
        "charges": (FloatArray, Optional),
    }

    def __init__(self, name: str, db: Database, extra_fields: dict = {}):
        self.name = name
        self.db = db
        self.extra_fields = extra_fields
        self._ase_entity = type("ASEEntity", (self.db.Entity,), get_field_from_dict(AseDBLoader.DEFAULT_FIELDS))
        self._entity = type(self.name, (self.ase_entity,), get_field_from_dict(self.extra_fields))

    def download_ase_db(self, ase_db: str, save_dir: Path):
        r = requests.get(ase_db)
        with open(save_dir, "wb") as f:
            f.write(r.content)

    @property
    def ase_entity(self):
        return self._ase_entity
    
    @property
    def entity(self):
        return self._entity

    @cached_property
    def fields(self):
        return {**AseDBLoader.DEFAULT_FIELDS, **self.extra_fields}

    def migrate(self, ase_db, bind_kwargs={}):
        getter = get_value_from_row(self.fields.keys())
        if not self.db.provider:
            self.db.bind(**bind_kwargs)
            self.db.generate_mapping(create_tables=True)
        with db_session:
            with ase.db.connect(ase_db) as conn:
                for row in conn.select():
                    self.entity(**getter(row))