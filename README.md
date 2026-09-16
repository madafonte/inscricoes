# Concursos TI — Recife

Agregador pessoal de concursos públicos de TI com inscrições abertas, presenciais em Recife-PE, filtrado para nível médio/técnico ou superior (com aceitação de "cursando").

Site publicado em: https://madafonte.github.io/inscricoes/

## Como funciona

O script em `scraper/` consulta o [servidor MCP oficial do PCI Concursos](https://www.pciconcursos.com.br/mcp-e-gpt) (`https://mcp.pciconcursos.com.br/mcp`) — uma interface de dados estruturados mantida pela própria PCI Concursos, sem necessidade de ler o HTML da página. Isso evita o principal risco de manutenção de um scraper tradicional (o site mudar de layout).

O script filtra os resultados por:
- **Relevância de TI** — lista de termos em [scraper/filtros.py](scraper/filtros.py)
- **Localização** — só presencial em Recife-PE; casos incertos aparecem no site marcados como "verificar"
- **Escolaridade** — nível médio/técnico sempre incluído; nível superior só se houver indício de aceitar candidatos "cursando"

O resultado é salvo em `data/concursos.json` e copiado para `docs/data/concursos.json`, que é o que o site (pasta `docs/`) lê.

## Rodar manualmente

**Pelo GitHub (recomendado, não precisa instalar nada):**
Vá na aba **Actions** do repositório → workflow **"Atualizar concursos"** → botão **"Run workflow"**.

**Localmente** (precisa de Python 3.10+):
```bash
pip install -r scraper/requirements.txt
python scraper/main.py
cp data/concursos.json docs/data/concursos.json
```
Depois abra `docs/index.html` no navegador, ou sirva localmente:
```bash
cd docs && python -m http.server
```

## Limitações conhecidas

- Só cobre concursos com **inscrições abertas** — editais "previstos/anunciados" ficam para uma fase futura.
- Só usa o PCI Concursos como fonte — Google Notícias fica para uma fase futura.
- A detecção de "aceita cursando" (para vagas de nível superior) depende de o título/cargo mencionar isso explicitamente — informação que geralmente só está no PDF completo do edital. Pode haver vagas elegíveis sendo excluídas por falta desse sinal no texto.
- Concursos nacionais/federais de TI aparecem marcados como "verificar" (a API não expõe "cidade da prova" pra esses casos) — é preciso checar manualmente se o concurso tem polo de prova em Recife antes de se candidatar.
- A automação diária (GitHub Actions com `cron`) está propositalmente desligada por enquanto — o workflow só roda quando disparado manualmente (`workflow_dispatch`). Para ligar, descomente o bloco `schedule` em [.github/workflows/update.yml](.github/workflows/update.yml).

## Manutenção do site (cache do navegador)

`docs/index.html` referencia `app.js` e `style.css` com um parâmetro `?v=N` (ex.: `app.js?v=2`). Isso existe pra forçar o navegador a buscar a versão nova sempre que esses arquivos mudam — sem isso, quem já visitou o site antes pode ficar até ~10 minutos vendo a versão em cache. **Toda vez que `docs/app.js` ou `docs/style.css` for editado, incremente o número da versão em `docs/index.html`.**

## Ajustar os filtros

- Termos de busca de TI: `PALAVRAS_TI` em [scraper/filtros.py](scraper/filtros.py)
- Termos de localização/Recife: `_TERMOS_RECIFE` em [scraper/filtros.py](scraper/filtros.py)
- Destaque de prazo urgente no site: classes `.urgente` (≤7 dias) e `.atencao` (≤15 dias) em [docs/style.css](docs/style.css), limites definidos em [docs/app.js](docs/app.js)
