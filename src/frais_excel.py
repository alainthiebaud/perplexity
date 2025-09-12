import pandas as pd

EXCEL_PATH = "assets/frais_divers_annuels.xlsx"

def get_feuilles():
    """Retourne la liste des feuilles à traiter (hors 'frais divers')."""
    xls = pd.ExcelFile(EXCEL_PATH)
    return [f for f in xls.sheet_names if f.lower() != "frais divers"]

def lire_tous_les_frais():
    """Retourne un dict {feuille: dataframe} pour toutes les feuilles (hors 'frais divers')."""
    result = {}
    for feuille in get_feuilles():
        df = pd.read_excel(EXCEL_PATH, sheet_name=feuille)
        result[feuille] = df
    return result

def afficher_tous_les_frais():
    """Affiche tous les frais de chaque feuille dans la console (debug)."""
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

def regrouper_frais_vers_frais_divers():
    """Regroupe toutes les lignes des autres feuilles dans l'onglet 'frais divers'.

    - Efface/remplace complètement la feuille 'frais divers'.
    - Ajoute une colonne 'Feuille' indiquant la provenance.
    - Ne fait aucun regroupement/somme: chaque ligne originale est gardée telle quelle.
    """
    feuilles = get_feuilles()
    frames = []
    for feuille in feuilles:
        df = pd.read_excel(EXCEL_PATH, sheet_name=feuille)
        if df.empty:
            continue
        df = df.copy()
        df['Feuille'] = feuille
        frames.append(df)
    if not frames:
        # Si aucune donnée, on écrit une feuille vide avec les colonnes standards
        colonnes_min = ["Description", "montant (CHF)", "Feuille"]
        vide = pd.DataFrame(columns=colonnes_min)
        with pd.ExcelWriter(EXCEL_PATH, engine="openpyxl", mode='a', if_sheet_exists='replace') as writer:
            vide.to_excel(writer, sheet_name='frais divers', index=False)
        print("Aucune donnée à regrouper. Feuille 'frais divers' recréée vide.")
        return

    frais_divers = pd.concat(frames, ignore_index=True)

    # Ecriture dans la feuille 'frais divers'
    with pd.ExcelWriter(EXCEL_PATH, engine="openpyxl", mode='a', if_sheet_exists='replace') as writer:
        frais_divers.to_excel(writer, sheet_name='frais divers', index=False)

    print(f"{len(frais_divers)} lignes écrites dans la feuille 'frais divers'.")

def lire_frais_divers():
    """Lit la feuille 'frais divers' (après regroupement). Retourne un DataFrame ou None si erreur."""
    try:
        return pd.read_excel(EXCEL_PATH, sheet_name='frais divers')
    except Exception as e:
        print(f"Impossible de lire la feuille 'frais divers': {e}")
        return None

if __name__ == "__main__":
    # Exemple d'utilisation rapide
    regrouper_frais_vers_frais_divers()
    print(lire_frais_divers())