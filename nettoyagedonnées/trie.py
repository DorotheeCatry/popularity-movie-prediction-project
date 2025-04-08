import csv

# Nom du fichier d'entrée contenant les lignes invalides
input_file = "listfilmjpbox_invalid.csv"

# Dictionnaire qui va regrouper les lignes en fonction du nombre d'éléments
rows_by_count = {}

# Lecture du fichier invalid.csv
with open(input_file, "r", newline="", encoding="utf-8") as infile:
    reader = csv.reader(infile)
    for row in reader:
        count = len(row)
        # Ajouter la ligne dans le groupe correspondant
        rows_by_count.setdefault(count, []).append(row)

# Pour chaque groupe, écrire un fichier CSV distinct
for count, rows in rows_by_count.items():
    output_file = f"invalid_{count}.csv"
    with open(output_file, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.writer(outfile)
        writer.writerows(rows)
    print(f"Écriture de {len(rows)} lignes avec {count} éléments dans le fichier {output_file}")
