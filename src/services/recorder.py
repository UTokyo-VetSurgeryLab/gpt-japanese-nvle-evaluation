import datetime
from collections import defaultdict

from src.services.write_to_excel import write_api_history_to_excel

class ApiHistoryRecorder:
    def __init__(
        self,
        excel_path:str = "",
    ):
        self.excel_path = excel_path
        self.cost_per_model = defaultdict(float)
    
    def record(
        self,
        model_str: str,
        cost: float,
    ):
        self.cost_per_model[model_str] += cost
    
    def export(self):
        dt_now = datetime.datetime.now()
        now = dt_now.strftime('%Y/%m/%d %H:%M')
        for model, cost in self.cost_per_model.items():
            print(model, cost)
            write_api_history_to_excel(
                date_time=now,
                value=cost,
                model=model,
                excel_path=self.excel_path
            )
        self.cost_per_model = defaultdict(float)
