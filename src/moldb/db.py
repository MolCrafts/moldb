import pony.orm as orm
from pony.orm.core import Entity
from .presets import get_default_entity
from rich.table import Table
import numpy as np
from typing import Callable

class Database(orm.Database):

    def def_entity(self, name:str, fields:dict):
        name = name.capitalize()
        default_entity = get_default_entity(self)
        entity = type(name, (default_entity,), fields)
        return entity
    
    def def_custom_entity(self, name:str, fields:dict):
        name = name.capitalize()
        entity = type(name, (self.Entity,), fields)
        return entity

    @orm.db_session
    def load_ase(self, filename:str, entity: Entity, selection:None):
        import ase.db
        ase_db = ase.db.connect(filename)
        default_keys = {attr.name for attr in entity.__base__._attrs_}
        default_keys.remove('classtype')
        this_keys = {attr.name for attr in entity._attrs_}
        this_keys.remove('classtype')
        data_keys = set(this_keys) - set(default_keys)
        for row in ase_db.select(selection):
            meta = {
                'id': row.id,
                'uuid': row.unique_id,
                'ctime': row.ctime,
                'mtime': row.mtime,
                'atomic_numbers': row.numbers,
                'pbc': np.array(row.pbc, dtype=int),
                'cell': row.cell.flatten(),
                'xyz': row.positions.flatten()
            }
            data = {k: row.get(k) for k in data_keys}
            entity(**meta, **data)

    def show_table(self, entity, display_column: list[str] = [], selection: Callable = None, n_rows:int=5):
        # get fields and make a rich table then print it
        table = Table(title = f"{entity.__name__} table")
        for field in display_column:
            table.add_column(field)
        if selection:
            results = entity.select(selection)[:n_rows]
        else:
            results = entity.select()[:n_rows]
        for row in results:
            table.add_row(*[str(getattr(row, field.header)) for field in table.columns if field.header in display_column])
        return table
