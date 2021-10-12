import os

def format_audio(audioList: list) -> str:
    """
    Naformatuje hodnotu vracenou z `get_dir()` tak, aby to bylo citelne.
    Pouziva to `bota naga`
    """
    message = ""
    for (idx, value) in enumerate(audioList, start=1):
        value = value.replace(".mp3", "").replace("_", " ")
        message += f"{idx}: {value}\n"
    return message


def sorted_ls(path):
    """
    `listdir`, ale serazeny podle data pridani (od nejstarsiho po nejnovejsi)
    """
    # https://stackoverflow.com/a/4500607
    mtime = lambda f: os.stat(os.path.join(path, f)).st_mtime
    return list(sorted(os.listdir(path), key=mtime))


def get_list(file):
    """Nacte radky souboru do listu a vrati ho."""
    getList = list()
    with open(file) as f:
        for line in f:
            getList.append(line.strip())
    return getList


def get_dir(directory):
    """
    Nacte soubory z nejakeho adresare do listu a prilozi jim ID.
    Pouziva to `bota naga`
    """
    getList = []

    for i in sorted_ls(directory):
        getList.append(i)

    return getList
