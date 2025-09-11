
from pathlib import Path
import pandas as pd

class DataLoader:
    def __init__(self, config_mgr):
        self.config_mgr = config_mgr

    def excel_file(self, path: Path):
        path = Path(path) if path else None
        if not path or not path.exists(): return None
        return pd.ExcelFile(path)

    def read_df(self, path: Path, sheet: str):
        xls = self.excel_file(path)
        if not xls or sheet not in xls.sheet_names: return None
        return xls.parse(sheet)
