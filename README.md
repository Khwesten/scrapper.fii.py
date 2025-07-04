# 🏢 FII Scraper API v2.0

Uma API moderna para scraping e análise de Fundos de Investimento Imobiliário (FIIs) brasileiros com **scraping automático**, **descoberta dinâmica de FIIs** e **armazenamento em DynamoDB**.

## ✨ **Principais Funcionalidades**

- 🔄 **Scraping Automático**: Seed inicial + atualizações a cada 8 horas
- 🌐 **Descoberta Dinâmica**: Lista automaticamente todos os FIIs disponíveis 
- 🗄️ **DynamoDB Nativo**: Armazenamento escalável em nuvem
- 🧪 **Testes E2E**: Testes automatizados completos
- 📊 **Health Check Inteligente**: Monitoramento de API + banco + scheduler
- 🛠️ **Makefile Centralizado**: Comandos simplificados para desenvolvimento
- 📚 **ReDoc**: Interface moderna de documentação da API
- ⚙️ **Configuração Centralizada**: Suporte a múltiplos ambientes (local, test, dev, prod)

## 🚀 **Início Rápido**

### Pré-requisitos
- Docker & Docker Compose
- Make
- Python 3.10+ e Poetry (para desenvolvimento local)

### Comandos por Ambiente

#### 🏠 **Desenvolvimento Local**
```bash
# Iniciar ambiente completo (API na porta 8001)
make dev-up

# Ver logs em tempo real
make dev-logs

# Parar ambiente
make dev-down
```

#### 🧪 **Testes**
```bash
# Executar todos os testes (126 testes)
make test-all

# Testes unitários (68 testes)
make test-unit

# Testes de integração (27 testes)
make test-integration

# Testes E2E (31 testes)
make test-e2e

# Formatar código
make format
```

#### 🐳 **Produção**
```bash
# Iniciar produção (API na porta 8000)
make prod-up

# Ver logs de produção
make prod-logs

# Parar produção
make prod-down
```

### Comandos de Monitoramento

```bash
# Verificar saúde do sistema
make health

# Ver status detalhado do banco
make status

# Abrir documentação da API
make docs
```

## ⚙️ **Configuração de Ambientes**

A aplicação suporta múltiplos ambientes com configuração centralizada:

### Ambientes Disponíveis

| Ambiente | API Port | DynamoDB | Config File | Uso |
|----------|----------|----------|-------------|-----|
| **Local** | 8001 | localhost:8002 | `config.yml` | Desenvolvimento |
| **Test** | 8000 | localhost:8002 | `config-test.yml` | Testes unitários/integração |
| **E2E** | 8080 | dynamodb-local:8000 | `config-e2e.yml` | Testes E2E no Docker |
| **Prod** | 8000 | AWS DynamoDB | Env vars | Produção |

### Configuração via Arquivo YAML

```yaml
api:
  host: "localhost"
  port: 8001
  debug: true

database:
  type: "dynamodb"
  dynamodb:
    table_name: "fiis"
    region: "us-east-1"
    endpoint: "http://localhost:8002"  # null para AWS
    access_key: "dummy"                # null para AWS IAM
    secret_key: "dummy"                # null para AWS IAM

external:
  status_invest:
    base_url: "https://statusinvest.com.br/fundos-imobiliarios/"
    timeout: 30

scheduler:
  scrape_interval_hours: 8
```

### Configuração via Variáveis de Ambiente

```bash
# Ambiente
export ENVIRONMENT=local|test|e2e|prod

# API
export API_HOST=localhost
export API_PORT=8001
export API_DEBUG=true

# DynamoDB
export DYNAMODB_TABLE_NAME=fiis
export DYNAMODB_ENDPOINT=http://localhost:8002
export AWS_REGION=us-east-1
export AWS_ACCESS_KEY_ID=dummy
export AWS_SECRET_ACCESS_KEY=dummy

# Status Invest
export STATUS_INVEST_BASE_URL="https://statusinvest.com.br/fundos-imobiliarios/"
export STATUS_INVEST_TIMEOUT=30

# Scheduler
export SCRAPE_INTERVAL_HOURS=8
```

## 📡 **Endpoints da API**

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/health` | GET | Health check com status de banco e scheduler |
| `/database/status` | GET | Status detalhado do banco e estatísticas |
| `/fiis` | GET | Lista todos os FIIs |
| `/fiis/magic_numbers` | GET | Cálculo de magic numbers |
| `/docs` | GET | Documentação interativa (ReDoc) |

### URLs por Ambiente

| Ambiente | Base URL | Documentação |
|----------|----------|--------------|
| **Local** | http://localhost:8001 | http://localhost:8001/docs |
| **Test** | http://localhost:8000 | http://localhost:8000/docs |
| **E2E** | http://localhost:8080 | http://localhost:8080/docs |
| **Prod** | http://localhost:8000 | http://localhost:8000/docs |

### Exemplos de Uso

```bash
# Health check completo (ambiente local)
curl http://localhost:8001/health

# Status do banco
curl http://localhost:8001/database/status

# Listar FIIs
curl http://localhost:8001/fiis

# Magic numbers com investimento de R$ 10.000
curl "http://localhost:8001/fiis/magic_numbers?invested_value=10000"
```

## 🔄 **Sistema de Scraping Automático**

### Funcionamento
- **Inicialização**: Scraping automático após 30s da inicialização
- **Descoberta**: Lista dinamicamente todos os FIIs disponíveis no Status Invest
- **Atualizações**: Executa a cada 8 horas automaticamente
- **Fallback**: Em caso de falha no gateway, usa lista de FIIs populares

### Logs do Scheduler
```
🌱 Starting initial database seed...
✅ Initial seed completed: 145 FIIs added from gateway
🔄 Starting scheduled FII update...
✅ Scheduled update completed: 152 FIIs updated from gateway
```

## 🛠️ **Desenvolvimento**

### Estrutura do Projeto
```
├── app/                    # Código principal da aplicação
├── tests/                  # Testes (unit, integration, e2e)
├── config*.yml             # Arquivos de configuração por ambiente
├── app_config.py           # Classe central de configuração
├── docker-compose.yml      # Orquestração Docker
├── Makefile               # Comandos automatizados
└── README.md              # Este arquivo
```

### Comandos de Desenvolvimento
```bash
# Executar localmente (sem Docker)
poetry install
export ENVIRONMENT=local
poetry run python main.py

# Executar testes específicos
poetry run pytest tests/unit/ -v
poetry run pytest tests/integration/ -v  
poetry run pytest tests/e2e/ -v

# Verificar qualidade do código
make format
```

## 🚀 **Melhorias Implementadas v2.0**

### ✅ Configuração Centralizada
- ⚙️ **Sistema unificado**: AppConfig com suporte a YAML e env vars
- 🌍 **Multi-ambiente**: Configurações específicas para local/test/e2e/prod
- 🔒 **Type-safe**: Propriedades tipadas e validadas
- 📝 **Zero hardcode**: Todas as portas/URLs/credenciais configuráveis

### ✅ Removidas Dependências Obsoletas
- ❌ Rotas `/fiis/scrape` e `/database/seed` (redundantes)
- ❌ Arquivo `scrape.py` (obsoleto)
- ❌ Todas as referências a CSV

### ✅ Scraping Inteligente
- 🌐 Descoberta automática de todos os FIIs disponíveis
- 🔄 Sem listas fixas - usa gateway para listar FIIs
- ⚡ Fallback para FIIs populares em caso de falha

### ✅ Testes Completos
- 🧪 **126 testes total**: 68 unit + 27 integration + 31 e2e
- ⚡ Execução rápida e confiável
- 📊 Validação completa do sistema
- � Configuração automatizada de ambientes de teste

## 📈 **Próximas Melhorias**

- [ ] Métricas avançadas (Prometheus)
- [ ] Alertas automáticos (Slack/Discord)  
- [ ] Cache Redis para performance
- [ ] Rate limiting para API
- [ ] Deploy automatizado (CI/CD)

## 🤝 **Contribuindo**

1. Fork o projeto
2. Crie uma branch: `git checkout -b feature/nova-funcionalidade`
3. Commit suas mudanças: `git commit -m 'Add nova funcionalidade'`
4. Push para a branch: `git push origin feature/nova-funcionalidade`
5. Abra um Pull Request

## 📄 **Licença**

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

---

**FII Scraper API v2.0** - Scraping automático e inteligente de FIIs brasileiros com configuração centralizada 🚀
