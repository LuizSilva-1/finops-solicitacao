# Provisionamento FinOps Local (sem integrações AWS)

Aplicação web local (FastAPI + Postgres) para registrar solicitações de provisionamento com foco em FinOps. Não cria/encerra recursos na nuvem; serve para controle, aprovação, expiração e auditoria. Inclui autenticação com roles (admin/solicitante), importação CSV, notificações por webhook (Rocket.Chat/Slack), paginação/filtros e testes básicos.

## Stack
- Backend: FastAPI, SQLAlchemy, Alembic, JWT (PyJWT), bcrypt.
- Banco: Postgres (Docker Compose).
- Frontend simples estático servido pelo FastAPI.
- Worker: marca solicitações expiradas.

## Rodando
```bash
cp .env.example .env  # se quiser customizar
docker compose up --build -d
# aplica migrações e sobe app em http://localhost:8000
```
Login inicial: `admin / admin123`. Admin cria usuários e aprova/expira/removê solicitações; não cria solicitações.

## Configuração principal (env)
- `DATABASE_URL`: já definido no compose para Postgres.
- `SECRET_KEY`: troque para algo seguro.
- `WEBHOOK_URL`: URL de webhook (Rocket.Chat/Slack/Teams).
- `WEBHOOK_CHANNEL` (opcional): canal do webhook.
- `WEBHOOK_USERNAME` (opcional): nome do bot.
- `ALLOWED_SERVICES`, `ALLOWED_REGIONS`, `MAX_EXPIRATION_DAYS`: configuráveis em `app/core/config.py` ou via env.

## Funcionalidades
- Autenticação JWT, roles admin/user. Admin vê todas, user só as próprias.
- Solicitações com validações: serviço/região permitidos, conta obrigatória, data futura até N dias, admin bloqueado de criar.
- Página única:
  - User: cria solicitações e acompanha status.
  - Admin: aprova/expira/removê, vê detalhes em modal, importa CSV, filtra (status, expira até), paginação, chips de status.
- Importação CSV (admin): botão “Importar CSV” → `/api/imports/csv` (campos: requester, service_type, aws_account, region, expires_at YYYY-MM-DD, status, params, tags). Template em `data/import_template.csv`.
- Notificações por webhook: criação, mudança de status, expiração e remoção.
- Worker: marca como expirada se `expires_at` for alcançada.
- Healthcheck: `/health` (usado pelo compose).

## Endpoints principais
- `POST /api/auth/login` (JWT), `POST /api/auth/refresh`, `POST/GET /api/auth/users` (admin).
- `POST /api/requests` (user), `GET /api/requests` (paginação/filtros), `PATCH /api/requests/{id}` (admin), `POST /requests/{id}/expire`, `/mark-removed` (admin).
- `POST /api/imports/csv` (admin).

## Testes
```bash
docker compose run --rm app pytest
```
(usa SQLite em memória com overrides).

## Notas
- Admin não cria solicitações; use-o para criar usuários e aprovar/gerir.
- Para Rocket.Chat, defina `WEBHOOK_URL` e opcionalmente `WEBHOOK_CHANNEL`/`WEBHOOK_USERNAME`.
