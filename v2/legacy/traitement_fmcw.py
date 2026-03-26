import h5py
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks, butter, filtfilt
import argparse
import os

def lowpass_filter(data, cutoff, fs, order=5):
    """
    Applique un filtre passe-bas numérique de type Butterworth.
    - data : le signal à filtrer
    - cutoff : la fréquence de coupure (en Hz)
    - fs : la fréquence d'échantillonnage (en Hz)
    - order : l'ordre du filtre (plus il est élevé, plus la coupure est raide)
    """
    nyq = 0.5 * fs  # Fréquence de Nyquist
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    y = filtfilt(b, a, data) # filtfilt évite le déphasage du signal
    return y

def process_and_get_fft(filename, y_txt, B, Tc, cst_diele):
    """
    Lit un fichier .out, effectue le mélange, applique un filtre passe-bas,
    calcule la FFT et détecte les distances.
    """
    if not os.path.exists(filename):
        print(f"Erreur : Le fichier '{filename}' est introuvable.")
        return None, None

    with h5py.File(filename, 'r') as f:
        rx_list = list(f['rxs'].keys())
        first_rx = rx_list[0]
        available_fields = list(f['rxs'][first_rx].keys())
        field = 'Hz' if 'Hz' in available_fields else available_fields[0]

        trace = np.array(f['rxs'][first_rx][field])
        if trace.ndim == 1:
            trace = trace[np.newaxis, :]

        dt_trace = f.attrs.get('dt', 1.0)
    
    single_trace = trace[0]
    N_trace = len(single_trace)
    
    # 1. INTERPOLATION
    y_interp = np.interp(np.linspace(0, len(y_txt) - 1, N_trace),
                         np.arange(len(y_txt)),
                         y_txt)

    # 2. MULTIPLICATION (Mélange / Mixing)
    result_brut = single_trace * y_interp

    # 3. FILTRAGE PASSE-BAS
    fs = 1.0 / dt_trace  # Fréquence d'échantillonnage du signal gprMax
    cutoff_freq = 2e9    # Fréquence de coupure à 2 GHz (2 milliards de Hz)
    
    result_filtre = lowpass_filter(result_brut, cutoff_freq, fs)

    # 4. FFT (Analyse Spectrale sur le signal filtré)
    hanning = np.hanning(N_trace)
    fft_values = np.fft.fft(result_filtre * hanning)
    freqs = np.fft.fftfreq(N_trace, dt_trace)
    
    positive_freqs = freqs[:N_trace//2]
    positive_fft = np.abs(fft_values[:N_trace//2])

    # 5. DÉTECTION DES PICS
    c = 3e8
    # On abaisse un peu le seuil à 5% car le filtre a lissé le signal global
    peaks, _ = find_peaks(positive_fft, height=np.max(positive_fft) * 0.05)
    fb_list = positive_freqs[peaks]

    print(f"\n--- Analyse de {filename} ---")
    if len(fb_list) == 0:
        print("Aucun pic significatif détecté.")
    else:
        for i, fb in enumerate(fb_list):
            R = (fb * c * Tc) / (2 * B * np.sqrt(cst_diele))
            print(f"Pic {i+1}: Fréquence fb = {fb:.2e} Hz --> Distance = {R:.3f} m")

    return positive_freqs, positive_fft

def main():
    parser = argparse.ArgumentParser(description='Post-traitement radar FMCW gprMax')
    parser.add_argument('--file1', type=str, default='legacy\EECYL_x06_antenne.out', help='Fichier de référence')
    parser.add_argument('--file2', type=str, default='legacy\ESCYL_x06_antenne.out', help='Fichier avec cible')
    parser.add_argument('--sweep', type=str, default='4a8GHz_25ns_5.txt', help='Fichier TXT du chirp')
    args = parser.parse_args()

    B = 4e9            
    Tc = 2.5e-8        
    cst_diele = 6      

    if not os.path.exists(args.sweep):
        print(f"Erreur : Le fichier chirp '{args.sweep}' est introuvable.")
        return

    txt_data = np.loadtxt(args.sweep, skiprows=1)
    y_txt = txt_data[:, 1] 

    plt.figure(figsize=(10, 5))

    freqs1, fft1 = process_and_get_fft(args.file1, y_txt, B, Tc, cst_diele)
    if freqs1 is not None:
        plt.plot(freqs1, fft1, label=args.file1, color='blue')

    freqs2, fft2 = process_and_get_fft(args.file2, y_txt, B, Tc, cst_diele)
    if freqs2 is not None:
        plt.plot(freqs2, fft2, label=args.file2, color='orange', linestyle='--')

    plt.xlabel("Fréquence de battement (Hz)")
    plt.ylabel("Amplitude")
    plt.title("Spectres de battement FMCW (Filtré)")
    
    # On limite l'axe X à 2 GHz puisque tout ce qui est au-dessus a été coupé
    plt.xlim(0, 2e9) 
    
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()