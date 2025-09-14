@echo off
REM Ce script doit être placé à la racine du dépôt (même dossier que main.py)

REM Aller dans le dossier du script (la racine du projet)
cd /d "%~dp0"

REM Mettre à jour la branche courante depuis GitHub
git pull

REM Lancer le script principal Python
python main.py

pause