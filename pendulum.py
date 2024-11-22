from matplotlib.widgets import CheckButtons
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from sklearn.cluster import DBSCAN

GRAVITY = 9.81
LENGTH = 0.5



fig, ((view_ax, phase_ax), (time_ax, fsm_ax)) = plt.subplots(2, 2)
t = np.linspace(0, 3, 40)
g = -9.81
v0 = 12
z = g * t**2 / 2 + v0 * t

v02 = 5
z2 = g * t**2 / 2 + v02 * t

scat = view_ax.scatter(t[0], z[0], c="b", s=20,)
scat2 = view_ax.scatter(t[0], z[0], c="r", s=20,)

line = view_ax.plot(t[0], z2[0], c="b")[0]
line2 = view_ax.plot(t[0], z2[0], c="r")[0]



angle = np.pi * 0.995
angular_velocity = 0

angle2 = np.pi * 0.1
angular_velocity2 = 0

DATA_X = []
DATA_Y = []
DATA_X2 = []
DATA_Y2 = []

T = []

scat_data, = phase_ax.plot([], [], ls='', marker="o", color="b", ms=1)
scat_data2, = phase_ax.plot([], [], ls='', marker="o", color="r", ms=1)

t_data1 = time_ax.plot([], [], color="b")[0]
t_data2 = time_ax.plot([], [], color="r")[0]


import datetime
last_t = datetime.datetime.now()

class Pendulum:
    def __init__(self, color: str, length: float = 0.5, init_angle: float = np.pi/4, init_angular_velocity: float = 0, friction: float = 0.0, gravity: float = 9.81, label: None | str = None):
        self.length = length
        self.angle = init_angle
        self.angular_velocity = init_angular_velocity
        self.gravity = gravity

        self.friction = friction


        self.color = color
        self.label = label

        self.history_t = [0.0]
        self.history_angle = [init_angle]
        self.history_angular_velocity = [init_angular_velocity]

        self.history_acceleration = [-self.gravity / self.length * np.sin(self.angle)]



    def attach_axis(self, view_ax, phase_ax, time_ax):
        self.view_ax = view_ax
        self.string, = self.view_ax.plot([0], [0], c=self.color, label=self.label)
        self.ball = self.view_ax.scatter([0], [0], c=self.color, s=30)

        self.phase_ax = phase_ax
        self.phase_points, = phase_ax.plot(self.history_angle, self.history_angular_velocity, c=self.color, marker="o", ms=3, alpha=0.1)

        self.time_ax = time_ax
        self.angle_time_plot, = time_ax.plot(self.history_t, self.history_angle, c=self.color, label=self.label)
        self.vel_time_plot, = time_ax.plot(self.history_t, self.history_angular_velocity, c=self.color, ls="--", label=self.label)

    def step(self, dt: float):
        # ai
        angular_acceleration = -self.gravity / self.length * np.sin(self.angle) - self.angular_velocity * self.friction
        # vi+1/2
        self.angular_velocity += angular_acceleration * dt/2
        # xi+1
        self.angle += self.angular_velocity * dt
        # ai+1
        angular_acceleration = -self.gravity / self.length * np.sin(self.angle) - self.angular_velocity * self.friction
        # vi+1
        self.angular_velocity += angular_acceleration * dt/2

        self.history_t.append(self.history_t[-1] + dt)
        self.history_acceleration.append(angular_acceleration)
        self.history_angular_velocity.append(self.angular_velocity)
        self.history_angle.append(self.angle)

    def update(self):
        x = np.sin(self.angle) * self.length
        y = -np.cos(self.angle) * self.length

        self.string.set_xdata([0.0, x])
        self.string.set_ydata([0.0, y])

        data = np.stack([x, y]).T
        self.ball.set_offsets(data)

        self.phase_points.set_xdata(self.history_angle)
        self.phase_points.set_ydata(self.history_angular_velocity)

        
        self.angle_time_plot.set_xdata(self.history_t)
        self.angle_time_plot.set_ydata(self.history_angle)

        self.vel_time_plot.set_xdata(self.history_t)
        self.vel_time_plot.set_ydata(self.history_angular_velocity)
        

FPS = 20



small_angle_pendulum = Pendulum("b", 0.4, 10 / 360 * 2 * np.pi, label="Small Angle")
small_angle_pendulum.attach_axis(view_ax=view_ax, phase_ax=phase_ax, time_ax=time_ax)
# medium_angle_pendulum = Pendulum("green", 0.5, 90 / 360 * 2 * np.pi, label="Medium Angle")
# medium_angle_pendulum.attach_axis(view_ax=view_ax, phase_ax=phase_ax, time_ax=time_ax)
high_swing_pendulum = Pendulum("k", 0.6, 179.9 / 360 * 2 * np.pi, label="Big Swing")
high_swing_pendulum.attach_axis(view_ax=view_ax, phase_ax=phase_ax, time_ax=time_ax)

pendulums = [
    small_angle_pendulum, 
    # medium_angle_pendulum, 
    high_swing_pendulum
]

def callback(label):
    the_p: None | Pendulum = None

    for p in pendulums:
        if p.label == label:
            the_p = p
            break

    if the_p is None:
        return

    the_p.angle_time_plot.set_visible(not the_p.angle_time_plot.get_visible())
    the_p.vel_time_plot.set_visible(not the_p.vel_time_plot.get_visible())

fsm_plot = None
scan = DBSCAN(eps=0.25, min_samples=50)

def main():
    global fsm_plot
    
    view_ax.set(xlim=[-1, 1], ylim=[-1, 1], xlabel='x-Auslenkung [m]', ylabel='y-Auslenkung [m]')
    view_ax.legend()

    phase_ax.set(xlim=[-5, 5], ylim=[-10, 10])
    phase_ax.set(xlabel=r'Auslenkungswinkel $\theta$ [rad]', ylabel=r"Winkelgeschwindigkeit $\omega$ [rad/s]")

    fsm_ax.set(xlim=[-5, 5], ylim=[-10, 10])
    fsm_ax.set(xlabel=r'Auslenkungswinkel $\theta$ [rad]', ylabel=r"Winkelgeschwindigkeit $\omega$ [rad/s]")

    view_ax.set_aspect('equal')
    # phase_ax.set_aspect('equal')

    time_ax.set(xlim=[0, 50], ylim=[-3*np.pi, 3*np.pi])

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

    # check.on_clicked(callback)

    fsm_plot = fsm_ax.scatter([], [], c="k", alpha=0.1, s=20)

    ani = animation.FuncAnimation(fig=fig, func=update, interval=1000/FPS, blit=True, frames=100_000)
    plt.show()


LABEL_COLORS = {
    -1: "gray",
    0: "green",
    1: "blue",
    2: "red",
    3: "yellow",
}

def update(frame):
    global last_t
    # global angle, angle2, angular_velocity, angular_velocity2, DATA_X, DATA_Y, DATA_X2, pendulum

    now = datetime.datetime.now()
    dt = (now - last_t).microseconds / 1_000_000
    print(dt)
    last_t = now
    pass

    for p in pendulums:
        p.step(1 / FPS)
        p.update()

    data = np.array([pendulums[-1].history_angle, pendulums[-1].history_angular_velocity]).T
    labels = scan.fit_predict(data)

    fsm_plot.set_offsets(data)
    fsm_plot.set_color([LABEL_COLORS[l] for l in labels])

    # return ((p.string, p.ball) for p in pendulums)
    # T.append(frame * 1/15)

    # DATA_X.append((angle))
    # DATA_Y.append((angular_velocity))

    # DATA_X2.append((angle2))
    # DATA_Y2.append((angular_velocity2))


    # # update the scatter plot:
    # data = np.stack([x, y]).T
    # scat.set_offsets(data)

    # data2 = np.stack([x2, y2]).T
    # scat2.set_offsets(data2)

    # scat_data.set_data(DATA_X, DATA_Y)
    # scat_data2.set_data(DATA_X2, DATA_Y2)

    # phase_ax.set(xlim=[-2*np.pi, +2*np.pi], ylim=[-15, 15], xlabel='Angle [rad]', ylabel='Ang. Velocity [rad/s]')

    # line.set_xdata([0.0, x])
    # line.set_ydata([0.0, y])

    # line2.set_xdata([0.0, x2])
    # line2.set_ydata([0.0, y2])

    # t_data1.set_xdata(T)
    # t_data1.set_ydata(DATA_X)

    # t_data2.set_xdata(T)
    # t_data2.set_ydata(DATA_X2)


    # return (scat, line2, t_data2)


    retval = [fsm_plot]

    for p in pendulums:
        retval += [p.string, p.ball, p.phase_points, p.angle_time_plot, p.vel_time_plot]


    return retval





if __name__ == "__main__":
    main()
