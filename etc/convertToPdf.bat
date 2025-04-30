@ECHO OFF
:: Gestion de l'UTF-8
chcp 65001 > NUL
ECHO Création du PDF, veuillez patienter
"%~3" --headless --convert-to pdf:writer_pdf_Export "%~1" --outdir "%~2"
