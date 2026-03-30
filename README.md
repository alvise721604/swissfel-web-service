# user_services_ng

Mini progetto NiceGUI multipagina per sostituire una GUI Flask-based con:

- pagina Home
- Create Reservation
- Cluster Status
- Cleanup PGROUP
- wrapper HTTP riusabile
- job asincroni per cleanup
- lettura utente autenticato da header HTTP

## Avvio rapido

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

## Variabili d'ambiente utili

- `HOST`
- `PORT`
- `RA_API_BASE_URL`
- `RA_API_USERNAME`
- `RA_API_PASSWORD`
- `REQUESTS_VERIFY`
- `TRUSTED_USER_HEADER`
- `CLEANUP_SCRIPT`
- `CLEANUP_TIMEOUT_SECONDS`

`REQUESTS_VERIFY` può essere:

- `true`
- `false`
- path a un CA bundle

## Note

Il codice in `services/ra_api.py` contiene un fallback stub se il backend reale non è ancora collegato.
Il controllo LDAP in `services/ldap_service.py` è ancora uno stub da sostituire con la tua logica reale.
