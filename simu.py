T_ext = 20       # Température extérieure
C = 2000         # Capacité thermique (exemple)
k = 0.5          # Pertes thermiques
P_max = 1000     # Puissance max du chauffage (W)
T_securite = 80  # Seuil de sécurité (°C)

# État initial
T = T_ext
chauffage_allume = True
securite_active = False

for t in range(200):  # Simulation sur 1h
    # 1. Gestion du bouton de sécurité
    if T >= T_securite:
        securite_active = True
        chauffage_allume = False
    
    # 2. Calcul de la puissance effective
    if chauffage_allume and not securite_active:
        P_eff = P_max
    else:
        P_eff = 0

    # 3. Mise à jour de la température
    T += (P_eff - k*(T - T_ext)) / C
    
    # 4. Enregistrement des données
    print(f"t={t}s ; T={T:.2f}°C ; Chauffage={chauffage_allume} ; Sécurité={securite_active}")