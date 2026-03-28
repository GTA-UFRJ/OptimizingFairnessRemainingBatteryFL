from wf_solver.wf_solver import WaterFillingSolver
from wf_solver.client import Client

class FlOptimizer(WaterFillingSolver):
    def __init__(
        self,
        reports_list,
        num_min_epochs: int,
        time_budget: float,
        fixed_epochs: int = 2,
    ):
        self._set_clients(reports_list, time_budget)
        super().__init__(
            self.clients_list,
            num_min_epochs,
            time_budget,
            thresh=1,
            is_log_active=False,
            fixed_epochs=fixed_epochs,
        )

    def _set_clients(self, reports_list, time_budget):
        self.clients_list = []
        for report in reports_list:
            Emax = report["battery_mAh"] * 1e-3 * 3600 * 3.7
            Eo = report["battery_soc"] * Emax / 100
            f = report["cpu_GHz"] * 1e12
            self.clients_list.append(
                Client(
                    Eio=Eo,
                    Bi=report["num_batches"],
                    gamma_i=report["gamma_est"],
                    ci=report["ci_est"],
                    fi=f,
                    P_down_avg=report["p_down_avg"],
                    Pi=0,
                    max_time=time_budget,
                    ui=4 * 8 / report["upload_Mbps"],
                    di=4 * 8 / report["download_Mbps"],
                    is_log_active=True,
                )
            )
