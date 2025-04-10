REM Script qui copie le plugin dans le dossier des plugins de QGis

@echo off
REM Définir le chemin source et destination
set SOURCE=%~dp0..
set DESTINATION=C:\Users\louis.huguet\Travail\Plugins\DDTM06_GenerationRapport

REM Créer le dossier de destination s'il n'existe pas
if not exist "%DESTINATION%" (
    mkdir "%DESTINATION%"
)

REM Copier tout le contenu du dossier testbuilder sans demander de confirmation
xcopy "%SOURCE%" "%DESTINATION%" /E /H /C /I /Y

REM Afficher un message de confirmation
echo Le dossier testbuilder a été copié avec succès dans %DESTINATION%.