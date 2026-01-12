import numpy as np

def _print(text):
    global log
    if log:
        print(text)

class Client:
    def __init__(
        self,
        Eio:float,          # initial energy
        Bi:int,             # num batches
        gamma_i:float,      # CPU effective capacitance
        ci:int,             # CPU cycles for processing 1 batch
        fi:int,             # CPU clock freq
        P_down_avg:float,   # avg power by the app
        Pi:float,           # charging power,
        max_time:float,     # max time
        ui:float,           # upload time
        di:float,           # download time
        is_log_active=True
    ) -> None:
        self.Eio = Eio
        self.original_Eio = Eio
        self.P_down_avg = P_down_avg
        self.Pi = Pi
        self.ui = ui
        self.di = di
        self.max_time = max_time
        self.Ti = 0

        global log
        log = is_log_active


        self.epsilon_i = Bi*ci*gamma_i*fi*fi # energy per epoch
        self.tau_i = Bi*ci/fi # time per epoch (bacthes * cycles/batch / cycles/sec = sec)
        #self.Ki = self.epsilon_i + self.tau_i * (self.P_down_avg - self.Pi) # energy decreasse per epoch

        _print("New client created:")
        _print(f"Energy per epoch = {self.epsilon_i} J")
        _print(f"Time per epoch = {self.tau_i}s")
        #_print(f"Energy decrease per epoch (Ki) = {self.Ki}s")

    def _setters(self,ri,Ui,Ti,csi):
        self.ri = ri
        self.Ui = Ui
        self.Ti = Ti
        self.num_epochs = csi-ri
        self.energy_consumed_training = self.epsilon_i * self.num_epochs
        self.energy_consumed_base = self.P_down_avg * self.max_time
        self.energy_recharged = self.Pi * self.max_time
        self.energy_variation = self.energy_recharged - self.energy_consumed_base - self.energy_consumed_training
        self.Ei = self.Eio + self.energy_variation

    def _compute_Ni(self,csi):
        return (self.Eio - (self.P_down_avg-self.Pi)*self.max_time - csi*self.epsilon_i)/self.epsilon_i

    def compute(
        self, 
        ri:int,  # reduction in num of epochs 
        csi:int  # ceil num of epochs
    )->tuple:    # rtype: (Ui, Ti) = (utility, time)

        self.Ni = self._compute_Ni(csi)
        Ui = np.math.log10(1+ri/self.Ni) # utility

        Ti = csi*self.tau_i + self.ui + self.di - ri*self.tau_i # complete round time

        self._setters(ri,Ui,Ti,csi)

    def report(self):
        _print(f"Num epochs: {self.num_epochs}")
        _print(f"Reduced num epochs: {self.ri}")
        _print(f"Utility: {self.Ui}")
        _print(f"Time: {self.Ti} s")
        _print(f"Energy before: {self.Eio} J")
        _print(f"Energy consumed by training: {self.energy_consumed_training} J")
        _print(f"Energy consumed base: {self.energy_consumed_base} J")
        _print(f"Energy recharged: {self.energy_recharged} J")
        _print(f"Total energy variation: {self.energy_variation} J")
        _print(f"Energy after: {self.Ei} J")

if __name__ == "__main__":

    Emax = 3000 * 10e-3 * 3600 * 3.7 
    _print(f"Emax = {Emax} J")
    # mAh * 10e-3 A/mA * 3600 s/h * V = VAs = Ws = J

    _print("-----------------------")
    client = Client(
        Eio=0.9*Emax, # 90% SoC battery level
        Bi=100,
        gamma_i=1e-28,
        ci=0.015 * 1e9, # sec/batch * cycles/sec = cycles/batch
        fi=1e9,
        P_down_avg= 0.00000023*Emax, # 0.000023 percent/per second ~ 1% in 12 hours
        Pi=0.99*(9*1.5), # charger efficiency = 99%
        max_time=150,
        ui=4*8/10, # sending a yolo nano (4MB) in a LTE 10Mbps upload link
        di=4*8/15 # sending a yolo nano (4MB) in a LTE 15Mbps download link
    )
    _print("Client while charging")
    client.compute(30,50)
    client.report()


    _print("-----------------------")
    client = Client(
            Eio=0.9*Emax, # 90% SoC battery level
            Bi=100,
            gamma_i=1e-28,
            ci=0.015 * 1e9, # sec/batch * cycles/sec = cycles/batch
            fi=1e9,
            P_down_avg= 0.00000023*Emax, # 0.000023 percent/per second ~ 1% in 12 hours
            Pi=0,
            max_time=150,
            ui=4*8/10, # sending a yolo nano (4MB) in a LTE 10Mbps upload link
            di=4*8/15 # sending a yolo nano (4MB) in a LTE 15Mbps download link
        )
    _print("Client without charging")
    client.compute(30,50)
    client.report()