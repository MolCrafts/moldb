import requests, tarfile, io
import numpy as np

print("Downloading QM9 dataset...")
qm9_url = "https://ndownloader.figshare.com/files/3195389"
qm9_bytes = requests.get(qm9_url, allow_redirects=True).content
qm9_fobj = io.BytesIO(qm9_bytes)
qm9_fobj.seek(0)
qm9_tar = tarfile.open(fileobj=qm9_fobj, mode='r:bz2')
names = qm9_tar.getnames()

print("Downloading QM9 exclude list...")
exclude_url = "https://figshare.com/ndownloader/files/3195404"
exclude_bytes = requests.get(exclude_url, allow_redirects=True).content
exclude_fobj = io.TextIOWrapper(io.BytesIO(exclude_bytes))
exclude = [int(line.split()[0]) for line in exclude_fobj.readlines()[9:-1]]
names = [name for name in names if int(name[-10:-4]) not in exclude]

_labels = ['tag', 'index', 'A', 'B', 'C', 'mu', 'alpha', 'homo',
            'lumo', 'gap', 'r2', 'zpve', 'U0', 'U', 'H', 'G', 'Cv']
_label_ind = {k: i for i, k in enumerate(_labels)}

def load_qm9_tar(name):
    f = io.TextIOWrapper(qm9_tar.extractfile(name))
    lines = f.readlines()
    elems = [l.split()[0] for l in lines[2:-3]]
    coord = [[i.replace('*^', 'E') for i in l.split()[1:4]]
            for l in lines[2:-3]]
    elems = np.array(elems, np.int32)
    coord = np.array(coord, float)

    data = dict()
    for k in _labels:  # TODO: remap keywords
        data[k] = float(lines[1].split()[_label_ind[k]])
    
qm9_ds = load_qm9_tar(names)