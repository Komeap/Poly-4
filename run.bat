@echo off
pushd "%~dp0"
title Lancement du Projet Puissance 4
cls

echo        INITIALISATION
echo.

REM Verif Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERREUR] Python n'est pas detecte !
    echo Installer python depuis python.org
    pause
    exit
)

REM Création venv
if not exist "venv" (
    echo [INFO] Creation de l'environnement virtuel 'venv'...
    echo        (Cela peut prendre une minute...)
    python -m venv venv
)

REM Activation
echo [INFO] Activation de l'environnement virtuel...
call venv\Scripts\activate

REM Install pip (On affiche tout maintenant)
echo.
echo [INFO] Mise a jour de pip...
python -m pip install --upgrade pip

REM Dépendances (On affiche tout maintenant)
echo.
echo [INFO] Installation des librairies (Numpy, Pillow, OpenCV)...
echo        Regarde les barres de progression ci-dessous :
echo.
pip install numpy Pillow opencv-python

echo.
echo ========================================================
echo                  LANCEMENT DU JEU
echo ========================================================
echo.

python main.py

if %errorlevel% neq 0 (
    echo.
    echo [ERREUR] Le programme s'est ferme avec une erreur.
)

pause