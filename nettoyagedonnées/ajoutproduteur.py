import pandas as pd
import numpy as np

# Charger le fichier invalid_17.csv
df_17 = pd.read_csv('invalid_17.csv')

# Ajouter la colonne "Producteur" avec des valeurs "NaN"
df_17['Producteur'] = np.nan

# Sauvegarder les données normalisées dans un nouveau fichier CSV
df_17.to_csv('normalized_18.csv', index=False)

print("Les données ont été normalisées et enregistrées dans 'normalized_18.csv'.")
