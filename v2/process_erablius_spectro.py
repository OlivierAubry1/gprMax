import h5py
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks,savgol_filter, spectrogram
import argparse
import os

def main():

    filename1 = "entaille_cylindre.out"

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
    y_txt = txt_data[:12484, 1]

    # ==============================
    # Traitement de toutes les traces
    # ==============================
    for idx, single_trace in enumerate(trace):
        # Multiplication
        result = single_trace * y_txt


        # création et affichage du spectrogram
        f, t, Sxx = spectrogram(result,9.99e10)
       
        plt.figure(figsize=(10, 4))
        plt.ylim(0,0.75e9)
        plt.pcolormesh(t, f, Sxx, shading='gouraud')
        plt.ylabel('Frequency [Hz]')
        plt.xlabel('Time [sec]')
        plt.show()



if __name__ == "__main__":
    main()
