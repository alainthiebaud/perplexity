# Implémentation de l'Affichage Hiérarchique - Frais Divers

## Résumé de l'Implémentation

Cette implémentation ajoute un affichage hiérarchique dans l'onglet "Frais divers" de l'application, permettant de regrouper les lignes selon leur catégorie (groupe) avec une structure parent-enfant.

## Fonctionnalités Implémentées

### ✅ Affichage Hiérarchique
- Les lignes sont regroupées par la colonne 'Groupe'
- Structure parent-enfant claire avec icônes de dossier (📁)
- Comptage automatique d'éléments par groupe
- Calcul et affichage des totaux par groupe

### ✅ Expand/Collapse
- Chaque groupe peut être ouvert/fermé individuellement
- Indicateurs visuels ([-] ouvert, [+] fermé)
- Menu contextuel pour développer/réduire tous les groupes

### ✅ Édition Préservée
- Double-clic sur les éléments enfants pour éditer
- Protection des en-têtes de groupe (non éditables)
- Mapping correct entre l'affichage et les données
- Mise à jour automatique si le groupe d'un élément change

### ✅ Interface Utilisateur
- Menu contextuel (clic droit) avec options :
  - Développer tout
  - Réduire tout
  - Actualiser l'affichage
- Distinction visuelle des groupes et éléments
- Préservation de toutes les fonctionnalités existantes

### ✅ Robustesse
- Fallback vers affichage plat si pas de colonne 'Groupe'
- Gestion des cas limites (données vides, types mixtes)
- Sauvegarde avec préservation de la hiérarchie

## Fichiers Modifiés

### `src/app_ui.py`
- **Nouvelle méthode** : `_fill_tree_hierarchical_frais()` - Remplit l'arbre avec affichage hiérarchique
- **Nouvelle méthode** : `_start_edit_cell_hierarchical()` - Gestion de l'édition hiérarchique
- **Nouvelle méthode** : `_commit_edit_hierarchical()` - Validation des modifications hiérarchiques
- **Nouvelle méthode** : `_setup_frais_context_menu()` - Configuration du menu contextuel
- **Nouvelles méthodes** : `_expand_all_groups()`, `_collapse_all_groups()` - Gestion expand/collapse
- **Modification** : Méthode `_load_all()` - Utilise l'affichage hiérarchique pour frais
- **Modification** : Méthode `_save_frais()` - Actualise l'affichage après sauvegarde

## Structure des Données

L'affichage hiérarchique utilise la colonne 'Groupe' existante créée par le module `frais_excel.py` lors du regroupement des feuilles.

### Format d'Affichage
```
📁 Énergie (3 éléments - Total: 541.50 CHF)
    • Électricité janvier     150.50 CHF
    • Chauffage janvier       250.75 CHF  
    • Électricité février     140.25 CHF

📁 Assurances (2 éléments - Total: 480.50 CHF)
    • Assurance immeuble      300.00 CHF
    • Assurance responsabilité 180.50 CHF
```

## Compatibilité

- ✅ Compatible avec l'interface existante
- ✅ Préserve toutes les fonctionnalités d'édition et sauvegarde
- ✅ Fonctionne avec les données existantes du module `frais_excel`
- ✅ Fallback automatique si structure non hiérarchique

## Tests Réalisés

- ✅ Test d'affichage hiérarchique avec données réelles
- ✅ Test d'édition et de sauvegarde
- ✅ Test des cas limites (données vides, sans groupe)
- ✅ Test d'intégration avec `frais_excel`
- ✅ Test de robustesse avec types de données mixtes

## Utilisation

1. Charger un fichier Excel avec des données de frais divers contenant une colonne 'Groupe'
2. L'affichage hiérarchique se met en place automatiquement
3. Utiliser le clic droit pour accéder aux options de gestion des groupes
4. Double-cliquer sur les éléments enfants pour les éditer
5. Sauvegarder normalement - la hiérarchie est préservée

Cette implémentation répond à tous les critères demandés tout en conservant la compatibilité avec le code existant.