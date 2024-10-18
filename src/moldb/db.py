import pony.orm as orm
from .entities import create_entity
from rich.table import Table
from rich.console import Console
from .adapters import load_ase

class Database(orm.Database):

    def def_entity(self, name:str, definition:dict, base_entity=None):
        if base_entity is None:
            base_entity = self.Entity
        entity = create_entity(name, definition, base_entity)
        return entity

    @orm.db_session
    def show_table(self, entity, n_rows:int=5, columns:list[str]|None=None):

        if isinstance(entity, str):
            entity = self.entities[entity]

        rows = entity.select()[:n_rows]
        table = Table(title=entity.__name__)
        if columns is None:
            columns = [attr.name for attr in entity._attrs_]
        for col in columns:
            table.add_column(col)
        for row in rows:
            fields = []
            for col in columns:
                field = getattr(row, col)
                if isinstance(field, bytes):
                    field = "numpy.ndarray"
                fields.append(str(field))
            table.add_row(*fields)
        consolo = Console()
        consolo.print(table)

    def load_ase(self, db_path, selection, table_name, extra={}):
        return load_ase(db_path, selection, self, table_name, extra)