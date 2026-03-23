import h5py
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks,savgol_filter, spectrogram
import argparse
import os

def main():

    filename1 = "EERECT_x06_antenne.out"
    filename2 = "EECYL_x06_antenne.out"

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
    # Paramètres FMCW
    # ==============================
    c = 3e8            # vitesse lumière
    B = 4e9            # bande passante réelle du chirp (à ajuster selon ton modèle)
    Tc =  2.5e-8 #dt_trace * len(y_interp)  # durée réelle du chirp (issue du TXT ou du modèle gprMax)
    cst_diele = 6      # constante diélectrique (1 pour air)

    # ==============================
    # FFT du premier fichier
    # ==============================
    for idx, single_trace in enumerate(trace):
        # Multiplication
        result = single_trace * y_txt

        # FFT pour trouver la fréquence du pic (FMCW)
        N = len(result)
        hanning = np.hanning(N)
        fft_values = np.fft.fft(result*hanning)
        freqs = np.fft.fftfreq(N, dt_trace)
        positive_freqs = freqs[:N//2]
        positive_fft = np.abs(fft_values[:N//2])
        
        plt.figure()
        plt.plot(positive_freqs, positive_fft, label=filename1)
        plt.xlabel("Fréquence (Hz)")
        plt.ylabel("Amplitude")
        plt.title(f"FFT - Trace {idx+1}")
        plt.grid(True)
        #plt.show()
                
        fb_voulu = 2*0.2*B*np.sqrt(cst_diele)/(c*Tc)
        print(fb_voulu)

        # Détection des pics principaux
        #peaks, _ = find_peaks(positive_fft, height=np.max(positive_fft)*0.01)
        #fb_list = positive_freqs[peaks]
        
        # Il y a un facteur de 10 dans le temps du signal ( Tw = 1.4e-7 vs sweep_time = 1.43e-6)

        #print(f"\n--- Trace {idx+1} ---")
        #if len(fb_list) == 0:
        #    print("Aucun pic détecté")
        #for i, fb in enumerate(fb_list):
        #    # Formule FMCW correcte pour la distance
        #    R = (fb * c * Tc) / (2 * B * np.sqrt(cst_diele))
        #    print(f"Pic {i+1}: fb = {fb:.3e} Hz → Distance = {R:.3f} m")


            

# ==============================
    # Lecture fichier2 .out
    # ==============================
    with h5py.File(filename2, 'r') as f:
        print(f)
        rx_list = list(f['rxs'].keys())
        if not rx_list:
            print("Erreur : Aucun récepteur trouvé.")
            return

        first_rx = rx_list[0]
        available_fields = list(f['rxs'][first_rx].keys())
        field = 'Hz' if 'Hz' in available_fields else available_fields[0]

        print(f"\nFichier chargé : {filename2}")
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

    for idx, single_trace in enumerate(trace):
        # Multiplication
        result = single_trace * y_txt


# FFT du deuxième fichier
        N = len(result)
        hanning = np.hanning(N)
        fft_values = np.fft.fft(result*hanning)
        freqs = np.fft.fftfreq(N, dt_trace)
        positive_freqs = freqs[:N//2]
        positive_fft = np.abs(fft_values[:N//2])

        #plt.figure(figsize=(10, 4))
        plt.plot(positive_freqs, positive_fft, label=filename2)
        #plt.xlabel("Fréquence (Hz)")
        #plt.ylabel("Amplitude")
        #plt.title(f"FFT - Trace {idx+1}")
        #plt.grid(True)
        plt.legend()
        plt.show()



if __name__ == "__main__":
    main()
