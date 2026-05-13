# Redditi postituste automaatne klassifitseerimine erineva signaalitasemega keskkondades
### Ann Marleen Varul

## Andmete kogumine ja puhastamine
Andmete kogumiseks tuleb luua `.env` fail:
```env
REDDIT_CLIENT_ID=...
REDDIT_CLIENT_SECRET=...
REDDIT_USER_AGENT=...
```

- `collect_posts.py` - andmete kogumine
- `data_cleaning.py` - andmete puhastamine
- `clean_format_llm.py` - andmete puhastamine ja struktureerimine LLM mudelite jaoks


## Andmete analüüs
Andmete analüüsiks GPT-4.1-mini mudeliga tuleb lisada `.env` fail:
```env
OPENAI_API_KEY=...
```

Alguses võrreldi kolme LLM-i mudelit, kuid lõplikust võrdlusest jäeti esimene LLM-i katsetus välja, sest see osutus sisutühjaks (LLM-ile ei antud ette alamfoorumi nimetus, kuid konteksti mõistmine on just see, mis on LLM-i eeliseks). Seetõttu on ka failide nimetused natuke segadust tekitavad: "llm1" tähistab failinimedes võrdlusest välja jäetud LLM-i mudelit, "llm2" on tegelikult LLM-1 ja "llm3" on LLM-2.

`Notebooks` kaust
- `gold_standard_llm1` kaust sisaldab esimest (võrdlusest välja jäetud) LLM-i võrdlust RoBERTa mudelitega ja kuldstandardi loomist
- `llm_second.ipynb` sisaldab LLM-1 mudeli võrdlusi RoBERTa mudelitega
- `llm_third.ipynb` sisaldab LLM-2 mudeli võrdlusi RoBERTa mudelitega
- `model_comparison.ipynb` sisaldab RoBERTa mudelite ning LLM-1 ja LLM-2 võrdlus
- `signal_level_comparison.ipynb` sisaldab signaalitasemete võrdlusi
- `thread_level_classification.ipynb` - sisaldab lõime analüüsi (MVP jaoks)



## MVP
Analüüsi tulemuste põhjal loodi MVP, mis demonstreerib, kuidas Redditi postituste automaatne klassifitseerimine on võimalik integreerida terviklikuks süsteemiks ning esitada tulemused tootejuhile struktureeritud ning kasutajasõbralikul viisil.

MVP kasutab HubSpoti näitel eelnevalt kogutud ja analüüsitud andmeid.

### Struktuur: 
Kasutajaliides (Vue.js)  ->  Taustaprogramm (FastAPI)  ->  Andmefail (JSON)

#### Andmete eeltöötlus
Meelestatuse määramiseks kasutati GPT-4.1-mini-põhist mudelit kahe viibaga. Esimene viip määras meelestatuse ja teine tegi sügavama analüüsi. Analüüsitud andmed salvestati `data/thread_level_results/thread_results_mvp.json` faili 
- `notebooks/thread_level_classification.ipynb` - kood analüüsi jaoks 

#### Frontend (Vue.js)
Komponendid
- `App.vue` — peamine komponent, API päringud `main.py`-le
- `Header.vue` — päis koos otsinguga
- `Side.vue` — külgriba alamfoorumi valikuga ja filtritega
- `Thread.vue` — ühe lõime kast
- `Comments.vue` — kommentaaride hierarhiline kuvamine

Käivitamine (`mvp-ui` kaustas olles):
```bash
npm install
npm run dev
```
Avaneb aadressil: http://localhost:5173

#### Backend (FastAPI)
- `main.py` - võtab andmed JSON failist

Käivitamine (`backend` kaustas olles):
```bash
uvicorn main:app --reload
```
Töötab aadressil: http://localhost:8000
