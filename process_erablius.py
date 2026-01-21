import h5py
import numpy as np
import matplotlib.pyplot as plt
import argparse
import os

def main():
    # 1. Configuration des arguments
    parser = argparse.ArgumentParser(description='Traitement et visualisation de B-Scan gprMax.')
    parser.add_argument('filename', help='Chemin vers le fichier .out fusionné')
    # Nouvel argument optionnel pour fixer l'échelle
    parser.add_argument('--clim', type=float, default=None, help='Valeur max absolue pour l\'échelle de couleur (ex: 2000)')
    
    args = parser.parse_args()
    filename = args.filename

    if not os.path.exists(filename):
        print(f"Erreur : Le fichier '{filename}' est introuvable.")
        return

    try:
        with h5py.File(filename, 'r') as f:
            rx_list = list(f['rxs'].keys())
            if not rx_list:
                print("Erreur : Aucun récepteur trouvé.")
                return
                
            first_rx = rx_list[0]
            available_fields = list(f['rxs'][first_rx].keys())
            field = 'Ez' if 'Ez' in available_fields else available_fields[0]
            
            print(f"Traitement : {filename} | Rx: {first_rx} | Champ: {field}")
            data = np.array(f['rxs'][first_rx][field])

        # --- TRAITEMENT ---
        # 1. Background Subtraction
        data_no_bg = data - np.mean(data, axis=1, keepdims=True)

        # 2. Gain temporel
        t_points = data.shape[0]
        t = np.linspace(0, t_points, t_points)
        gain_factor = 0.005 
        gain = np.exp(t * gain_factor)
        data_gained = data_no_bg * gain[:, np.newaxis]

        # --- GESTION DE L'ÉCHELLE (CLIM) ---
        # Si --clim est fourni, on l'utilise. Sinon, on calcule le max absolu du fichier.
        if args.clim:
            abs_max = args.clim
        else:
            abs_max = np.max(np.abs(data_gained))
        
        # On force une échelle symétrique (-max à +max) pour que 0 soit blanc (cmap seismic)
        v_min, v_max = -abs_max, abs_max

        # --- AFFICHAGE ---
        plt.figure(figsize=(12, 7))
        num_scans = data.shape[1]
        
        # Ajout des arguments vmin et vmax
        plt.imshow(data_gained, aspect='auto', cmap='seismic', 
                   extent=[0, num_scans, 18, 0],
                   vmin=v_min, vmax=v_max)
        
        plt.colorbar(label='Amplitude du champ (Gain appliqué)')
        plt.title(f'B-Scan : {os.path.basename(filename)}\nÉchelle : [{-abs_max:.0f}, {abs_max:.0f}]')
        plt.xlabel('Mesures (Traces)')
        plt.ylabel('Temps (ns)')
        plt.show()

    except Exception as e:
        print(f"Une erreur est survenue : {e}")

if __name__ == "__main__":
    main()