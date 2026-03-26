import h5py
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import spectrogram

def main():
    file_sain = r"oli\erablius_sain_simple.out"
    file_entaille = r"oli\erablius_entaille_simple_2cm.out"
    sweep_path = "4a8GHz_25ns_5.txt"

    # ==============================
    # 1. Lecture des fichiers
    # ==============================
    # Fonction locale rapide pour lire les traces
    def get_trace(filename):
        with h5py.File(filename, 'r') as f:
            rx = list(f['rxs'].keys())[0]
            fields = list(f['rxs'][rx].keys())
            field = 'Hz' if 'Hz' in fields else fields[0]
            tr = np.array(f['rxs'][rx][field])
            return tr[np.newaxis, :] if tr.ndim == 1 else tr

    trace_sain = get_trace(file_sain)
    trace_entaille = get_trace(file_entaille)

    txt_data = np.loadtxt(sweep_path, skiprows=1)
    y_txt = txt_data[:12484, 1]

    # ==============================
    # 2. Traitement et Affichage
    # ==============================
    num_traces = min(trace_sain.shape[0], trace_entaille.shape[0])

    for idx in range(num_traces):
        # Multiplication (on s'assure que les tailles correspondent)
        len_sig = min(len(trace_sain[idx]), len(y_txt))
        result_sain = trace_sain[idx][:len_sig] * y_txt[:len_sig]
        result_entaille = trace_entaille[idx][:len_sig] * y_txt[:len_sig]

        # Création des spectrogrammes
        _, _, Sxx_sain = spectrogram(result_sain, 9.99e10, nperseg=1024)
        _, _, Sxx_entaille = spectrogram(result_entaille, 9.99e10, nperseg=1024)

        # EXACTEMENT votre calcul mathématique pour le visuel
        img_sain = np.log(np.abs(Sxx_sain))
        img_entaille = np.log(np.abs(Sxx_entaille))
        
        # Soustraction pour voir la différence
        img_diff = img_entaille - img_sain

        # ==============================
        # 3. Graphiques (côte à côte)
        # ==============================
        fig, axs = plt.subplots(1, 3, figsize=(18, 5))
        
        # Graphique 1 : Sain
        axs[0].imshow(img_sain, aspect='auto', origin='lower')
        axs[0].set_title('Arbre Sain')

        # Graphique 2 : Entaille
        axs[1].imshow(img_entaille, aspect='auto', origin='lower')
        axs[1].set_title('Arbre avec Entaille (2cm)')

        # Graphique 3 : Différence
        # On utilise une palette de couleurs qui va du bleu au rouge pour bien voir les variations
        vmax = np.max(np.abs(img_diff)) * 0.8 # Ajustement léger pour mieux voir les contrastes
        im2 = axs[2].imshow(img_diff, aspect='auto', origin='lower', cmap='RdBu_r', vmin=-vmax, vmax=vmax)
        axs[2].set_title('Différence (Entaille - Sain)')
        
        # On ajoute juste la barre de couleur sur le dernier pour comprendre l'intensité de la différence
        fig.colorbar(im2, ax=axs[2])

        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    main()