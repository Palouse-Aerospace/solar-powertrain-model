import numpy as np
from datetime import timedelta, datetime
import csv

from solar_model.functions import P_sol, P_level, dE_bat_dt, battery_limits, simulate_battery
from graphing.power_time import plot_results
from graphing.battery_wingspan import plot_design_space

# Loading technical parameters
with open('params.csv', newline='', mode='r', encoding='utf-8-sig') as file:
    reader = csv.DictReader(file)
    p = {row['param']:float(row['value']) for row in reader}

# Aircraft and environmental parameters
# TODO put into csv

lat = 46.7   #latitude of flight(degrees)
h = 820      #altitude(M)
date_time = datetime(2027, 6, 11, 7, 0) #date, Y-M-D-H-M
normal = np.array([0,0,-1])   #North-East-Down normal vector

b_step= 0.1
m_bat_step = 0.1

# Simulation parameters
dt_hours = 1.0 / 5.0   #5-minute time steps
simulation_hours = 48  # wo days to examine repeatability
n_steps = int(simulation_hours / dt_hours)

n_steps = int(round(simulation_hours / dt_hours))

times = [
    date_time + timedelta(hours=k * dt_hours)
    for k in range(n_steps + 1)
]

# Index for comparing the same time on consecutive days
steps_per_day = int(round(24.0 / dt_hours))


b_values = np.round(
    np.arange(
        p['b_min'],
        p['b_max'] + b_step / 2,
        b_step
    ),
    3
)

battery_values = np.round(
    np.arange(
        p['m_bat_min'],
        p['m_bat_max'] + m_bat_step / 2,
        m_bat_step
    ),
    3
)

print("Precomputing solar power profiles...")

solar_profiles = {}

for b_test in b_values:
    solar_profiles[b_test] = np.array([
        P_sol(
            b_test, lat, h, t,
            normal, p['Ch'], p['Eta_mppt']
        )
        for t in times
    ])


print("Searching candidate designs...")

feasible_designs = []
all_designs = []

for b_test in b_values:
    solar_power = solar_profiles[b_test]

    for m_bat_test in battery_values:

        (
            energy,
            battery_power,
            load,
            motor_power,
            feasible
        ) = simulate_battery(
            b_test, m_bat_test, solar_power, p, h, times, n_steps, dt_hours, steps_per_day
        )

        E_min, E_max = battery_limits(m_bat_test, p)

        result = {
            "b": b_test,
            "m_bat": m_bat_test,
            "motor_power": motor_power,
            "load": load,
            "min_energy": float(energy.min()),
            "final_energy": float(energy[-1]),
            "day1_end_energy": float(
                energy[steps_per_day]
            ),
            "E_max": E_max,
            "E_min": E_min,
            "feasible": feasible,
        }

        all_designs.append(result)

        if feasible:
            feasible_designs.append(result)


if not feasible_designs:
    print("\nNo feasible design found within the search bounds.")

else:
    # minimum battery mass.
    best = min(
        feasible_designs,
        key=lambda d: (d["m_bat"], d["b"])
    )

    b = best["b"]
    m_bat = best["m_bat"]

    print("\n========== OPTIMAL DESIGN ==========")
    print(f"Wingspan:              {b:.2f} m")
    print(f"Battery mass:          {m_bat:.2f} kg")
    print(f"Battery capacity:      {best['E_max']:.1f} Wh")
    print(f"Minimum reserve:       {best['E_min']:.1f} Wh")
    print(f"Motor power:           {best['motor_power']:.2f} W")
    print(f"Total electrical load: {best['load']:.2f} W")
    print(f"Minimum energy:        {best['min_energy']:.1f} Wh")
    print(f"Energy after 24 h:     {best['day1_end_energy']:.1f} Wh")
    print(f"Energy after 48 h:     {best['final_energy']:.1f} Wh")
    print(f"Feasible designs:      {len(feasible_designs)}")
    print(f"Designs tested:        {len(all_designs)}")


    P_solar = solar_profiles[b]

    (
        E_battery,
        P_battery,
        P_load,
        P_motor,
        feasible
    ) = simulate_battery(b, m_bat, P_solar, p, h, times, n_steps, dt_hours, steps_per_day)

    plot_results(
        times=times,
        P_solar=P_solar,
        P_motor=P_motor,
        P_load=P_load,
        P_battery=P_battery,
        E_battery=E_battery,
        E_max=best["E_max"],
        reserve_fraction=p['reserve_fraction']
    )
