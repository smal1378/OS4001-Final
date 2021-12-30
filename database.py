# Save & Load data to or from files
import os.path
from typing import Generator, Dict
import pickle


class Database:
    class Node:
        def __init__(self, key, start):
            self.key = key
            self.start = start

    _dict = {}

    def __new__(cls, *args, **kwargs):
        if len(args) >= 1:
            filename = args[0]
        elif 'filename' in kwargs:
            filename = kwargs['filename']
        else:
            filename = "database"
        filename = os.path.abspath(filename)
        if filename not in Database._dict:
            return super(Database, cls).__new__(cls)
        return Database._dict[filename]

    def __init__(self, filename: str = "database"):
        self.filename = os.path.abspath(filename)
        if self.filename in Database._dict:
            return  # This is not a new obj!
        Database._dict[self.filename] = self
        self._change_flag: bool = False
        self._change_header_flag: bool = False
        self._header: Dict[str, Database.Node]
        self._values = {}
        if os.path.exists(self.filename+".header"):
            with open(self.filename+".header", "rb") as file:
                self._header = pickle.load(file)
        else:
            with open(self.filename+".header", "wb") as file:
                self._header = {}
                pickle.dump(self._header, file)
            open(self.filename+".bin", "wb").close()  # create it

    def __getitem__(self, item):
        """
        Get a value for saved key,
        :param item: key of a value
        :return: value
        """
        if item not in self._header:
            raise IndexError(f"key {item} not found!")
        node = self._header[item]
        if item not in self._values:
            with open(self.filename+".bin", "rb") as file:
                file.seek(node.start)
                self._values[item] = pickle.load(file)
        return self._values[item]
    get = __getitem__

    def __setitem__(self, key, value):
        """
        Save or replace a value with a key
        :param key: key of value, you can retrieve value with this key
        :param value: the value to be saved,
        """
        if key in self._header:
            self._values[key] = value
            self._change_flag = True
        else:
            with open(self.filename+".bin", "ab") as file:
                new = Database.Node(key, file.tell())
                self._header[key] = new
                self._change_header_flag = True
                self._values[key] = value
                pickle.dump(value, file)
    set = __setitem__

    def __contains__(self, item):
        return item in self._header

    def keys(self) -> Generator:
        for node in self._header:
            yield node.key

    def flash(self):
        """
        Flushes buffer and saves everything to file
        """
        if self._change_flag:
            self._change_header_flag = True
            with open(self.filename+".bin_tmp", "wb") as tmp_file, open(self.filename+".bin", "rb") as file:
                for key, node in self._header.items():
                    if key in self._values:
                        data = self._values[key]
                    else:
                        file.seek(node.start)
                        data = pickle.load(file)
                    node.start = tmp_file.tell()
                    pickle.dump(data, tmp_file)
            os.remove(self.filename + ".bin")
            os.rename(self.filename + ".bin_tmp", self.filename + ".bin")

        if self._change_header_flag:
            with open(self.filename+".header_tmp", "wb") as file:
                pickle.dump(self._header, file)
            os.remove(self.filename+".header")
            os.rename(self.filename+".header_tmp", self.filename+".header")

    def clear_cache(self):
        """
        Clears memory cache to avoid extra memory usage.
        """
        self.flash()  # save everything
        self._values.clear()  # delete cache
