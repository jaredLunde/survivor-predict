# survivor-predict
A basic statistical model for picking teams in NFL survivor pools

## Things you'll need
- An API key from [Rapid API](https://rapidapi.com/theoddsapi/api/live-sports-odds/endpoints)
- [Poetry][https://poetry.eustace.io/] for Python dependency management and packaging
## Installation
```bash
git clone https://github.com/jaredLunde/survivor-predict.git
cd survivor-predict
# Create a .env with your Rapid API key
echo "RAPID_API_KEY=${RAPID_API_KEY}" >> .env
# Installs and runs the script
poetry install
poetry run python -m survivor_predict
```
