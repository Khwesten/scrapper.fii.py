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

## 🚀 **Início Rápido**

### Pré-requisitos
- Docker & Docker Compose
- Make

### Comandos Essenciais

```bash
# Iniciar ambiente completo
make dev-up

# Verificar saúde do sistema
make health

# Ver status detalhado do banco
make status

# Abrir documentação da API
make docs

# Executar testes E2E
make test-e2e

# Ver logs em tempo real
make dev-logs

# Parar ambiente
make dev-down
```

## 📡 **Endpoints da API**

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/health` | GET | Health check com status de banco e scheduler |
| `/database/status` | GET | Status detalhado do banco e estatísticas |
| `/fiis` | GET | Lista todos os FIIs |
| `/fiis/magic_numbers` | GET | Cálculo de magic numbers |
| `/docs` | GET | Documentação interativa (ReDoc) |

### Exemplos de Uso

```bash
# Health check completo
curl http://localhost:8001/health

# Status do banco
curl http://localhost:8001/database/status

# Listar FIIs
curl http://localhost:8001/fiis

# Magic numbers com investimento de R$ 10.000
curl "http://localhost:8001/fiis/magic_numbers?invested_value=10000"
```

## 📚 **Documentação da API**

A API utiliza **ReDoc** para uma documentação interativa e moderna:

- **URL**: http://localhost:8001/docs
- **Interface**: ReDoc (mais limpa que Swagger)
- **Recursos**: Descrições detalhadas, exemplos, códigos de resposta
- **Organização**: Endpoints agrupados por tags (FIIs, Sistema, Análise, Monitoramento)

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

## 🚀 **Melhorias Implementadas v2.0**

### ✅ Removidas Dependências Obsoletas
- ❌ Rotas `/fiis/scrape` e `/database/seed` (redundantes)
- ❌ Arquivo `scrape.py` (obsoleto)
- ❌ Todas as referências a CSV

### ✅ Scraping Inteligente
- 🌐 Descoberta automática de todos os FIIs disponíveis
- 🔄 Sem listas fixas - usa gateway para listar FIIs
- ⚡ Fallback para FIIs populares em caso de falha

### ✅ Interface de Documentação Melhorada
- 📚 **ReDoc**: Interface moderna e limpa para documentação da API
- 📖 **Documentação Rica**: Descrições detalhadas de todos os endpoints
- 🏷️ **Tags Organizadas**: Endpoints agrupados por funcionalidade
- 💡 **Exemplos Claros**: Exemplos de uso e códigos de resposta

### ✅ Testes E2E Automatizados
- 🧪 Substituiu testes manuais com curl
- ⚡ Execução rápida e confiável
- 📊 Validação completa do sistema

### ✅ Makefile Centralizado
- 🛠️ Todos os comandos Docker centralizados
- ⏱️ Sleeps automáticos otimizados
- 🔄 Comandos simplificados

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

**FII Scraper API v2.0** - Scraping automático e inteligente de FIIs brasileiros 🚀
