import math
import numpy as np

from solarpy import irradiance_on_plane
from datetime import datetime
from weight_model.weight import mass_wing, mass_fuse


Eta_stc_sm = 0.237   #(Y)Standard Testing Condition solar conversion efficency, need to look at data sheet
Ep_I_sm = 1.0        #(Y)Iradiance efficency, again data sheet, need to model
Ep_T_sm = 1.0        #(Y)Temperature efficency, need to model
Ep_cbr_sm = 0.97     #Wing Chamber Efficency, V1 results


def P_sol(b, lat, h, date_time, normal, Ch, Eta_mppt):

    irradiance = irradiance_on_plane(
         normal, h, date_time, lat
    )

    panel_area = Ch * b * 0.85  # 85% of wing area covered by solar cells

    return irradiance * panel_area * Eta_sm() * Eta_mppt


def P_level(b, m_bat, p, h):    

    total_mass = mass_wing(p, b) + m_bat + mass_fuse(p, b)
    wing_area = p['Ch'] * b

    return (
        p['C_D'] / (p['C_L'] ** (3 / 2))
        * (
           2 * (total_mass * 9.81) ** 3
            / (rho(h) * wing_area)
            * 2
        ) ** (1 / 2)
    )


def Eta_sm():

    return (
        Eta_stc_sm
        * Ep_I_sm
        * Ep_T_sm
        * Ep_cbr_sm
    )


def rho(h):

    P0 = 101325.0       # Sea-level pressure (Pa)
    T0 = 288.15         # Sea-level temperature (K)
    lapse_rate = 0.0065  # Temperature lapse rate (K/m)
    R = 287.05          # Specific gas constant for dry air (J/(kg·K))
    g = 9.81            # Gravitational acceleration (m/s²)

    T = T0 - lapse_rate * h
    exponent = g / (lapse_rate * R)
    P = P0 * (1 - (lapse_rate * h / T0)) ** exponent
    air_density = P / (R * T)

    return air_density



def dE_bat_dt(b, Ch, lat, h, date_time, normal, Eta_mppt,
              C_D, C_L, m_L, m_rest, m_bat, Eta_prop, P_av, P_pld):
    solar_power = P_sol(
        b, lat, h, date_time, normal, Ch, Eta_mppt
    )

    propulsion_power = P_level(
        b, m_bat, C_D, C_L, m_L, m_rest, h, Ch
    ) / Eta_prop

    total_load = propulsion_power + P_av + P_pld

    return solar_power - total_load


def battery_limits(m_bat, p):
    E_max = m_bat * p['e_bat'] * p['f_usable']
    E_min = p['reserve_fraction'] * E_max
    return E_min, E_max



def simulate_battery(b, m_bat, solar_power, p, h, times, n_steps, dt_hours, steps_per_day):

    E_min, E_max = battery_limits(m_bat, p)

    motor_power = P_level(
        b, m_bat, p, h
    ) / p['Eta_prop']

    load = motor_power + p['P_av'] + p['P_pld']

    # Positive = charging; negative = discharging
    battery_power = solar_power - load

    energy = np.zeros(len(times))
    energy[0] = E_max

    for k in range(n_steps):
        E_next = (
            energy[k] + battery_power[k] * dt_hours
        )
        energy[k + 1] = min(E_next, E_max)

    # Must maintain the required reserve at every timestep
    reserve_ok = np.all(energy >= E_min)

    # Compare energy at the same clock time on days 1 and 2
    repeatability_ok = (
        energy[-1] >= energy[-1 - steps_per_day]
    )

    feasible = reserve_ok and repeatability_ok

    return (
        energy,
        battery_power,
        load,
        motor_power,
        feasible
    )
