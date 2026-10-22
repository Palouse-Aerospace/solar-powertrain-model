import csv
import math
from weight_model.structure import spar_calc

### Inputs ###
with open('params.csv', newline='', mode='r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        p = {row['param']:float(row['value']) for row in reader}

rhoA_14g = 0.0475 # kg/m^2; 1.4oz/yd^2 fiberglass areal density
rhoA_07g = 0.02375 # kg/m^2; 0.7oz/yd^2 fiberglass areal density
rho_foam = 22.5 # kg/m^3; 25psi foam board density. https://www.homedepot.com/p/Owens-Corning-FOAMULAR-NGX-F-250-2-in-x-4-ft-x-8-ft-SSE-R-10-XPS-Rigid-Foam-Board-Insulation-52DDNGX/315197962

m_sc = 0.008 # kg; mass of a Sunpower C60 cell https://www.mdpi.com/2504-446x/5/2/44 TODO verify
m_dogbone = 0.001 # kg; mass of dogbone conncetor TODO verify
m_bat = 0.047 # kg; 18650 battery mass per cell

w_sc = 0.125 # m; Sunpower C60 solar cell width

efrac_fg = 0.5 # fiberglass/epoxy mass fraction
efrac_cf = 0.6 # carbon fiber/epoxy mass fraction
efrac_sc = 0.95 # solar cell/epoxy mass fraction

### Wing ###
def mass_wing(p, b=None, N_bat=None):
    ### Wing mass estimation ###
    # This assumes a similar construction to the V1 plane wing

    if b is None:  #This is so it can be used in the optimization code
         b = p['b']
    if N_bat is None:  #This is also just for the optimization
         N_bat = p['N_bat']

    # Inputs
    Ch = p['Ch']

    afoil_th_ratio = p['afoil_th_ratio']
    afoil_area_ratio = p['afoil_area_ratio']
    
    Ch_sc = p['Ch_sc']
    frac_sc = p['Ch_sc']

    m_elec_w = p['m_elec_w']

    bat_cutout = p['bat_cutout']


    # Calcs
    N_sc = math.floor((b / w_sc)*frac_sc) * Ch_sc
    m_sol = (N_sc*m_sc)/efrac_sc + N_sc*m_dogbone # Total solar system mass

    m_skin = Ch*b*afoil_area_ratio * (rhoA_14g/efrac_fg) # Outer layer skin mass
    m_sc_skin = w_sc*1.1 * b * (rhoA_14g/efrac_fg) # Under cell fiberglass mass

    spar_dat = spar_calc(p)
    m_cap = spar_dat['m_cap'] / efrac_cf

    V_core = Ch * (afoil_th_ratio*Ch) * b # m^3
    if bat_cutout == True:
         V_core += -1.1 * b * ((math.pi/4) * 0.018**2) # 1.1 since there needs to be space for wires
    m_core = V_core * rho_foam

    m_bats = N_bat * m_bat

    m_wing = 1.05*(m_sol + m_skin + m_sc_skin + m_cap + m_core + m_elec_w + m_bats)

    if p['debug'] == 1:
        print("--- DEBUG WING MASS INFO ---")
        print(f"m_sol:     {m_sol:.4f} kg")
        print(f"m_skin:    {m_skin:.4f} kg")
        print(f"m_sc_skin: {m_sc_skin:.4f} kg")
        print(f"m_cap:     {m_cap:.4f} kg")
        print(f"m_core:    {m_core:.4f} kg")
        print(f"m_elec_w:  {m_elec_w:.4f} kg")
        print(f"m_bats:    {m_bats:.4f} kg")
        print(f"m_wing:    {m_wing:.4f} kg")
        print()

    return m_wing

def mass_fuse(p, b):
    ### Fuselage mass estimation ###
    # this is stupid baka garbage
    # somewhat based on Noth except we're not including the wing so it's weird
    # ^I reduced the exponent for that reason

    #The f*** is this? Im so confused

    # Inputs
    if b is None:  #This is so it can be used in the optimization code
             b = p['b']

    Ch = p['Ch']

    A = 0.156 # matched to the other parameters given data from Solar Plane V1 
    B = -0.2 # Noth says -0.25 for the whole airframe. this is pure vibes
    C = 1.5 # Noth says 3.1 for the whole airframe. this is pure vibes
    
    m_fuse = A * (b/Ch)**B * b**C

    if p['debug'] == 1:
        print("--- DEBUG FUSE MASS INFO ---")
        print(f"m_fuse: {m_fuse:.4f} kg")
        print()

    return m_fuse

def mass_tot(p):
    ### Total plane mass estimation ###
    # Combines the wing mass and the fuselage mass
    # Note that wing mass includes battery mass

    m_wing = mass_wing(p)
    m_fuse = mass_fuse(p)

    m_tot = m_wing + m_fuse

    return m_tot

if __name__ == "__main__":
    with open('params.csv', newline='', mode='r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        p = {row['param']:float(row['value']) for row in reader}

    m_tot = mass_tot(p)
    print(f"m_tot = {m_tot:.4g} kg")