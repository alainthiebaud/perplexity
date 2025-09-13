#!/usr/bin/env python3
"""Create a visual representation of the hierarchical UI."""

def create_ui_mockup():
    """Create a text-based mockup of the hierarchical UI."""
    
    mockup = """
╔══════════════════════════════════════════════════════════════════════════════════════╗
║                           Répartition des Charges - Frais divers                     ║
╠══════════════════════════════════════════════════════════════════════════════════════╣
║ [Fichiers & Config] [Aperçu données] [Répartitions] [Calculs & Détails] [Sorties]   ║
╠══════════════════════════════════════════════════════════════════════════════════════╣
║                                   Aperçu données                                     ║
║ ┌────────────────────────────────────────────────────────────────────────────────┐   ║
║ │ [Charges 2024] [Locataires] [Frais divers] [PAC/Energie]                      │   ║
║ └────────────────────────────────────────────────────────────────────────────────┘   ║
║                                                                                       ║
║ ┌─ Frais divers (Vue hiérarchique) ──────────────────────────────────────────────┐   ║
║ │ Description                    │ montant (CHF) │ Date      │ Groupe             │   ║
║ │ ──────────────────────────────┼───────────────┼───────────┼────────────────────│   ║
║ │ [-] 📁 Énergie (3 éléments - Total: 541.50 CHF)           │                    │   ║
║ │     • Électricité janvier      │        150.50 │ 2024-01-15│ Énergie            │   ║
║ │     • Chauffage janvier        │        250.75 │ 2024-01-20│ Énergie            │   ║
║ │     • Électricité février      │        140.25 │ 2024-02-15│ Énergie            │   ║
║ │                                │               │           │                    │   ║
║ │ [-] 📁 Assurances (2 éléments - Total: 480.50 CHF)        │                    │   ║
║ │     • Assurance immeuble       │        300.00 │ 2024-02-01│ Assurances         │   ║
║ │     • Assurance responsabilité │        180.50 │ 2024-02-01│ Assurances         │   ║
║ │                                │               │           │                    │   ║
║ │ [+] 📁 Entretien (4 éléments - Total: 746.25 CHF)         │                    │   ║
║ │                                │               │           │                    │   ║
║ └────────────────────────────────────────────────────────────────────────────────┘   ║
║                                                                                       ║
║ ┌─ Fonctionnalités disponibles ──────────────────────────────────────────────────┐   ║
║ │ • Double-clic sur un élément enfant pour éditer                                │   ║
║ │ • Clic droit pour menu contextuel (Développer/Réduire tout)                   │   ║
║ │ • Les groupes parents ne sont pas éditables                                    │   ║
║ │ • Sauvegarde préserve la hiérarchie                                           │   ║
║ │ • Affichage du nombre d'éléments et total par groupe                          │   ║
║ └────────────────────────────────────────────────────────────────────────────────┘   ║
║                                                              [Enregistrer Frais]    ║
╚══════════════════════════════════════════════════════════════════════════════════════╝

MENU CONTEXTUEL (Clic droit):
┌─────────────────────────┐
│ Développer tout         │
│ Réduire tout            │
│ ─────────────────────── │
│ Actualiser l'affichage  │
└─────────────────────────┘

FONCTIONNALITÉS IMPLÉMENTÉES:
✓ Regroupement hiérarchique par colonne 'Groupe'
✓ Icônes de dossier (📁) pour les groupes
✓ Comptage d'éléments et totaux par groupe
✓ Expand/collapse des groupes ([-] ouvert, [+] fermé)
✓ Édition des éléments enfants (double-clic)
✓ Protection des en-têtes de groupe (non éditables)
✓ Menu contextuel pour gestion globale
✓ Mise à jour automatique après édition de groupe
✓ Sauvegarde avec préservation de la hiérarchie
✓ Fallback vers affichage plat si pas de colonne 'Groupe'
✓ Gestion robuste des cas limites et erreurs
"""
    
    print(mockup)

if __name__ == "__main__":
    create_ui_mockup()