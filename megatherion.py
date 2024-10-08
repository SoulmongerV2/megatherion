from abc import abstractmethod, ABC
from json import load
from numbers import Real
from pathlib import Path
from typing import Dict, Iterable, Iterator, Tuple, Union, Any, List, Callable
from enum import Enum
from collections.abc import MutableSequence
import random


class Type(Enum):
    Float = 0
    String = 1


def to_float(obj) -> float:
    """
    casts object to float with support of None objects (None is cast to None)
    """
    return float(obj) if obj is not None else None


def to_str(obj) -> str:
    """
    casts object to float with support of None objects (None is cast to None)
    """
    return str(obj) if obj is not None else None


def common(iterable): # from ChatGPT
    """
    returns True if all items of iterable are the same.
    :param iterable:
    :return:
    """
    try:
        # Nejprve zkusíme získat první prvek iterátoru
        iterator = iter(iterable)
        first_value = next(iterator)
    except StopIteration:
        # Vyvolá výjimku, pokud je iterátor prázdný
        raise ValueError("Iterable is empty")

    # Kontrola, zda jsou všechny další prvky stejné jako první prvek
    for value in iterator:
        if value != first_value:
            raise ValueError("Not all values are the same")

    # Vrací hodnotu, pokud všechny prvky jsou stejné
    return first_value


class Column(MutableSequence):# implement MutableSequence (some method are mixed from abc)
    """
    Representation of column of dataframe. Column has datatype: float columns contains
    only floats and None values, string columns contains strings and None values.
    """
    def __init__(self, data: Iterable, dtype: Type):
        self.dtype = dtype
        self._cast = to_float if self.dtype == Type.Float else to_str
        # cast function (it casts to floats for Float datatype or
        # to strings for String datattype)
        self._data = [self._cast(value) for value in data]

    def __len__(self) -> int:
        """
        Implementation of abstract base class `MutableSequence`.
        :return: number of rows
        """
        return len(self._data)

    def __getitem__(self, item: Union[int, slice]) -> Union[float,
                                    str, list[str], list[float]]:
        """
        Indexed getter (get value from index or sliced sublist for slice).
        Implementation of abstract base class `MutableSequence`.
        :param item: index or slice
        :return: item or list of items
        """
        return self._data[item]

    def __setitem__(self, key: Union[int, slice], value: Any) -> None:
        """
        Indexed setter (set value to index, or list to sliced column)
        Implementation of abstract base class `MutableSequence`.
        :param key: index or slice
        :param value: simple value or list of values

        """
        self._data[key] = self._cast(value)

    def append(self, item: Any) -> None:
        """
        Item is appended to column (value is cast to float or string if is not number).
        Implementation of abstract base class `MutableSequence`.
        :param item: appended value
        """
        self._data.append(self._cast(item))

    def insert(self, index: int, value: Any) -> None:
        """
        Item is inserted to colum at index `index` (value is cast to float or string if is not number).
        Implementation of abstract base class `MutableSequence`.
        :param index:  index of new item
        :param value:  inserted value
        :return:
        """
        self._data.insert(index, self._cast(value))

    def __delitem__(self, index: Union[int, slice]) -> None:
        """
        Remove item from index `index` or sublist defined by `slice`.
        :param index: index or slice
        """
        del self._data[index]

    def permute(self, indices: List[int]) -> 'Column':
        """
        Return new column which items are defined by list of indices (to original column).
        (eg. `Column(["a", "b", "c"]).permute([0,0,2])`
        returns  `Column(["a", "a", "c"])
        :param indices: list of indexes (ints between 0 and len(self) - 1)
        :return: new column
        """
        assert len(indices) == len(self)
        ...

    def copy(self) -> 'Column':
        """
        Return shallow copy of column.
        :return: new column with the same items
        """
        # FIXME: value is cast to the same type (minor optimisation problem)
        return Column(self._data, self.dtype)

    def get_formatted_item(self, index: int, *, width: int):
        """
        Auxiliary method for formating column items to string with `width`
        characters. Numbers (floats) are right aligned and strings left aligned.
        Nones are formatted as aligned "n/a".
        :param index: index of item
        :param width:  width
        :return:
        """
        assert width > 0
        if self._data[index] is None:
            if self.dtype == Type.Float:
                return "n/a".rjust(width)
            else:
                return "n/a".ljust(width)
        return format(self._data[index],
                      f"{width}s" if self.dtype == Type.String else f"-{width}.2g")

class DataFrame:
    """
    Dataframe with typed and named columns
    """
    def __init__(self, columns: Dict[str, Column]):
        """
        :param columns: columns of dataframe (key: name of dataframe),
                        lengths of all columns has to be the same
        """
        assert len(columns) > 0, "Dataframe without columns is not supported"
        self._size = common(len(column) for column in columns.values())
        # deep copy od dict `columns`
        self._columns = {name: column.copy() for name, column in columns.items()}

    def __getitem__(self, index: int) -> Tuple[Union[str,float]]:
        """
        Indexed getter returns row of dataframe as tuple
        :param index: index of row
        :return: tuple of items in row
        """
        try:
            return tuple(c[index] for c in self._columns.values())
        except IndexError:
            print("Index out of bounds.")
            
    def __delitem__(self, index: int) -> None:
        """
        Delete a row at the selected index from a DataFrame.
        :param index: Index of the row to be deleted
        """
        try:
            for col in self.columns:
                del self._columns[col][index]
            self._size -= 1
        except IndexError:
            print("Entry at index " + str(index) + " does not exist.")
        ...

    def __iter__(self) -> Iterator[Tuple[Union[str, float]]]:
        """
        :return: iterator over rows of dataframe
        """
        for i in range(len(self)):
            yield tuple(c[i] for c in self._columns.values())

    def __len__(self) -> int:
        """
        :return: count of rows
        """
        return self._size

    @property
    def columns(self) -> Iterable[str]:
        """
        :return: names of columns (as iterable object)
        """
        return self._columns.keys()

    def __repr__(self) -> str:
        """
        :return: string representation of dataframe (table with aligned columns)
        """
        lines = []
        lines.append(" ".join(f"{name:12s}" for name in self.columns))
        for i in range(len(self)):
            lines.append(" ".join(self._columns[cname].get_formatted_item(i, width=12)
                                     for cname in self.columns))
        return "\n".join(lines)
    
    def _skeleton(self) -> 'DataFrame':
        """
        Returns a new DataFrame which copies the input DataFrame structure (names and dtypes of columns) but excludes data
        :return: new empty dataframe with identical column structure 
        """
        dtypes = []
        
        for key in self.columns:
            dtypes.append(self._columns[key].dtype)
            
        return DataFrame({key: Column([], dtype) for key, dtype in zip(self.columns, dtypes)})    

    def append_column(self, col_name:str, column: Column) -> None:
        """
        Appends new column to dataframe (its name has to be unique).
        :param col_name:  name of new column
        :param column: data of new column
        """
        if col_name in self._columns:
            raise ValueError("Duplicate column name")
        self._columns[col_name] = column.copy()

    def append_row(self, row: Iterable) -> None:
        """
        Appends new row to dataframe.
        :param row: tuple of values for all columns
        """
        assert len(row) == len(self.columns), "Input does not match the number of columns in this DataFrame."
        
        li = list(row)
        
        for key in self.columns:
            self._columns[key].append(li.pop(0))
            
        self._size += 1

    def filter(self, col_name:str,
               predicate: Callable[[Union[float, str]], bool]) -> 'DataFrame':
        """
        Returns new dataframe with rows which values in column `col_name` returns
        True in function `predicate`.

        :param col_name: name of tested column
        :param predicate: testing function
        :return: new dataframe
        """
        assert col_name in self.columns, "DataFrame doesn't contain " + col_name + " column."
        
        ret_df = self._skeleton()
        index = list(self.columns).index(col_name)
        
        for row in iter(self):
            if predicate(row[index]):
                ret_df.append_row(row)
                
        return ret_df


    def sort(self, col_name:str, ascending=True) -> 'DataFrame':
        """
        Sort dataframe by column with `col_name` ascending or descending.
        :param col_name: name of key column
        :param ascending: direction of sorting
        :return: new dataframe
        """
        
        ret_df = self._skeleton()
        
        for row in sorted(iter(self), key = lambda col: col[list(self.columns).index(col_name)], reverse = not ascending):
            ret_df.append_row(row)
        
        return ret_df

    def describe(self) -> str:
        """
        similar to pandas but only with min, max and avg statistics for floats and count"
        :return: string with formatted decription
        """
        ...

    def inner_join(self, other: 'DataFrame', self_key_column: str,
                   other_key_column: str) -> 'DataFrame':
        """
            Inner join between self and other dataframe with join predicate
            `self.key_column == other.key_column`.

            Possible collision of column identifiers is resolved by prefixing `_other` to
            columns from `other` data table.
        """
        ...
        
    def extend(self, *donor_df: 'DataFrame') -> 'DataFrame':
        """
        Joins data from DataFrames with identical column structure into a new DataFrame
        :return: new dataframe containing data from all input dataframes
        """
        for df in donor_df:
            assert df.columns == self.columns, "Input DataFrames do not match in structures"
            
        ret_df = self._skeleton()
        
        for df in (self,) + donor_df:
            for row in df:
                ret_df.append_row(row)
            
        return ret_df
        

    def setvalue(self, col_name: str, row_index: int, value: Any) -> None:
        """
        Set new value in dataframe.
        :param col_name:  name of culumns
        :param row_index: index of row
        :param value:  new value (value is cast to type of column)
        :return:
        """
        col = self._columns[col_name]
        col[row_index] = col._cast(value)
    
    def sum_by(self, category_column, data_columns: Iterable):
        
        #input check
        assert category_column in self.columns, "DataFrame doesn't contain " + category_column + " column."
        
        for key in data_columns:
            assert key in data_columns, "DataFrame doesn't contain " + key + " column."
            assert self._columns[key].dtype == Type.Float, "Data column " + key + " is not a float type."
        
        
        #produce a new category column with unique values only, None excluded
        
        
        squished_category_column = Column(list(set(self._columns[category_column]._data)),self._columns[category_column].dtype)
        
        #set up a return DataFrame
        ret_df = DataFrame({"Cat(" + category_column + ")": squished_category_column})
        
        #sum up the totals of categorical values in data columns + append the values as new columns        
        cat_index = list(self.columns).index(category_column)
        
        for dc in data_columns:
            
            dc_index = list(self.columns).index(dc)
            dc_dict = {}
            
            for row in self:
                
                if row[cat_index] is None:
                    continue
                
                if row[cat_index] in dc_dict:
                    if row[dc_index] is not None:
                        try:
                            dc_dict[row[cat_index]] += row[dc_index]
                        except TypeError:
                            continue
                else:
                    dc_dict[row[cat_index]] = row[dc_index]
            
            ret_df.append_column(dc, Column(list(dc_dict.values()), Type.Float))
               
        return ret_df
    
    
            
    def cummin(self, colname, skipna=True):
        
        #input check
        assert colname in self.columns, "Dataframe doesn't contain " + colname + " column."
        
        column = self._columns[colname]
        
        ret_col = Column([], column.dtype)
        min_current = column[0]
        
        if skipna:
            for val in column:
                
                if min_current is None:
                    min_current = val
                
                if val is None:
                    ret_col.append(min_current)
                    continue
                
                if val < min_current:
                    min_current = val
                ret_col.append(min_current)
                
            return ret_col
        
        index = 0
        for val in column:
            if val is None:
                for i in range(index,column.__len__()):
                    ret_col.append(None)
                return ret_col
            if val < min_current:
                min_current = val
            ret_col.append(min_current)
            index += 1
                    
        return ret_col       
    
    def unique(self, col_name:str) -> 'DataFrame':
        """
        Create a new DataFrame only containing rows with the first occurence of a unique value in a selected column.
        :param col_name: column selected for unique value search
        :return: new reduced dataframe  
        """
        
        assert col_name in self.columns, "Dataframe does not contain " + col_name + " column."
        
        ret_df = self._skeleton()
        
        unique_values = []
        index = list(self.columns).index(col_name)
        
        for row in self:
            if row[index] not in unique_values:
                unique_values.append(row[index])
                ret_df.append_row(row)
            
        return ret_df 
    
    def sample(self, sample_size:int, *, norepeat=False) -> 'DataFrame':
        """
        Creates a new DataFrame containing randomly selected entries from the original DataFrame
        :param sample_size: defines the number of randomly selected entries
        :param norepeat: Optional. Selects whether the randomly sampled DataFrame can contain repeat entries. Defaults to False.
        :return: new randomly sampled DataFrame
        """
        if norepeat:
            assert sample_size < self._size, "Sample size exceeds the number of entries, use 'norepeat=False' for duplicate samples."
            ret_df = self._skeleton()
            repeats = []
            while sample_size > 0:
                randindex = random.randrange(self._size)
                if randindex not in repeats:
                    repeats.append(randindex)
                    ret_df.append_row(self[randindex])
                    sample_size -= 1
            
            return ret_df
        
        ret_df = self._skeleton()
        
        for _ in range(sample_size):
            ret_df.append_row(self[random.randrange(self._size)])
            
        return ret_df
       

    @staticmethod
    def read_csv(path: Union[str, Path]) -> 'DataFrame':
        """
        Read dataframe by CSV reader
        """
        return CSVReader(path).read()

    @staticmethod
    def read_json(path: Union[str, Path]) -> 'DataFrame':
        """
        Read dataframe by JSON reader
        """
        return JSONReader(path).read()


class Reader(ABC):
    def __init__(self, path: Union[Path, str]):
        self.path = Path(path)

    @abstractmethod
    def read(self) -> DataFrame:
        raise NotImplemented("Abstract method")


class JSONReader(Reader):
    """
    Factory class for creation of dataframe by CSV file. CSV file must contain
    header line with names of columns.
    The type of columns should be inferred from types of their values (columns which
    contains only value has to be floats columns otherwise string columns),
    """
    def read(self) -> DataFrame:
        with open(self.path, "rt") as f:
            json = load(f)
        columns = {}
        for cname in json.keys(): # cyklus přes sloupce (= atributy JSON objektu)
            dtype = Type.Float if all(value is None or isinstance(value, Real)
                                      for value in json[cname]) else Type.String
            columns[cname] = Column(json[cname], dtype)
        return DataFrame(columns)


class CSVReader(Reader):
    """
    Factory class for creation of dataframe by JSON file. JSON file must contain
    one object with attributes which array values represents columns.
    The type of columns are inferred from types of their values (columns which
    contains only value is floats columns otherwise string columns),
    """
    def read(self) -> 'DataFrame':
        ...


if __name__ == "__main__":

    df = DataFrame.read_json("./test_data.json")
    
    print(df)
    
    
###