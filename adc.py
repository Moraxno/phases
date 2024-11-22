from matplotlib.widgets import CheckButtons
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import functools as ft

from sklearn.cluster import DBSCAN



V_SUPPLY = 12
LDO_STEEPNESS = 100
LDO_MAX = 5
LDO_DROPOUT = 0.5
VREF_DROPOUT = 0.1


WORKING_STATE_COLOR = {
    -1: "blue",
    0: "black",
    1: "green"
}

class VivaDevice:
    def __init__(self, v_steepness: float = 9.0, ldo_delay: float = 0.500, adc_delay: float = 0.600, adc_check_delay: float = 0.100, adc_cutoff = 2.45, color: str = "red", v_phase: float = 0):
        self.v_steepness = v_steepness
        self.ldo_delay = ldo_delay
        self.vref_delay = adc_delay
        self.adc_cutoff = adc_cutoff
        self.adc_check_delay = adc_check_delay

        self.color=color
        self.label="Device"

        self.v = 0.0
        self.ldo = 0.0
        self.adc_enable = 0.0

        self.working_state = 0

        self.phase = v_phase

        self.history_t = [0.0]
        self.history_v = [0.0]
        self.history_ldo = [0.0]
        self.history_adc = [0.0]
        # self.history_angular_velocity = [init_angular_velocity]

        # self.history_acceleration = [-self.gravity / self.length * np.sin(self.angle)]

    def attach_axis(self, flat_ax, phase_ax, flat_ax2, time_ax):
        self.time_ax = time_ax
        self.v_plot,   = time_ax.plot([], [], c=self.color, alpha=0.33, )
        self.ldo_plot, = time_ax.plot([], [], c=self.color, alpha=0.33, ls="--")
        self.adc_plot, = time_ax.plot([], [], c=self.color, alpha=0.33, ls=":")

        self.flat_phase,  = flat_ax.plot( [], [], c=WORKING_STATE_COLOR[0], alpha=0.95, linewidth=2)
        self.flat_phase2, = flat_ax2.plot([], [], c=WORKING_STATE_COLOR[0], alpha=0.95, linewidth=2)

        self.phase_plot, = phase_ax.plot([], [], [], c=WORKING_STATE_COLOR[0], label=self.label, alpha=0.33, marker="o", ms=3, linewidth=4)
        

    def step(self, dt: float):
        if self.history_t[-1] > 1.5:
            return

        # === V SUPPLY ===
        self.v += self.v_steepness * dt + 5 * np.sin(self.history_t[-1] * 3 + self.phase) * dt
        
        if self.v > V_SUPPLY:
            self.v = V_SUPPLY
        elif self.v < 0:
            self.v = 0

        
        # === LDO ===
        if self.history_t[-1] >= self.ldo_delay:
            self.ldo += LDO_STEEPNESS * dt

        if self.ldo > LDO_MAX:
            self.ldo = LDO_MAX
        
        if self.ldo > self.v - LDO_DROPOUT: 
            self.ldo = self.v - LDO_DROPOUT
        

        # === ADC ENABLE ===
        if self.history_t[-1] >= self.vref_delay:
            self.adc_enable = 3.3
        

        # === ADC WORKS ===
        if self.history_t[-1] >= (self.vref_delay + self.adc_check_delay):
            if self.working_state == 0:
                self.working_state = 1 if self.ldo > self.adc_cutoff else -1
        

        self.history_t.append(self.history_t[-1] + dt)
        self.history_v.append(self.v)
        self.history_ldo.append(self.ldo)
        self.history_adc.append(self.adc_enable)

        

    def update(self):
        self.v_plot.set_xdata(self.history_t)
        self.v_plot.set_ydata(self.history_v)
        self.v_plot.set(color=WORKING_STATE_COLOR[self.working_state])

        self.ldo_plot.set_xdata(self.history_t)
        self.ldo_plot.set_ydata(self.history_ldo)
        self.ldo_plot.set(color=WORKING_STATE_COLOR[self.working_state])

        self.adc_plot.set_xdata(self.history_t)
        self.adc_plot.set_ydata(self.history_adc)
        self.adc_plot.set(color=WORKING_STATE_COLOR[self.working_state])

        self.phase_plot.set_data_3d(self.history_v, self.history_ldo, self.history_adc)
        self.phase_plot.set(color=WORKING_STATE_COLOR[self.working_state])

        self.flat_phase.set_xdata(self.history_v)
        self.flat_phase.set_ydata(self.history_adc)
        self.flat_phase.set(color=WORKING_STATE_COLOR[self.working_state])

        
        self.flat_phase2.set_xdata(self.history_v)
        self.flat_phase2.set_ydata(self.history_adc)
        self.flat_phase2.set(color=WORKING_STATE_COLOR[self.working_state])


        if self.history_t[-1] > (self.adc_check_delay):
            index_delay = np.sum(np.array(self.history_t) < (self.adc_check_delay))

            self.flat_phase2.set_xdata(self.history_v[index_delay:])
            self.flat_phase2.set_ydata(self.history_adc[:-index_delay])
            self.flat_phase2.set(color=WORKING_STATE_COLOR[self.working_state])

import random 

def main():
    global fsm_plot

    # ((view_ax, phase_ax), (time_ax, fsm_ax))
    fig = plt.figure(figsize=plt.figaspect(2.))

    flat_ax   = fig.add_subplot(2, 2, 1)
    phase_ax  = fig.add_subplot(2, 2, 2, projection="3d")
    time_ax   = fig.add_subplot(2, 2, 3)
    flat_ax2 = fig.add_subplot(2, 2, 4)
    

    devs = []

    # 1 === BULK ===
    for v_steep in np.linspace(3.0, 7.0, 5):
        for v_phase in np.linspace(0, 2*np.pi, 21):
            devs.append(VivaDevice(v_steepness=v_steep, v_phase=v_phase))

    random.shuffle(devs)

    # 2 === SLIM ===
    # colors = ["r", "yellow", "green", "blue"]
    # i = 0
    # for v_steep in np.linspace(3.0, 7.0, 2):
    #     for v_phase in np.linspace(0, 1*np.pi, 2):
    #         devs.append(VivaDevice(v_steepness=v_steep, v_phase=v_phase, color=colors[i]))
    #         i += 1

    for d in devs:
        d.attach_axis(time_ax=time_ax, flat_ax=flat_ax, phase_ax=phase_ax, flat_ax2=flat_ax2)
    
    time_ax.set(xlim=[0, 2], ylim=[-0.1, V_SUPPLY * 1.25], xlabel=r"Zeit $t$ [s]", ylabel=r"Spannung $U$ [V]")
    phase_ax.set(xlim=[-2, V_SUPPLY * 1.25], ylim=[-1, 6], zlim=[-1, 6], xlabel=r"$V_\text{supply}$", ylabel=r"$V_\text{LDO}$", zlabel=r"$\text{ADC}_\text{EN}$")
    
    flat_ax.set(xlim=[-2, V_SUPPLY * 1.25], ylim=[-1, 6], xlabel=r"$V_\text{supply}$", ylabel=r"$\text{ADC}_\text{EN}$")
    flat_ax2.set(xlim=[-2, V_SUPPLY * 1.25], ylim=[-1, 6], xlabel=r"$V_\text{supply}$", ylabel=r"$\text{ADC}_\text{EN} - t_\text{delay}$")

    # rax = time_ax.inset_axes([0.0, 0.0, 0.5, 0.25])
    # check = CheckButtons(
    #     ax=rax,
    #     labels=[p.label for p in pendulums],
    #     actives=[True for p in pendulums],
    #     label_props={'color': [p.color for p in pendulums]},
    #     frame_props={'edgecolor': [p.color for p in pendulums]},
    #     check_props={'facecolor': [p.color for p in pendulums]},
    # )




        # .figure.canvas.draw_idle()

    # # check.on_clicked(callback)

    # fsm_plot = fsm_ax.scatter([], [], c="k", alpha=0.1, s=20)

    ani = animation.FuncAnimation(fig=fig, func=ft.partial(update, devs=devs) , interval=1000/FPS)
    plt.show()


LABEL_COLORS = {
    -1: "gray",
    0: "green",
    1: "blue",
    2: "red",
    3: "yellow",
}


FPS = 12

def update(frame, devs):
    for dev in devs:
        for _ in range(10):
            dev.step(1/(10 * FPS))
        dev.update()


if __name__ == "__main__":
    main()
