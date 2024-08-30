# Install
```bash
git clone https://github.com/L0r3nz0000/spotify-free-api.git
cd spotify-free-api
python3 -m venv .env
source .env/bin/activate
pip install -r requirements.txt
flask run
```

## endpoints
- `/pause`
- `/resume`
- `/next_track`
- `/prev_track`
- `/set_volume/<percentage>`
