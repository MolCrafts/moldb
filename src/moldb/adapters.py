import pony.orm as orm
import numpy as np
import io

from .entities import get_ase_entity, get_namespace_entity


def to_orm(obj):
    if isinstance(obj, np.ndarray):
        with io.BytesIO() as byte_io:
            np.save(byte_io, obj)
            return byte_io.getvalue()
    return obj


def from_orm(obj):
    if isinstance(obj, bytes):
        with io.BytesIO(obj) as byte_io:
            return np.load(byte_io)
    return obj


def load_ase(
    db_path, selection, db, table_name='ASE', extra={}
):
    from ase.db import connect

    conn = connect(db_path)

    ASEEntity = get_ase_entity(
        table_name,
        db.Entity, {key: value.pop("kind") for key, value in extra.items()}
    )
    NameSpaceEntity = get_namespace_entity(table_name, db.Entity)

    # db.bind(provider=provider, filename=filename, create_db=True)
    db.generate_mapping(create_tables=True)

    with orm.db_session:

        # register meta data
        NameSpaceEntity(name="id")
        NameSpaceEntity(name="unique_id")
        NameSpaceEntity(name="ctime")
        NameSpaceEntity(name="mtime")
        NameSpaceEntity(name="user")
        NameSpaceEntity(name="numbers", shape=[-1], dtype="int", category='atoms')
        NameSpaceEntity(name="pbc", shape=[3], dtype="bool")
        NameSpaceEntity(name="cell", unit="angstrom", shape=[3, 3], dtype="float")
        NameSpaceEntity(name="positions", unit="angstrom", shape=[-1, 3], dtype="float", category='atoms')

        NameSpaceEntity(name="energy", unit="eV", shape=[], dtype="float")
        NameSpaceEntity(name="forces", unit="eV/angstrom", shape=[-1, 3], dtype="float")
        NameSpaceEntity(name="stress", unit="eV/angstrom^3", shape=[6], dtype="float")

        if extra:
            for ex in extra:
                NameSpaceEntity(name=ex, **extra[ex])

        for row in conn.select(selection):

            data = dict(
                id=row.id,
                unique_id=row.unique_id,
                ctime=row.ctime,
                mtime=row.mtime,
                user=row.user,
                numbers=row.numbers,
                pbc=row.pbc,
                cell=row.cell,
                positions=row.positions,
            )

            for ex in extra:
                ed = row.get(ex)
                if ed is None:
                    continue
                data[ex] = ed
            ASEEntity(**{key: to_orm(value) for key, value in data.items()})
