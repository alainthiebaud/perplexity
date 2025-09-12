import pandas as pd

EXCEL_PATH = "assets/frais_divers_annuels.xlsx"

def get_feuilles():
    """Retourne la liste des feuilles à traiter (hors 'frais divers')."""
    xls = pd.ExcelFile(EXCEL_PATH)
    return [f for f in xls.sheet_names if f.lower() != "frais divers"]

def lire_tous_les_frais():
    """Retourne un dict {feuille: dataframe} pour toutes les feuilles."""
    xls = pd.ExcelFile(EXCEL_PATH)
    result = {}
    for feuille in get_feuilles():
        df = pd.read_excel(EXCEL_PATH, sheet_name=feuille)
        result[feuille] = df
    return result

def afficher_tous_les_frais():
    """Affiche tous les frais de chaque feuille dans la console."""
    frais = lire_tous_les_frais()
    for feuille, df in frais.items():
        print(f"\n--- {feuille} ---")
        print(df)

def ajouter_frais(feuille, valeurs_dict):
    """Ajoute une ligne de frais dans la feuille donnée.
    valeurs_dict: dict des colonnes/valeurs, ex: {"Description": "...", "montant (CHF)": 100}
    """
    df = pd.read_excel(EXCEL_PATH, sheet_name=feuille)
    new_row = pd.DataFrame([valeurs_dict])
    df = pd.concat([df, new_row], ignore_index=True)
    with pd.ExcelWriter(EXCEL_PATH, engine="openpyxl", mode='a', if_sheet_exists='replace') as writer:
        df.to_excel(writer, sheet_name=feuille, index=False)

def modifier_frais(feuille, index_ligne, colonne, nouvelle_valeur):
    """Modifie une valeur existante dans une feuille."""
    df = pd.read_excel(EXCEL_PATH, sheet_name=feuille)
    df.at[index_ligne, colonne] = nouvelle_valeur
    with pd.ExcelWriter(EXCEL_PATH, engine="openpyxl", mode='a', if_sheet_exists='replace') as writer:
        df.to_excel(writer, sheet_name=feuille, index=False)