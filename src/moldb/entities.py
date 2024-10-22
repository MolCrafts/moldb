from pony.orm import *

def get_base_entity(entity):

    class MolDBBaseEntity(entity):
        id = PrimaryKey(int, auto=True)
        uuid = Required(str, unique=True)
        ctime = Required(float)
        mtime = Required(float)

    return MolDBBaseEntity

def get_default_entity(entity):

    BaseEntity = get_base_entity(entity)

    class MolDBDefaultEntity(BaseEntity):
        atomic_numbers = Required(IntArray)
        pbc = Required(IntArray)
        cell = Required(FloatArray)
        xyz = Required(FloatArray)

    return MolDBDefaultEntity

def get_ase_entity(name, entity, extra):

    ase_attrs = {
        'id': PrimaryKey(int),
        'unique_id': Required(str, unique=True),
        'ctime': Required(float),
        'mtime': Required(float),
        'user': Required(str),
        'numbers': Required(IntArray),
        'pbc': Required(StrArray),
        'cell': Required(FloatArray),
        'positions': Required(FloatArray),
    }
    ase_attrs.update(extra)

    return type(name, (entity,), ase_attrs)

def get_namespace_entity(name, entity):

    attrs = {
        'name': Required(str, unique=True),
        'unit': Optional(str),
        'dtype': Optional(str),
        'shape': Optional(IntArray),
        'comment': Optional(str),
        'category': Optional(str),
    }

    return type(f"{name}", (entity,), attrs)

def create_entity(name:str, defination:dict, base_entity):

    return type(name, (base_entity,), defination)

