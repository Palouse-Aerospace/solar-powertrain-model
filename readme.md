# Solar Plane V2 Power Train 

A python based simulation and optimization tool for evaluating the power train of a fixed wing aircraft. This models simulates solar generationg, power consumtion, and battery charging/discharging over time using *AtlantikSolar's* calculations. 

Developed as a part of the 2nd version of the Solar Plane from **Palouse Aerospace**

## Overview 

For an aircraft to achieve indefinete flight, it must be able to generate enough solar energy to fully recharge the battery during the day while powering the rest of the system. Then the battery must be able to fully support the flight during the night with a margin by morning. 

This project simulates the battery as a function of time, and optimizes battery mass and wing span provided our given parameters in [`params.csv`](./params.csv). 

## Key Features

- **Solar Power Modeling:** Based on the nominal solar output calculation from [*Oettershagen et al., 2017*](https://arxiv.org/pdf/1703.07385).

  $$
  P_{\mathrm{sol}}^{\mathrm{nom}} =
  I_{\mathrm{solar}}(\varphi_{\mathrm{lat}}, h, \delta, t, \vec{n}_{\mathrm{sm}})
  \cdot A_{\mathrm{sm}}
  \cdot \eta_{\mathrm{sm}}
  \cdot \eta_{\mathrm{mppt}}
  $$

- **Aircraft Power Consumption:** Based on the level-flight power calculation from [*Oettershagen et al., 2015*](https://www.atlantiksolar.ethz.ch/wp-content/downloads/publications/AtlantikSolar_ICRA_2015_vFinal.pdf).

  $$
  P_{\mathrm{level}} =
  \left(\frac{C_D}{C_L^{3/2}}\right)_{\min}
  \sqrt{\frac{2(m_{\mathrm{tot}}g)^3}{\rho(h)A_{\mathrm{wing}}}}
  $$

  $$
  P_{\mathrm{out}}^{\mathrm{nom}} =
  \frac{P_{\mathrm{level}}}{\eta_{\mathrm{prop}}}
  + P_{\mathrm{av}} + P_{\mathrm{pld}}
  $$

- **Battery Simulation:** Based on the battery state equation from [*Oettershagen et al., 2015*](https://www.atlantiksolar.ethz.ch/wp-content/downloads/publications/AtlantikSolar_ICRA_2015_vFinal.pdf).

  $$
  \frac{dE_{\mathrm{bat}}}{dt} =
  P_{\mathrm{solar}}(\varphi, h, t)
  - P_{\mathrm{prop}}
  - P_{\mathrm{av}}
  - P_{\mathrm{pld}}
  $$

- **Optimization:** Uses grid-based optimization to find the minimum battery mass and optimal wing length for solar energy generation.

- **Performance Visualization:** Uses Matplotlib to generate energy-over-time graphs and visualize powertrain performance.

- **Mass Modeling:** Estimates aircraft mass and structural weight using previously collected data from the V1 aircraft.
s

## Getting Started
### Requirements

Install Python and required packages:
```pip install numpy matplotlib solarpy```

### Configuration

Adjust aircraft and power train parameters in [`params.csv`](./params.csv). The simulation parameters can be edited within [`optimizations.py`](./optimization.py). 

### Running The Model

Run the model from [`optimizations.py`](./optimization.py) using 
```python optimizations.py```