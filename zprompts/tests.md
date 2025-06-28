Regras de testes:
- Testes com Pytest na pasta test
- Testes escritos com estrutura de AAA(arrange, act, assert)
- Testes com mock, usam MagicMocks(spec=[class])
- Os arquivos de testes respectivo ao que testa, deve seguir a mesma estrutura de pastas(se a classe testada é um gateway, no teste, deveria estar na mesma estrutura de organização estando dentro da pasta gateway)
- Os arquivos de testes devem ser estruturados como classes não como funções soltas
- Quando todas as alterações tiverem sido aplicadas, rode o comando make relativo aos testes alterados
- Testes integrados devem testar integrado apenas o banco(dynamo), todo o resto deve ser mockado usando requests-mock ou MagicMock(spec=[class])