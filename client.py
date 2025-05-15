import numpy as np

class Client:
    def __init__(
        self,
        Eio:float,          # initial energy
        Bi:int,             # num batches
        gamma_i:float,      # CPU effective capacitance
        ci:int,             # CPU cycles for processing 1 batch
        fi:int,             # CPU clock freq
        P_down_avg:float,   # avg power consumption
        Pi:float,           # charging power,
        ui:float,           # upload time
        di:float,           # download time
    ) -> None:
        self.Eio = Eio
        self.P_down_avg = P_down_avg
        self.Pi = Pi
        self.ui = ui
        self.di = di

        self.epsilon_i = Bi*ci*gamma_i*fi*fi # energy per epoch
        self.tau_i = Bi*ci/fi # time per epoch (bacthes * cycles/batch / cycles/sec = sec)

        print(f"Energy per epoch = {self.epsilon_i} J")
        print(f"Time per epoch = {self.tau_i}s")

    def compute(
        self, 
        ri:int,  # reduction in num of epochs 
        csi:int  # ceil num of epochs
    )->tuple:    # rtype: (Ui, Ti) = (utility, time)
        
        # energy consumption minus charging per epoch
        Ki = self.epsilon_i + self.tau_i * (self.P_down_avg - self.Pi) 

        Ni = (self.Eio - csi*Ki)/Ki

        # utility
        Ui = np.math.log2(1+ri/Ni)
        
        # For sanity check
        assert np.math.log2(self.Eio - csi*Ki + ri*Ki) == Ui + np.math.log2(Ni*Ki)
        print(f"Energy before: {self.Eio}")
        print(f"Energy after: {self.Eio - Ki * (csi-ri)}")
        print(f"Energy variation: {-Ki * (csi-ri)}")

        # complete round time
        Ti = csi*self.tau_i + self.ui + self.di - ri*self.tau_i

        return Ui, Ti

if __name__ == "__main__":

    Emax = 4000 * 10e-3 * 3600 * 3.7 
    print(f"Emax = {Emax}")
    # mAh * 10e-3 A/mA * 3600 s/h * V = VAs = Ws = J

    client = Client(
        Eio=0.9*Emax, # 90% SoC battery level
        Bi=100,
        gamma_i=1e-28,
        ci=0.015 * 1e9, # sec/batch * cycles/sec = cycles/batch
        fi=1e9,
        P_down_avg= 0.0028*Emax, # 0.00345 percent/per second ~ 100% in 10 hours
        Pi=0.99*10, # charger efficiency = 99%
        ui=4*8/10, # sending a yolo nano (4MB) in a LTE 10Mbps upload link
        di=4*8/15 # sending a yolo nano (4MB) in a LTE 15Mbps download link
    )

    print(client.compute(30,50))