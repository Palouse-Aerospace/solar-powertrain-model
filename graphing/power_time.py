import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def plot_results(
    times,
    P_solar,
    P_motor,
    P_load,
    P_battery,
    E_battery,
    E_max,
    reserve_fraction
):

    # One figure with two vertical axes
    fig, ax1 = plt.subplots(figsize=(13, 6))

    ax1.plot(
        times, P_solar,
        color="blue", linewidth=1.5,
        label=r"$P_{\mathrm{solar}}$"
    )

    ax1.plot(
        times, np.full(len(times), P_load),
        color="green", linewidth=1.5,
        label=r"$P_{\mathrm{out}}$"
    )

    ax1.set_xlabel("Time")
    ax1.set_ylabel("Power (W)")
    ax1.set_ylim(bottom=0)
    ax1.grid(True, alpha=0.3)



    ax2 = ax1.twinx()

    ax2.plot(
        times, E_battery,
        color="red", linewidth=2.5,
        label=r"$E_{\mathrm{bat}}$"
    )

    ax2.axhline(
        E_max,
        color="red", linestyle=":",
        alpha=0.7,
        label=r"$E_{\mathrm{bat,max}}$"
    )

    ax2.axhline(
        reserve_fraction * E_max,
        color="red", linestyle="--",
        alpha=0.5,
        label="Minimum reserve"
    )

    ax2.set_ylabel("Battery energy (Wh)", color="red")
    ax2.tick_params(axis="y", labelcolor="red")
    ax2.set_ylim(bottom=0, top=E_max * 1.1)



    ax1.set_title("Solar UAV Power and Stored Battery Energy")

    ax1.xaxis.set_major_formatter(
        mdates.DateFormatter("%m-%d %H:%M")
    )

    fig.autofmt_xdate()

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()

    ax1.legend(
        lines1 + lines2,
        labels1 + labels2,
        loc="upper right"
    )

    fig.tight_layout()
    plt.show()


    print(f"Motor power draw: {P_motor:.2f} W")
    print(f"Total electrical load: {P_load:.2f} W")
    print(f"Peak solar power: {np.max(P_solar):.2f} W")
    print(f"Maximum battery capacity: {E_max:.1f} Wh")
    print(f"Minimum stored energy: {np.min(E_battery):.1f} Wh")
    print(f"Final stored energy: {E_battery[-1]:.1f} Wh")

    print(
        "Reserve maintained:",
        np.all(E_battery >= reserve_fraction * E_max)
    )