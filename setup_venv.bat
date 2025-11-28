@echo off
echo Criando ambiente virtual...
python -m venv venv

echo Ativando ambiente virtual...
call venv\Scripts\activate

echo Instalando dependencias...
pip install -r requirements.txt

echo.
echo Ambiente configurado com sucesso!
echo Para executar a aplicacao, use: run_app.bat
pause