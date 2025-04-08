
import pandas as pd

# Charger le premier CSV en interprétant "-" comme valeur manquante
df1 = pd.read_csv("listfilmjpbox.csv", na_values="-")

# Charger le deuxième CSV
df2 = pd.read_csv("demarage.csv")

# Extraire uniquement les colonnes utiles pour la fusion : 'Titre' et 'Demarage'
df2_subset = df2[['Titre', 'Demarage']]

# Fusionner les deux DataFrames sur la colonne "Titre" (jointure à gauche pour conserver toutes les lignes de df1)
merged = pd.merge(df1, df2_subset, on="Titre", how="left", suffixes=("", "_csv2"))

# Remplir les valeurs manquantes de la colonne "Entrées 1ère semaine" en utilisant la colonne "Demarage"
merged['Entrées 1ère semaine'] = merged['Entrées 1ère semaine'].fillna(merged['Demarage'])

# Supprimer la colonne additionnelle issue de la fusion si elle n'est plus nécessaire
merged.drop(columns=["Demarage"], inplace=True)

# Sauvegarder le DataFrame complété dans un nouveau fichier CSV
merged.to_csv("JPfilm.csv", index=False)

print("La complétion des valeurs manquantes est terminée et le fichier 'JPfilm.csv' a été créé.")
