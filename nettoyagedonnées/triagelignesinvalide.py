import pandas as pd
import csv

# Spécifie le fichier CSV original
input_csv = "listfilmjpbox.csv"

# Spécifie le fichier pour les lignes valides et pour les lignes invalides
valid_csv = "listfilmjpbox_valid.csv"
invalid_csv = "listfilmjpbox_invalid.csv"

# Nombre attendu de colonnes (remplace 18 par le nombre attendu pour ton fichier)
expected_columns = 18

# Ouvre le fichier CSV en lecture
with open(input_csv, "r", encoding="utf-8") as infile:
    reader = csv.reader(infile)

    # Prépare les fichiers de sortie
    with open(valid_csv, "w", newline="", encoding="utf-8") as valid_outfile, \
         open(invalid_csv, "w", newline="", encoding="utf-8") as invalid_outfile:
        valid_writer = csv.writer(valid_outfile)
        invalid_writer = csv.writer(invalid_outfile)
        
        # Itérer sur chaque ligne du CSV
        for idx, row in enumerate(reader):
            if len(row) == expected_columns:
                valid_writer.writerow(row)  # Écrit les lignes valides dans un fichier
            else:
                invalid_writer.writerow(row)  # Écrit les lignes invalides dans un autre fichier

print(f"Traitement terminé. Lignes valides : {valid_csv}. Lignes invalides : {invalid_csv}.")
