# Qualidade: Reprodutibilidade, Testes e CI

> Itens de engenharia de software que pontuam no relatório e tornam o projeto robusto e reproduzível.

## 1. Reprodutibilidade com Docker

Subir toda a stack (Node + Python) com um comando facilita avaliação e demo.

- `ai-service/Dockerfile` — imagem Python com FastAPI + Ultralytics.
- `backend/Dockerfile` — imagem Node + Express.
- `docker-compose.yml` na raiz — orquestra os dois (e variáveis de ambiente).

```yaml
# docker-compose.yml (esqueleto)
services:
  ai-service:
    build: ./ai-service
    ports: ["8000:8000"]
    env_file: .env
  backend:
    build: ./backend
    ports: ["3000:3000"]
    env_file: .env
    depends_on: [ai-service]
```

Comando único: `docker compose up`. Documentar no README.

## 2. Estratégia de testes

| Nível | O que testar | Ferramenta |
|-------|--------------|------------|
| Unitário (IA) | **Motor de fusão** e **limiares** (entradas conhecidas → risco esperado) | `pytest` |
| Unitário (IA) | Funções de pré-processamento (parsing CSV, features) | `pytest` |
| Unitário (Node) | Rotas de orquestração (mock do serviço Python) | `jest` |
| Integração | Pipeline ponta-a-ponta com mini-dataset (upload → IA → JSON) | `pytest` + container |

> Prioridade: testar o **motor de fusão**, pois é o núcleo do valor do projeto. Casos: só vídeo, só sinais vitais, ambos, nenhum, áudio com violência.

Exemplo de caso de teste da fusão:
```python
def test_fusao_alto_risco():
    r = avaliar_fusao(video={"evento": "sangramento", "confianca": 0.9},
                      vitais={"tipo": "hipotensao", "valor": 85})
    assert r["risco_detectado"] == "ALTO"
```

## 3. CI com GitHub Actions

Workflow `.github/workflows/ci.yml` que a cada push/PR:
1. Instala dependências (Python e Node).
2. Roda lint (`ruff`/`flake8`, `eslint`).
3. Roda testes (`pytest`, `jest`).

```yaml
# .github/workflows/ci.yml (esqueleto)
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: pip install -r ai-service/requirements.txt
      - run: pytest ai-service
```

## 4. Observabilidade
- **Logging estruturado** (JSON) em ambos os serviços, com `case_id` para rastrear um caso ponta-a-ponta.
- Logs de erro do serviço Python isolados (facilita debug da IA sem ruído do backend).

## 5. Definition of Done de qualidade
- [ ] `docker compose up` sobe a stack
- [ ] Testes do motor de fusão passando
- [ ] CI verde no PR
- [ ] Logging com `case_id` nos dois serviços
