import pandas as pd

EXCEL_PATH = "assets/frais_divers_annuels.xlsx"

def get_feuilles(excel_path: str | None = None):
    """Retourne toutes les feuilles à traiter sauf 'frais divers' (insensible à la casse et espaces)."""
    path = excel_path or EXCEL_PATH
    try:
        xls = pd.ExcelFile(path)
        return [f for f in xls.sheet_names if f.strip().lower() != "frais divers"]
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier {path}: {e}")
        return []

def lire_tous_les_frais(excel_path: str | None = None):
    """Retourne un dict {feuille: dataframe} pour toutes les feuilles (hors 'frais divers')."""
    path = excel_path or EXCEL_PATH
    result = {}
    for feuille in get_feuilles(excel_path):
        try:
            df = pd.read_excel(path, sheet_name=feuille)
            result[feuille] = df
        except Exception as e:
            print(f"Erreur lors de la lecture de la feuille '{feuille}': {e}")
            result[feuille] = pd.DataFrame()
    return result

def afficher_tous_les_frais(excel_path: str | None = None):
    """Affiche tous les frais de chaque feuille dans la console (debug)."""
    frais = lire_tous_les_frais(excel_path)
    for feuille, df in frais.items():
        print(f"\n--- {feuille} ---")
        print(df)

def ajouter_frais(feuille, valeurs_dict, excel_path: str | None = None):
    """Ajoute une ligne de frais dans la feuille donnée.
    valeurs_dict: dict des colonnes/valeurs, ex: {"Description": "...", "montant (CHF)": 100}
    """
    path = excel_path or EXCEL_PATH
    try:
        df = pd.read_excel(path, sheet_name=feuille)
        new_row = pd.DataFrame([valeurs_dict])
        df = pd.concat([df, new_row], ignore_index=True)
        with pd.ExcelWriter(path, engine="openpyxl", mode='a', if_sheet_exists='replace') as writer:
            df.to_excel(writer, sheet_name=feuille, index=False)
    except Exception as e:
        print(f"Erreur lors de l'ajout de frais dans la feuille '{feuille}': {e}")

def modifier_frais(feuille, index_ligne, colonne, nouvelle_valeur, excel_path: str | None = None):
    """Modifie une valeur existante dans une feuille."""
    path = excel_path or EXCEL_PATH
    try:
        df = pd.read_excel(path, sheet_name=feuille)
        df.at[index_ligne, colonne] = nouvelle_valeur
        with pd.ExcelWriter(path, engine="openpyxl", mode='a', if_sheet_exists='replace') as writer:
            df.to_excel(writer, sheet_name=feuille, index=False)
    except Exception as e:
        print(f"Erreur lors de la modification de frais dans la feuille '{feuille}': {e}")

def regrouper_frais_vers_frais_divers(tri=None, ordre='asc', excel_path: str | None = None):
    """Regroupe toutes les lignes des autres feuilles dans l'onglet 'frais divers'.

    Paramètres
    ----------
    tri : str | list[str] | None
        Colonne ou liste de colonnes sur lesquelles trier le résultat.
        Si None : pas de tri (ordre d'assemblage).
    ordre : str
        'asc' (défaut) ou 'desc'. S'applique à toutes les colonnes de tri.
    excel_path : str | None
        Chemin vers le fichier Excel. Si None, utilise EXCEL_PATH.

    - Remplace complètement la feuille 'frais divers'.
    - Ajoute une colonne 'Groupe' indiquant la provenance.
    - Ne fait aucun regroupement/somme: chaque ligne originale est gardée telle quelle.
    - Si colonne 'Date' présente, elle est tentée en conversion datetime pour un tri fiable.
    
    Returns
    -------
    pd.DataFrame
        Le DataFrame agrégé ou DataFrame vide si erreur.
    """
    path = excel_path or EXCEL_PATH
    feuilles = get_feuilles(excel_path)
    print("Feuilles détectées :", feuilles)
    frames = []
    for feuille in feuilles:
        print(f"Lecture de la feuille : {feuille}")
        try:
            df = pd.read_excel(path, sheet_name=feuille)
            print(df)
            if df.empty:
                continue
            df = df.copy()
            df['Groupe'] = feuille  # Ajoute la colonne Groupe
            # Tentative de normalisation colonne Date (facultatif)
            for candidate in ["Date", "date"]:
                if candidate in df.columns:
                    try:
                        df[candidate] = pd.to_datetime(df[candidate], errors='coerce')
                    except Exception:
                        pass
            frames.append(df)
        except Exception as e:
            print(f"Erreur lors de la lecture de la feuille '{feuille}': {e}")
            continue
    
    if not frames:
        colonnes_min = ["Description", "montant (CHF)", "Groupe"]
        vide = pd.DataFrame(columns=colonnes_min)
        try:
            with pd.ExcelWriter(path, engine="openpyxl", mode='a', if_sheet_exists='replace') as writer:
                vide.to_excel(writer, sheet_name='frais divers', index=False)
            print("Aucune donnée à regrouper. Feuille 'frais divers' recréée vide.")
        except Exception as e:
            print(f"Erreur lors de l'écriture de la feuille vide: {e}")
        return vide

    frais_divers = pd.concat(frames, ignore_index=True)
    print("Résultat final :")
    print(frais_divers)

    # Vérification dev-only: présence de colonne Groupe
    if not frais_divers.empty and 'Groupe' not in frais_divers.columns:
        raise ValueError("Colonne 'Groupe' manquante après regroupement (erreur dev)")

    # Application du tri si demandé
    if tri:
        by = tri if isinstance(tri, (list, tuple)) else [tri]
        asc = True if ordre.lower() == 'asc' else False
        by_valides = [c for c in by if c in frais_divers.columns]
        if by_valides:
            try:
                frais_divers = frais_divers.sort_values(by=by_valides, ascending=asc, kind='stable')
            except Exception as e:
                print(f"Tri ignoré (erreur: {e})")
        else:
            print("Colonnes de tri inexistantes, tri ignoré.")

    # Vérification dev-only: conversion Date
    if not frais_divers.empty:
        for candidate in ["Date", "date"]:
            if candidate in frais_divers.columns:
                if not pd.api.types.is_datetime64_any_dtype(frais_divers[candidate]):
                    print(f"Attention: colonne '{candidate}' n'a pas pu être convertie en datetime")

    try:
        with pd.ExcelWriter(path, engine="openpyxl", mode='a', if_sheet_exists='replace') as writer:
            frais_divers.to_excel(writer, sheet_name='frais divers', index=False)
        print(f"{len(frais_divers)} lignes écrites dans la feuille 'frais divers'.")
        if tri:
            print(f"Tri appliqué sur: {by_valides} (ordre {'ascendant' if asc else 'descendant'}).")
    except Exception as e:
        print(f"Erreur lors de l'écriture de la feuille 'frais divers': {e}")
    
    return frais_divers

def lire_frais_divers(excel_path: str | None = None):
    """Lit la feuille 'frais divers' (après regroupement). 
    
    Returns
    -------
    pd.DataFrame
        DataFrame de la feuille 'frais divers' ou DataFrame vide si erreur/absent.
    """
    path = excel_path or EXCEL_PATH
    try:
        return pd.read_excel(path, sheet_name='frais divers')
    except FileNotFoundError:
        print(f"Fichier introuvable: {path}")
        return pd.DataFrame()
    except Exception as e:
        print(f"Impossible de lire la feuille 'frais divers' depuis {path}: {e}")
        return pd.DataFrame()

if __name__ == "__main__":
    # Exemple d'utilisation rapide avec tri par Groupe puis Date si existant
    result = regrouper_frais_vers_frais_divers(tri=["Groupe", "Date"], ordre='asc')
    print(lire_frais_divers())
