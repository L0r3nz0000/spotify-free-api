read -s -p "Inserisci lo username del tuo account spotify: " USERNAME
echo ""

read -s -p "Inserisci la password del tuo account spotify: " PASSSWORD
echo ""

echo "username='$USERNAME'\npassword='$PASSWORD'" > credentials.py

if [ ! -d ".env" ]; then
  echo "Sto creando l'ambiente virtuale"
  python3 -m venv .env
else
  echo "Ambiente virtuale python già presente"
fi

source .env/bin/activate

pip install -r requirements.txt