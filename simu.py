"""Simulation thermique d'une pièce chauffée (sans Modbus)."""

T_ext = 20       # température extérieure (°C)
C = 2000         # capacité thermique (J/°C)
k = 0.5          # pertes thermiques (W/°C)
P_max = 1000     # puissance maximale du chauffage (W)
T_securite = 80  # seuil de sécurité (°C)

T = T_ext
chauffage_allume = True
securite_active = False

for t in range(200):
    if T >= T_securite:
        securite_active = True
        chauffage_allume = False

    P_eff = P_max if chauffage_allume and not securite_active else 0

    T += (P_eff - k * (T - T_ext)) / C

    print(f"t={t}s ; T={T:.2f}°C ; Chauffage={chauffage_allume} ; Sécurité={securite_active}")
