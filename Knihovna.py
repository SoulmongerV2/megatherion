from .megatherion import *
import csv

class Knihovna:
    def __init__(self):
        self._data = Knihovna._init_lib()
        self._size = len(self._data)
        
    def add(self, name:str, author:str, genre:str, year:int) -> None:
        self._data.append_row((name, author, genre, float(year)))
        
    def remove(self, index) -> None:
        del self._data[index]
        
    def bibliography_size(self, author:str) -> int:
        return len(self._data.filter("Autor", lambda a: a == author))
    
    def export_lib(self, path:Union[Path, str]) -> None:
        """
        Exports the library into a csv file. Each line of the file represents a single entry (row) in the library.
        Uses 'unix' dialect.
        :param path: path to the 'filename' where the data will be stored 
        """
        with open(path,"w") as file:
            
            w = csv.writer(file, "unix")
            for row in self._data:
                w.writerow(row)
            
    @staticmethod
    def import_lib(path:Union[Path, str]) -> 'Knihovna':
        
        with open(path,"r") as file:
            
            r = csv.reader(file, "unix")
            ret_lib = Knihovna()            
            for line in r:
                ret_lib._data.append_row(line)
                
        return ret_lib
        ...
        
    @staticmethod
    def _init_lib():
        return DataFrame({
            "Nazev": Column([], Type.String),
            "Autor": Column([], Type.String),
            "Zanr": Column([], Type.String),
            "Rok Vydani": Column([], Type.Float)
            })