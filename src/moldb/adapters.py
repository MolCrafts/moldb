import pony.orm as orm
import numpy as np
import io

from tqdm import tqdm

from .entities import get_ase_entity, get_namespace_entity


def to_orm(obj):
    if isinstance(obj, np.ndarray):
        # with io.BytesIO() as byte_io:
        #     np.save(byte_io, obj)
        #     return byte_io.getvalue()
        return obj.flatten().tolist()
    return obj


def from_orm(obj):
    if isinstance(obj, bytes):
        with io.BytesIO(obj) as byte_io:
            return np.load(byte_io)
    return obj


def load_ase(db_path, selection, db, table_name="ASE", extra={}):
    from ase.db import connect

    conn = connect(db_path)
    total = conn.count(selection)

    ASEEntity = get_ase_entity(table_name, db.Entity, {v['name']: v.pop("kind") for v in extra.values()})
    NameSpaceEntity = get_namespace_entity(f"{table_name}NameSpace", db.Entity)

    db.generate_mapping(create_tables=True)

    with orm.db_session:

        # register meta data
        NameSpaceEntity(name="id")
        NameSpaceEntity(name="unique_id")
        NameSpaceEntity(name="ctime")
        NameSpaceEntity(name="mtime")
        NameSpaceEntity(name="user")
        NameSpaceEntity(name="numbers", shape=[-1], dtype="int", category="atoms")
        NameSpaceEntity(name="pbc", shape=[3], dtype="bool")
        NameSpaceEntity(name="cell", unit="angstrom", shape=[3, 3], dtype="float")
        NameSpaceEntity(
            name="positions",
            unit="angstrom",
            shape=[-1, 3],
            dtype="float",
            category="atoms",
        )

        NameSpaceEntity(name="energy", unit="eV", shape=[], dtype="float")
        NameSpaceEntity(name="forces", unit="eV/angstrom", shape=[-1, 3], dtype="float")
        NameSpaceEntity(name="stress", unit="eV/angstrom^3", shape=[6], dtype="float")

        if extra:
            for ns in extra.values():
                NameSpaceEntity(**ns)

        for row in tqdm(conn.select(selection), total=total):

            ASEEntity(
                id=row.id,
                unique_id=row.unique_id,
                ctime=row.ctime,
                mtime=row.mtime,
                user=row.user,
                numbers=to_orm(row.numbers),
                pbc=to_orm(row.pbc),
                cell=to_orm(row.cell),
                positions=to_orm(row.positions),
                **{v['name']: to_orm(row.get(ase_key)) for ase_key, v in extra.items()}
            )
