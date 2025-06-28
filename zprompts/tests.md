Regras de testes:
- Testes com Pytest na pasta test
- Testes escritos com estrutura de AAA(arrange, act, assert)
- Testes com mock, usam MagicMocks(spec=[class])
- Estrutura de pastas dos arquivos de testes, devem ser análogos as da classes testadas(se a classe testada é um gateway, o teste deveria estar na mesma estrutura de organização dentro da pasta gateway)
- Os arquivos de testes devem ser estruturados como classes não como métodos/funções soltas
- Quando todas as alterações tiverem sido aplicadas, rode o comando make relativo aos testes alterados
- Testes integrados devem testar integrado apenas o banco(dynamo), todo o resto deve ser mockado usando requests-mock ou MagicMock(spec=[class])
- Tests e2e rodam integrados com o banco(dynamo) e a aplicação(fastapi)