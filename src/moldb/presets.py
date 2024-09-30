from pony.orm import *

def get_base_entity(db):

    class MolDBBaseEntity(db.Entity):
        id = PrimaryKey(int, auto=True)
        uuid = Required(str, unique=True)
        ctime = Required(float)
        mtime = Required(float)

    return MolDBBaseEntity

def get_default_entity(db):

    BaseEntity = get_base_entity(db)

    class MolDBDefaultEntity(BaseEntity):
        atomic_numbers = Required(IntArray)
        pbc = Required(IntArray)
        cell = Required(FloatArray)
        xyz = Required(FloatArray)

    return MolDBDefaultEntity

