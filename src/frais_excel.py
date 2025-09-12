import pandas as pd

EXCEL_PATH = "assets/frais_divers_annuels.xlsx"

def get_feuilles():
    """Retourne toutes les feuilles à traiter sauf 'frais divers' (insensible à la casse et espaces)."""
    xls = pd.ExcelFile(EXCEL_PATH)
    return [f for f in xls.sheet_names if f.strip().lower() != "frais divers"]

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

def update_valeur_origine(groupe, source_index, colonne, nouvelle_valeur):
    """Met à jour une valeur dans la feuille d'origine.
    
    Paramètres
    ----------
    groupe : str
        Nom de la feuille source (ex: 'Entretien', 'Maintenance', etc.)
    source_index : int
        Index original de la ligne dans la feuille source
    colonne : str
        Nom de la colonne à modifier
    nouvelle_valeur : str/float/int
        Nouvelle valeur à assigner
        
    Retourne
    --------
    bool
        True si la modification a réussi, False sinon
    """
    try:
        # Vérifier que la feuille existe
        xls = pd.ExcelFile(EXCEL_PATH)
        if groupe not in xls.sheet_names:
            print(f"Erreur: La feuille '{groupe}' n'existe pas.")
            return False
            
        # Lire la feuille
        df = pd.read_excel(EXCEL_PATH, sheet_name=groupe)
        
        # Vérifier que l'index existe
        if source_index >= len(df) or source_index < 0:
            print(f"Erreur: L'index {source_index} n'existe pas dans la feuille '{groupe}'.")
            return False
            
        # Vérifier que la colonne existe
        if colonne not in df.columns:
            print(f"Erreur: La colonne '{colonne}' n'existe pas dans la feuille '{groupe}'.")
            return False
            
        # Mettre à jour la valeur
        df.at[source_index, colonne] = nouvelle_valeur
        
        # Sauvegarder
        with pd.ExcelWriter(EXCEL_PATH, engine="openpyxl", mode='a', if_sheet_exists='replace') as writer:
            df.to_excel(writer, sheet_name=groupe, index=False)
            
        print(f"Mise à jour réussie: {groupe}[{source_index}].{colonne} = {nouvelle_valeur}")
        return True
        
    except Exception as e:
        print(f"Erreur lors de la mise à jour: {e}")
        return False

def regrouper_frais_vers_frais_divers(tri=None, ordre='asc'):
    """Regroupe toutes les lignes des autres feuilles dans l'onglet 'frais divers'.

    Paramètres
    ----------
    tri : str | list[str] | None
        Colonne ou liste de colonnes sur lesquelles trier le résultat.
        Si None : pas de tri (ordre d'assemblage).
    ordre : str
        'asc' (défaut) ou 'desc'. S'applique à toutes les colonnes de tri.

    - Remplace complètement la feuille 'frais divers'.
    - Ajoute une colonne 'Groupe' indiquant la provenance.
    - Ajoute une colonne 'SourceIndex' indiquant l'index original dans la feuille source.
    - Ne fait aucun regroupement/somme: chaque ligne originale est gardée telle quelle.
    - Si colonne 'Date' présente, elle est tentée en conversion datetime pour un tri fiable.
    """
    feuilles = get_feuilles()
    print("Feuilles détectées :", feuilles)
    frames = []
    for feuille in feuilles:
        print(f"Lecture de la feuille : {feuille}")
        df = pd.read_excel(EXCEL_PATH, sheet_name=feuille)
        print(df)
        if df.empty:
            continue
        df = df.copy()
        df['Groupe'] = feuille  # Ajoute la colonne Groupe
        df['SourceIndex'] = df.index  # Ajoute l'index original de la feuille source
        # Tentative de normalisation colonne Date (facultatif)
        for candidate in ["Date", "date"]:
            if candidate in df.columns:
                try:
                    df[candidate] = pd.to_datetime(df[candidate], errors='coerce')
                except Exception:
                    pass
        frames.append(df)
    if not frames:
        colonnes_min = ["Description", "Montant (CHF)", "Groupe", "SourceIndex"]
        vide = pd.DataFrame(columns=colonnes_min)
        with pd.ExcelWriter(EXCEL_PATH, engine="openpyxl", mode='a', if_sheet_exists='replace') as writer:
            vide.to_excel(writer, sheet_name='frais divers', index=False)
        print("Aucune donnée à regrouper. Feuille 'frais divers' recréée vide.")
        return

    frais_divers = pd.concat(frames, ignore_index=True)
    print("Résultat final :")
    print(frais_divers)

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

    with pd.ExcelWriter(EXCEL_PATH, engine="openpyxl", mode='a', if_sheet_exists='replace') as writer:
        frais_divers.to_excel(writer, sheet_name='frais divers', index=False)

    print(f"{len(frais_divers)} lignes écrites dans la feuille 'frais divers'.")
    if tri:
        print(f"Tri appliqué sur: {by_valides} (ordre {'ascendant' if asc else 'descendant'}).")

def lire_frais_divers():
    """Lit la feuille 'frais divers' (après regroupement). Retourne un DataFrame ou None si erreur."""
    try:
        return pd.read_excel(EXCEL_PATH, sheet_name='frais divers')
    except Exception as e:
        print(f"Impossible de lire la feuille 'frais divers': {e}")
        return None

if __name__ == "__main__":
    # Exemple d'utilisation rapide avec tri par Groupe puis Date si existant
    regrouper_frais_vers_frais_divers(tri=["Groupe", "Date"], ordre='asc')
    print(lire_frais_divers())
