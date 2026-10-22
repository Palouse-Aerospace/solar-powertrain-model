import numpy as np
import matplotlib.pyplot as plt

from solar_model.functions import P_sol, P_level


def plot_design_space(
    L_values,
    m_bat_values,
    times,
    lat,
    h,
    normal,
    Ch,
    C_L,
    C_D,
    Eta_prop,
    Eta_mppt,
    m_rest,
    m_L,
    P_av,
    P_pld,
    e_bat,
    f_usable,
    reserve_fraction,
    dt_hours
):

    simulation_hours = (len(times) - 1) * dt_hours
    n_steps = len(times) - 1
    steps_per_day = int(round(24.0 / dt_hours))

    L_grid, M_grid = np.meshgrid(L_values, m_bat_values)

    excess_hours = np.zeros_like(L_grid, dtype=float)
    charge_margin_hours = np.zeros_like(L_grid, dtype=float)
    minimum_energy = np.zeros_like(L_grid, dtype=float)

    solar_profiles = {}

    for L in L_values:
        solar_profiles[L] = np.array([
            P_sol(L, lat, h, t, normal, Ch, Eta_mppt)
            for t in times
        ])

    for i, m_bat in enumerate(m_bat_values):
        E_max = m_bat * e_bat * f_usable
        E_min = reserve_fraction * E_max

        for j, L in enumerate(L_values):
            solar = solar_profiles[L]

            P_motor = P_level(
                L, m_bat, C_D, C_L, m_L, m_rest, h, Ch
            ) / Eta_prop

            P_load = P_motor + P_av + P_pld
            P_net = solar - P_load

            # Average daily time with solar surplus
            day_excess = []

            for day in range(int(simulation_hours // 24)):
                start = day * steps_per_day
                stop = min(start + steps_per_day, n_steps)

                day_excess.append(
                    np.count_nonzero(solar[start:stop] > P_load)
                    * dt_hours
                )

            excess_hours[i, j] = (
                np.mean(day_excess) if day_excess else 0.0
            )

            # Average daily net energy balance,
            # expressed in equivalent hours of electrical load
            daily_net_energy = []

            for day in range(int(simulation_hours // 24)):
                start = day * steps_per_day
                stop = min(start + steps_per_day, n_steps)

                daily_net_energy.append(
                    np.sum(P_net[start:stop]) * dt_hours
                )

            mean_daily_net = (
                np.mean(daily_net_energy)
                if daily_net_energy else np.nan
            )

            charge_margin_hours[i, j] = (
                mean_daily_net / P_load if P_load > 0 else np.nan
            )

            # Battery simulation
            energy = np.zeros(len(times))
            energy[0] = E_max

            for k in range(n_steps):
                E_next = energy[k] + P_net[k] * dt_hours
                energy[k + 1] = min(E_next, E_max)

            minimum_energy[i, j] = np.min(energy)


    reserve_ok = minimum_energy >= (
        M_grid * e_bat * f_usable * reserve_fraction
    )
    energy_ok = charge_margin_hours >= 0
    feasible = reserve_ok & energy_ok

    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(10, 9), sharex=True
    )

    contour1 = ax1.contourf(
        L_grid, M_grid, excess_hours,
        levels=20, cmap="YlOrRd"
    )
    fig.colorbar(
        contour1, ax=ax1,
        label="Excess solar time (h/day)"
    )

    contour2 = ax2.contourf(
        L_grid, M_grid, charge_margin_hours,
        levels=20, cmap="YlOrRd"
    )
    fig.colorbar(
        contour2, ax=ax2,
        label="Charging margin (equivalent h)"
    )

    if (
        np.nanmin(charge_margin_hours) <= 0
        and np.nanmax(charge_margin_hours) >= 0
    ):
        ax2.contour(
            L_grid, M_grid, charge_margin_hours,
            levels=[0], colors="blue", linewidths=2
        )

    for ax in (ax1, ax2):
        ax.contourf(
            L_grid, M_grid, (~feasible).astype(float),
            levels=[0.5, 1.5],
            colors="none", hatches=["////"]
        )
        ax.set_ylabel("Battery mass (kg)")

    ax1.set_title("Solar UAV Design Space")
    ax1.text(
        0.02, 0.03,
        "Hatched: infeasible under current criteria",
        transform=ax1.transAxes,
        fontsize=9,
        bbox=dict(facecolor="white", alpha=0.8)
    )

    ax2.set_xlabel("Wingspan (m)")

    plt.tight_layout()
    plt.show()

    return (
        L_grid,
        M_grid,
        excess_hours,
        charge_margin_hours,
        minimum_energy,
        feasible
    )