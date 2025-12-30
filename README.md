# Provisionamento FinOps AWS (controle local, sem integrações)

Proposta de sistema web para registrar e controlar provisionamentos na AWS com foco em FinOps, mas operando 100% localmente (nenhuma chamada/integração com AWS). A aplicação mantém o inventário, ciclo de vida e alertas; toda ação na nuvem é manual e apenas registrada.

## Visão geral
- Usuários registram solicitações informando: solicitante, serviço (snapshot EBS, EC2, ELB etc.), finalidade, tags/custos, região, tempo de uso e data de remoção.
- O backend não cria/encerra recursos: ele apenas registra inventário, controla vencimentos e alertas, e registra evidências de quem executou ações manualmente.
- Alertas notificam responsáveis antes do vencimento; políticas podem exigir confirmação periódica ou marcar itens como expirados/removidos.

## Arquitetura sugerida (self-hosted, offline)
- **Frontend**: SPA (React/Vue) servida por Nginx/Express; autenticação local (Keycloak/Authelia/LDAP) ou JWT simples.
- **API**: serviço Node/Python com endpoints REST; cron interno para lembretes/expiração.
- **Persistência**: Postgres (recom.) ou SQLite para MVP (`requests`, `alerts`, `audit`, `imports`).
- **Notificações**: Webhook (Rocket.Chat/Slack/Teams) ou e-mail SMTP local (sem usar serviços de nuvem).
- **Ops**: Docker Compose para subir app + banco + worker de agendamento.

## Fluxo de solicitação
1) Solicitação criada via frontend → API: payload com serviço, parâmetros, tempo de uso e data de remoção.  
2) Backend valida políticas (limites, tags obrigatórias, datas).  
3) Registro persiste em `requests` com status `pendente`/`aprovado`/`em_uso`.  
4) Auditoria registra quem criou/aprovou.  
5) Cron agenda lembretes (T-7d, T-1d) e evento de expiração; notifica responsáveis e FinOps.  
6) Ao expirar, o item vira `expirado`; alguém marca como removido após executar a ação manualmente na nuvem. Auditoria registra o responsável e evidências (ex.: ID do recurso removido).

## Modelo de dados (exemplo Postgres)
- `requests`: `id` (pk), `requester`, `service_type`, `params` (JSON), `cost_center`, `tags`, `region`, `status`, `created_at`, `expires_at`, `retention_days`, `resource_id` (ID anotado pelo usuário), `estimated_cost`, `auto_delete` (bool), `approver`, `last_alert_at`.
- `alerts`: `id`, `request_id`, `type` (`reminder`, `expiration`), `scheduled_for`, `status`.
- `audit`: `id`, `request_id`, `action`, `by`, `at`, `details`.
- `imports` (opcional): histórico de cargas CSV/JSON vindas de relatórios ou planilhas (sem chamadas de API).

## API (exemplo)
- `POST /requests`: cria solicitação; calcula `expires_at`.
- `GET /requests?status=...`: lista com filtros (solicitante, serviço, vencimento, custo).
- `PATCH /requests/{id}`: aprova/reprova/renova; reagenda alertas.
- `POST /requests/{id}/expire`: marca como expirado (status interno).
- `POST /requests/{id}/mark-removed`: registra que o recurso foi removido manualmente.
- `POST /imports`: recebe CSV/JSON para conciliar inventário com relatórios/planilhas (opcional).

## Tags padrão recomendadas
`Owner=<email>`, `CostCenter=<cc>`, `Project=<proj>`, `ExpiresAt=<yyyy-mm-dd>`, `AutoDelete=<true|false>`, `Ticket=<id>`, `Environment=<env>`.  
Obrigatório informar `ExpiresAt`; não aprovar solicitações sem tags mínimas.

## Políticas de ciclo de vida
- Vencimento obrigatório; impedir submissão sem data de remoção.
- Renovação explícita via painel; sem renovação, vira `expirado` e exige ação manual na AWS.
- Limites por serviço (ex.: qtd snapshots por solicitante, tipos de EC2 permitidos) apenas como regras de aprovação local.
- Janelas de manutenção: alertar ou bloquear remoções fora da janela.

## Alertas e automação (local)
- Cron/worker envia alertas via SMTP ou webhooks a T-7d e T-1d; alerta de expiração no dia.
- Após expirar, continuar notificando até alguém marcar como removido/renovado.
- Painel de pendências: itens a expirar, expirados sem evidência, e SLAs de resposta.

## Segurança e acesso
- Autenticação via IdP local (Keycloak/LDAP) ou JWT simples; perfis `finops-admin`, `requester`, `approver`.
- Auditoria completa das mudanças de status e renovações.
- Exigir 2FA no IdP se disponível.

## FinOps e custo
- Estimativa manual ou calculada por tabelas internas (sem chamada a APIs de nuvem).  
- Importar CSV de billing/export ou planilhas internas para enriquecer custos por tag/centro de custo (opcional).  
- Relatórios: dashboards locais por tag/centro de custo, backlog de recursos vencidos, ranking de solicitações mais caras.

## Backlog inicial
- Criar frontend básico com formulário de solicitação e painel de vencimentos/pendências.
- Implementar `POST /requests`, `PATCH /requests/{id}`, `POST /requests/{id}/terminate`.
- Criar Step Function simples para snapshot EBS (criar/deletar) como MVP.
- Configurar EventBridge Scheduler + SNS/Slack para lembretes.
- Adicionar relatórios básicos de custos por tag.
