set INPUT_PATH="C:\Users\louis.huguet\Travail\Prog\ddtm_generationrapport"
set OUTPUT_PATH="C:\Users\louis.huguet\Travail\Plugins\DDTM06_GenerationRapport"

robocopy %INPUT_PATH% %OUTPUT_PATH% /E /XF journal.txt README.md /XD .git tools