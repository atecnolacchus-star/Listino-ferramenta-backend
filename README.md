BACKEND — LISTINO FERRAMENTA
===============================

Indirizzo pubblicato attualmente in uso dal front-end:
    https://listino-ferramenta-backend.onrender.com
(vedi "const API_BASE" in pwa/index.html se lo cambi)

Backend REST in Python (Flask) + SQLite. Gestisce login, catalogo,
aumento prezzi per classe articolo, import Excel, preventivi/offerte con
calcolo IVA e sconti a cascata, e gestione credenziali degli account.

AVVIO IN LOCALE
------------------
    pip install -r requirements.txt
    python3 seed.py          # crea il database con gli account e il catalogo
    python3 app.py           # avvia il server su http://localhost:5000

Variabili d'ambiente utili:
    SECRET_KEY   chiave di firma dei token di login (impostala sempre in
                 produzione: se non specificata viene generata a caso ad
                 ogni riavvio e tutti gli utenti vengono disconnessi)
    PORT         porta di ascolto (default 5000)
    DEBUG=1      abilita il reload automatico in sviluppo

ACCOUNT DI DEFAULT (creati da seed.py)
------------------------------------------
  Master      -> username: master      password: Master2026!
  Standard 1  -> username: standard1   password: Standard1!
  Standard 2  -> username: standard2   password: Standard2!
  Standard 3  -> username: standard3   password: Standard3!
  Standard 4  -> username: standard4   password: Standard4!
  Standard 5  -> username: standard5   password: Standard5!

Username e password si possono cambiare via API (vedi sotto) — sia dal
proprio account, sia da Master per qualunque account.

ENDPOINT PRINCIPALI
-----------------------
Autenticazione: header  Authorization: Bearer <token>  (ottenuto da /api/login,
valido 12 ore).

  POST   /api/login                        {username, password} -> {token, user}
  GET    /api/me                           utente corrente
  PATCH  /api/account/credentials          cambio username/password proprio
                                            {currentPassword, newUsername?, newPassword?}
  GET    /api/accounts                     [solo master] elenco account
  PATCH  /api/accounts/<id>                [solo master] modifica diretta credenziali
                                            {newUsername?, newPassword?, newName?}

  GET    /api/catalog                      catalogo completo (categorie + articoli)
  GET    /api/master/classes               [solo master] elenco "Desc. classe articolo"
  POST   /api/master/price-increase        [solo master] {classes:[...], pct}
  POST   /api/master/import                [solo master] upload file Excel (multipart, campo "file")

  GET    /api/quotes                       preventivi/offerte (proprie se standard, tutte se master)
  POST   /api/quotes                       [solo standard] crea preventivo/offerta
                                            {type:"Offerta"|"Preventivo", orderInfo:{...}, items:[...]}
                                            -> calcola automaticamente imponibile, IVA 22%, totale
  PATCH  /api/quotes/<id>                  {status:"Da confermare"|"Confermato"|"Annullato"}

  GET    /api/health                       stato del server

Ogni riga di "items" in POST /api/quotes accetta: codice, descrizione, qty,
prezzo, sconto1, sconto2, sconto3 (percentuali applicate in cascata: es.
sconto1=10, sconto2=5 equivale a un netto = prezzo × 0,90 × 0,95).

PUBBLICAZIONE (STESSO DISCORSO FATTO PER IL FRONT-END)
------------------------------------------------------------
Anche questo backend, per essere raggiungibile dal front-end installato sul
tablet, deve girare su un vero hosting (non sul tuo computer locale).
Opzioni semplici e con piano gratuito: Render.com, Railway.app, Fly.io.
In generale: crea un nuovo servizio Python, collega questa cartella, imposta
la variabile d'ambiente SECRET_KEY, e come comando di avvio:
    gunicorn app:app --bind 0.0.0.0:$PORT
(aggiungi "gunicorn" a requirements.txt: è il server di produzione consigliato
al posto di "python3 app.py", pensato solo per lo sviluppo).

STATO DELL'INTEGRAZIONE COL FRONT-END
------------------------------------------
Il front-end (index.html) oggi funziona in autonomia, senza chiamare questo
backend: login, catalogo, preventivi e credenziali sono gestiti nel browser
(vedi limiti descritti nel LEGGIMI.txt della cartella pwa/). Questo backend è
pronto e testato, ma collegarlo davvero al front-end (sostituire l'array
ACCOUNTS e il catalogo incorporato con chiamate fetch a questi endpoint)
è un passo di integrazione successivo, perché richiede un indirizzo del
backend già pubblicato a cui il front-end possa collegarsi. Fammi sapere
quando il backend è online e ti preparo il collegamento.

DATABASE
-----------
ferramenta.db (SQLite) contiene già gli account e il catalogo importato da
products.json. Per ripartire da zero: python3 seed.py --force (attenzione,
cancella tutti i preventivi salvati e le modifiche fatte finora).
