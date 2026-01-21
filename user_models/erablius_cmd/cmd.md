# Liste de commandes simulations
## Avec entaille

1. python -m gprMax user_models/erablius_entaille/erablius_entaille.in -n 18
1. python -m tools.outputfiles_merge user_models/erablius_entaille/erablius_entaille --remove-files
1. Remove-Item -Path "user_models/erablius_entaille/*.vti" -Force
1. python -m gprMax user_models/erablius_entaille/erablius_entaille.in --geometry-only
1. python process_erablius.py user_models/erablius_entaille/erablius_entaille_merged.out

## Sans entaille
1. python -m gprMax user_models/erablius_sain/erablius_sain.in -n 18
1. python -m tools.outputfiles_merge user_models/erablius_sain/erablius_sain --remove-files
1. Remove-Item -Path "user_models/erablius_sain/*.vti" -Force
1. python -m gprMax user_models/erablius_sain.in --geometry-only
1. python process_erablius.py user_models/erablius_sain/erablius_sain_merged.out
