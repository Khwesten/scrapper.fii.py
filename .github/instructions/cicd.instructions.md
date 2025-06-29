---
applyTo: '.github/workflows/*.yml'
---

Regras de ci/cd:
- Utilizamos github actions
- O pipeline deve seguir a seguinte ordem
- job make format(apenas no modo checagem e quee bloqueia os outros jobs, se não passar)
  - job unit tests
  - job integration tests
  - job e2e tests
  - job deploy(ainda não implementado e dependente do resultado dos jobs de tests)
- Utilizamos docker para rodar os testes
- Os jobs são separados em steps que executam pequenos contextos(ex.: setup machine, checkout repo, setup python, cache pip, set env vars...)
