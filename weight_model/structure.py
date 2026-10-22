import numpy as np
import math
import matplotlib.pyplot as plt
import csv

##################
### Spar calcs ###
##################
# There are two methods here to calculate spar cap thickness:
# Method 1: Limit curvature
# Method 2: Limit tip deflection
# Both methods should be used for proper spar design
#
# Assumptions:
# Only the spar cap is taking bending load.
# The core between the spar caps takes all the load from the spar caps.
# Wing weight is averaged over the span.

# TODO get actual test data on how far the solar cells can bend without cracking

def Lprime(L,b,y):
    # Lift distribution
    # Using Schrenk's approximation as outlined in Desing of Aircraft by Corke ch. 10
    return (L/(2*b)) * (1 + (4/np.pi) * (1 - ((2*y)/b)**2)**0.5)

def spar_calc(p):
    # Inputs
    Ch = p['Ch']
    m_other = p['m_other']
    m_wing = p['m_wing']
    TC = p['TC']
    G_max = p['G_max']
    b = p['b']
    nu_max = p['nu_max']
    E_cap = p['E_cap']
    th_skin = p['th_skin']
    th_cap = p['th_cap']
    db = p['db']
    rho_cap = p['rho_cap']
    dtheta_max = p['dtheta_max']

    # Intermediate calcs
    N = 50 # number of stations
    y = np.linspace(0, b/2, N)
    dy = y[1] - y[0]

    L = (m_other + m_wing) * G_max * 9.81 # N; total lift
    h_spar = Ch * TC * 0.95 # m; spar height
    Ly = Lprime(L,b,y)
    q_mwing = -9.81 * G_max * m_wing / b

    # Initializing values
    V = np.zeros(N) # N; shear force
    M = np.zeros(N) # Nm; moment
    I1 = np.zeros(N) # m^4; second moment of area, method 1
    I2 = np.zeros(N) # m^4; second moment of area, method 2
    w1 = np.zeros(N) # m; spar cap width, method 1
    w2 = np.zeros(N) # m; spar cap width, method 2
    theta = np.zeros(N) # rad; slope
    nu = np.zeros(N) # m; deflection
    P = np.zeros(N) # psi; core compression
    sigma_cap = np.zeros(N) # Pa; stress in spar cap
    m_cap = 0 # kg; spar cap mass, not including epoxy

    # Getting values from the tip inwards
    for n in reversed(range(N-1)):
        V[n] = V[n+1] + (dy/2) * (Ly[n+1]+Ly[n]) + dy*q_mwing
        M[n] = M[n+1] + (dy/2) * (V[n+1]+V[n])
        I1[n] = abs(M[n]) / (E_cap * dtheta_max) # controlling for max slope difference
        w1[n] = (2 * I1[n]) / (th_cap * h_spar**2)

    # Method 2 "I" calcs
    def I_opt(n):
        # For Method 2 calcs
        I = var1 * (((b/2) - y[n]) * abs(M[n]))**(0.5) * var2
        return I

    var1 = 1 / (E_cap * nu_max)
    var2 = 0
    for n in range(N):
        var2 += dy * ( ((b/2) - y[n]) * abs(M[n]) )**0.5

    for n in range(N):
        I2[n] = I_opt(n)
        w2[n] = (2 * I2[n]) / (th_cap * h_spar**2)

    I = I2
    w = w2

    # Getting values from the root outwards
    for n in range(1,N):
        if I[n] != 0:
            theta[n] = theta[n-1] + (dy/2) * ((M[n] / (E_cap * I[n])) + (M[n-1] / (E_cap * I[n-1])))
        else:
            theta[n] = theta[n-1]
        nu[n] = nu[n-1] + (dy/2) * (theta[n]+theta[n-1])

    for n in range(N):
        if I[n] != 0:
            sigma_cap[n] = (M[n] * (h_spar/2)) / I[n]
            P[n] = 0.000145 * (V[n] / w2[n])
        else:
            sigma_cap[n] = 0
            P[n] = 0
        m_cap += 2 * 2 * th_cap * w[n] * rho_cap * dy

    # Outputting
    P_max = max(P)
    sigma_cap_max = max(sigma_cap)

    data = {
        'Ly': Ly,
        'q_mwing': np.full(N,q_mwing),
        'V': V,
        'M': M,
        'w1': w1,
        'w2': w2,
        'nu': nu,
        'm_cap': m_cap,
        'P_max': P_max,
        'sigma_cap_max': sigma_cap_max
    }
    return data

if __name__ == "__main__":
    with open('params.csv', newline='', mode='r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        p = {row['param']:float(row['value']) for row in reader}
    
    dat = spar_calc(p)

    N = 50 # number of stations
    y = np.linspace(0, p['b']/2, N)

    print(f"max nu: {max(dat['nu']):.4g} m")
    print(f"max core compression: {dat['P_max']:.4g} psi")
    print(f"max spar cap stress: {(dat['sigma_cap_max']/10**6):.4g} MPa")
    print(f"spar cap mass (not including epoxy): {dat['m_cap']:.4g} kg")

    fig1, ax1 = plt.subplots()

    ax1.plot(y, dat['Ly'], label="Ly (N)", color="blue", linestyle="-")
    ax1.plot(y, -dat['q_mwing'], label="-q_mwing (N)", color="black", linestyle="-")
    ax1.plot(y, dat['V'], label="V (N)", color="red", linestyle="-")
    ax1.plot(y, dat['M'], label="M (Nm)", color="green", linestyle="-")

    ax1.set_xlabel("y")
    ax1.set_ylabel("data")
    ax1.legend()
    ax1.grid(True)

    fig2, ax2 = plt.subplots()

    ax2.plot(y, dat['w1']*1000, label="w1 (mm)", color="brown", linestyle="-")
    ax2.plot(y, dat['w2']*1000, label="w2 (mm)", color="grey", linestyle="-")
    ax2.plot(y, dat['nu']*1000, label="nu (mm)", color="orange", linestyle="-")

    ax2.set_xlabel("y")
    ax2.set_ylabel("data")
    ax2.legend()
    ax2.grid(True)

    plt.show()