# 1. Simulation et nettoyage : AVEC ENTAILLE
python -m gprMax user_models/erablius_entaille/erablius_entaille.in -n 18
python -m tools.outputfiles_merge user_models/erablius_entaille/erablius_entaille --remove-files
Remove-Item -Path "user_models/erablius_entaille/*.vti" -Force
python -m gprMax user_models/erablius_entaille/erablius_entaille.in --geometry-only

# 2. Simulation et nettoyage : SANS ENTAILLE (SAIN)
python -m gprMax user_models/erablius_sain/erablius_sain.in -n 18
python -m tools.outputfiles_merge user_models/erablius_sain/erablius_sain --remove-files
Remove-Item -Path "user_models/erablius_sain/*.vti" -Force
python -m gprMax user_models/erablius_sain/erablius_sain.in --geometry-only

# 3. Affichage simultané avec échelle commune (CLIM = 2000)
# L'argument --clim 2000 force l'échelle de couleur entre -2000 et 2000 pour les deux fenêtres.
Start-Process python -ArgumentList "process_erablius.py user_models/erablius_entaille/erablius_entaille_merged.out --clim 2000"
Start-Process python -ArgumentList "process_erablius.py user_models/erablius_sain/erablius_sain_merged.out --clim 2000"