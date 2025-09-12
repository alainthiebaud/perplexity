# Génération de factures professionnelles

Ce dossier contient :
- `facture_template.tex` : modèle LaTeX complet pour générer des factures PDF avec logo, QR code, mise en page professionnelle et une seconde page d’explications détaillées.
- `logo.png` : votre logo d’entreprise (à placer dans ce dossier).
- (optionnel) `logo.ico` : version icône du logo.

## Instructions

1. Placez votre logo sous le nom `logo.png` dans ce dossier.
2. Modifiez le fichier `facture_template.tex` selon vos besoins (coordonnées, prestations, IBAN…).
3. Pour générer la facture PDF :
   ```
   pdflatex facture_template.tex
   ```
4. Le PDF généré comportera :  
   - 1ère page : facture avec logo, QR code, tableau des prestations, total, modalités, etc.
   - 2e page : explications détaillées, mentions légales, contact, modalités, etc.

## Dépendances LaTeX

- [qrcode](https://ctan.org/pkg/qrcode) : pour générer le QR code.
- [fancyhdr](https://ctan.org/pkg/fancyhdr) : pour l’en-tête/pied de page.
- [hyperref](https://ctan.org/pkg/hyperref) : pour les liens cliquables.

Installez-les via votre distribution LaTeX si besoin.

## Exemple de QR code

Le QR code pointe vers une URL personnalisable (remplacez-la dans le template).

---