from .megatherion import *

class WeatherAnalyzer:
    
    def __init__(self, path:Union[Path,str]) -> None:
        self._data = DataFrame.read_json(path)
           
    def read_json(self, *path:Union[Path,str]) -> None:
        
        for p in path:
            self._data = self._data.extend(DataFrame.read_json(p))
               
    def monthly_avg(self, month:int, year:int) -> float:
        
        filtered_df = self._data.filter("rok", lambda r: r == year).filter("mesic", lambda m: m == month)
        
        temperature_values = []
        for T in filtered_df.__getitem__(0)[2:]:
            try:
                temperature_values.append(float(T))
            except:
                continue
        
        return sum(temperature_values)/len(temperature_values)
        
        
    def monthly_temp_variance(self) -> Column:
        
        ret_col = Column([], Type.Float)
        
        for row in iter(self._data):
            temperature_values = []
            for T in row[2:]:
                try:
                    temperature_values.append(float(T))
                except:
                    continue
                
            ret_col.append(round(max(temperature_values) - min(temperature_values), 1))
            
        return ret_col._data