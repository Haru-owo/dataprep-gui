sudo apt install python3.10-venv -y

python3 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

echo "Virtual environment setup complete! Run 'source .venv/bin/activate' to activate."