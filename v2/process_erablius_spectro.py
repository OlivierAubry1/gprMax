import h5py
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import spectrogram
import argparse
import os

def main():
    filename1 = "legacy\ESRECT_x06_antenne.out"
    sweep_path = "4a8GHz_25ns_5.txt"

    # ==============================
    # Lecture fichier1 .out
    # ==============================
    with h5py.File(filename1, 'r') as f:
        print(f)
        rx_list = list(f['rxs'].keys())
        if not rx_list:
            print("Erreur : Aucun récepteur trouvé.")
            return

        first_rx = rx_list[0]
        available_fields = list(f['rxs'][first_rx].keys())
        field = 'Hz' if 'Hz' in available_fields else available_fields[0]

        print(f"\nFichier chargé : {filename1}")
        print(f"Récepteur : {first_rx} | Champ : {field}")

        trace = np.array(f['rxs'][first_rx][field])
        # Si trace 1D, la mettre en 2D pour uniformité
        if trace.ndim == 1:
            trace = trace[np.newaxis, :]

        dt_trace = f.attrs.get('dt', 1.0)
        t_trace = np.arange(trace.shape[1]) * dt_trace
        print(f"Nombre de traces : {trace.shape[0]}, longueur d'une trace : {trace.shape[1]}")
        print(f"Pas de temps dt = {dt_trace:.3e} s")
    
    print("Durée trace gprMax :", t_trace[-1], "s")

    # ==============================
    # Lecture fichier TXT
    # ==============================
    txt_data = np.loadtxt(sweep_path, skiprows=1)
    if txt_data.shape[1] != 2:
        raise ValueError("Le fichier TXT doit contenir exactement deux colonnes.")
    
    # On prend toute la colonne de données sans la couper
    y_txt = txt_data[:, 1]

    # Calcul de la fréquence d'échantillonnage exacte pour le spectrogramme
    fs = 1.0 / dt_trace

    # ==============================
    # Traitement de toutes les traces
    # ==============================
    for idx, single_trace in enumerate(trace):
        
        # Interpolation : On étire/compresse y_txt pour qu'il ait EXACTEMENT la taille de single_trace
        y_interp = np.interp(np.linspace(0, len(y_txt) - 1, len(single_trace)),
                             np.arange(len(y_txt)),
                             y_txt)

        # Multiplication (Mélange FMCW)
        result = single_trace * y_interp

        # Création et affichage du spectrogramme
        # On utilise 'fs' dynamique au lieu d'une valeur hardcodée
        f_spec, t_spec, Sxx = spectrogram(result, fs)
       
        plt.figure(figsize=(10, 4))
        plt.pcolormesh(t_spec, f_spec, Sxx, shading='gouraud')
        
        # Limite de l'axe Y (Fréquence) - Ajusté à 0.75 GHz comme tu l'avais demandé
        plt.ylim(0, 0.75e9) 
        
        plt.ylabel('Fréquence de battement [Hz]')
        plt.xlabel('Temps [sec]')
        plt.title(f"Spectrogramme FMCW - Trace {idx+1}")
        
        # Ajout d'une barre de couleur pour lire l'intensité
        plt.colorbar(label='Intensité')
        
        plt.show()

if __name__ == "__main__":
    main()