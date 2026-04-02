# Modelagem e Otimização do Aprendizado Federado para Justiça do Nível de Energia em Redes Sem Fio

Manual de artefatos para o código documentado referente ao artigo aceito no SBRC 2026

## Selos Considerados

Os autores reivindicam os seguintes selos científicos para este artefato:
* Artefatos Disponíveis (SeloD);
* Artefatos Funcionais (SeloF);
* Artefatos Sustentáveis (SeloS);
* Experimentos Reprodutíveis (SeloR);

## Requisitos 

* Sistema Operacional: Debian 12 ou Ubuntu 24
* CPU mínima: 4 núcleos. 2 GHz
* RAM mínima: 4 GB
* Espaço em disco mínimo usado: ...GB

## Dependências

Caso ainda não tenha instalado o Docker Engine (com o Docker Compose), clique [aqui](https://docs.docker.com/engine/install/) para instalar. A versão mínima exigida é a 29.1.3.

## Preocupações com segurança

A execução dos experimentos em contêineres **não apresenta riscos de segurança conhecidos**. O uso do sudo é exigido pelo pelo Docker durante os testes. Os comandos Docker são executados por padrão com sudo, mas é possível que o usuário possua uma instalação do Docker configurada para execução de comandos sem sudo.

## Organziação dos diretórios

* `wf_solver`: biblioteca Python instalável com PIP que implementa a solução do problema de otimização proposto no artigo.
* `sample_problems`: soluciona alguns problemas de otimziação com parâmetros pré-definidos e ajustáveis pelo desenvolvedor, auxiliando na validação e na criação de intuição sobre o problema, conforme será discutido na [Parte 1](#parte-1---problemas-de-exemplo) deste tutorial
* `random_problems`: cria problemas aleatórios e os resolve, gerando métricas análogas às que foram incluídas no Experimento 1 descrito no artigo, mas em menor escala, conforme  será discutido na [Parte 2](#parte-2---problemas-aleatórios) deste tutorial
* `results_random_problems`: plota as figuras do artigo, de acordo com métricas printadas na execução do `random_problems`, conforme será discutido na [Parte 3](#parte-3---resultados-dos-problemas-aleatórios) deste tutorial
* `data`: geração dos dados para o treinamento de aprendizado federado com MNIST, conforme será discutido na [Parte 4](#parte-4---geração-dos-dados-para-o-fl) deste tutorial
* `flower`: executa treinamentos do Flower com a proposta do artigo, gerando resultados análogos, mas em menor escala, conforme  será discutido na [Parte 5](#parte-5---integração-com-o-flower) deste tutorial
* `results_flower`: plota as figuras do artigo, de acordo com métricas printadas na execução do `flower`, conforme será discutido na [Parte 6](#parte-6---resultados-da-integração-com-o-flower) deste tutorial

 ## Parte 1 - Problemas de exemplo

Acesse o diretório `sample_problems`

```bash
cd sample_problems
```

Dentro da pasta `sample_problems/cases`, há alguns problemas de otimização pré-definidos, com parâmetros especificados em arquivos JSON. Caso um parâmetros de um cliente não seja definido, o valor padrão será utilizado. Os valores padrões são os seguintes:

```python
{
    "num_min_epochs": 60,   # Mínimo de épocas distribuídas entre os clientes
    "time_budget": 60,      # Tempo máximo da rodada
    "gamma_i": 1e-28,       # Parâmetro da CPU (capacitância efetiva)
    "ui": 4 * 8 / 10,       # Tempo de upload
    "di": 4 * 8 / 15,       # Tempo de download
    "batches": 100,         # Batches do cliente
    "ci": 0.015 * 1e9,      # Ciclos por batch
    "fi": 1e9,              # Frequência da CPU
    "battery_mAh": 3000,    # Capacidade da bateria do cliente
    "starting_soc": 0.7,    # Porcentagem inicial de bateria do cliente
    "charging_power": 0     # Potência do carregador
}
```

Execute o caso 2 como exemplo:

```bash
bash config_and_run.sh 2
```

**Resumo** dos logs esperados no terminal:

```bash
---------------
Client 1
Num epochs: 27.33220709443426
Reduced num epochs: 8.66779290556574
Utility: 2.0187219910308795e-06
Time: 1351.386216246371 s
Energy before: 279720.0 J
Energy consumed by training: 4.099831064165139 J
Energy consumed base: 5.51448 J
Energy recharged: 0 J
Total energy variation: -9.61431106416514 J
Energy after: 279710.3856889358 J
---------------
Client 2
Num epochs: 31.333896452782877
Reduced num epochs: 4.666103547217123
Utility: 1.4819182654137439e-06
Time: 1340.66308656708 s
Energy before: 205128.0 J
Energy consumed by training: 4.700084467917431 J
Energy consumed base: 4.043951999999999 J
Energy recharged: 0 J
Total energy variation: -8.74403646791743 J
Energy after: 205119.25596353208 J
---------------
Client 3
Num epochs: 31.333896452782877
Reduced num epochs: 4.666103547217123
Utility: 2.593443200072707e-06
Time: 394.47592719431907 s
Energy before: 117216.0 J
Energy consumed by training: 4.700084467917431 J
Energy consumed base: 4.043951999999999 J
Energy recharged: 0 J
Total energy variation: -8.74403646791743 J
Energy after: 117207.25596353208 J
TOTAL ENERGY: 602036.8976159999
INITIAL ENERGY: 602064.0
TOTAL FAIRNESS: 15.827669523034732
ENERGY GAP TO MAX: 0.2825473198725848
ENERGY STANDARD DEVIATION: 202065.99652881935
ELAPSED TIME: 1.3113021850585938e-05
```

Para finalizar, volte para a raiz do repositório: `cd ..`

 ## Parte 2 - Problemas aleatórios

Execute os seguintes comandos

```bash
cd sample_problems
bash config_and_run.sh
```

A máquina irá executar apenas 5 repetições de um problema de otimização. O problema em questão possui parâmetros gerados aleatoriamente. O objetivo é apenas **ilustrar** como os resultados do artigo foram gerados.

Resumo dos logs esperados (apenas últimas linhas):

```bash
...
-----------------------------
Water-Filling
Optimization time = 0.0006668567657470703 +- 0.00022875607141030073s
Round time = 186.26949230088786 +- 64.2352658267825s
Energy = 65344.32700645474 +- 6049.5851125484505s
Energy drop factor = 0.01773589863076208 +- 0.001905005133131351s
Utility = 95.7056272200659 +- 0.8503643232312937s
Gap = 0.3764027472198499 +- 0.04269636171085652s
Energy std. dev. = 10817.802529960314 +- 771.8191591187751s
-----------------------------
Equal number of rounds
Execution time = 4.711151123046875e-05 +- 4.046062810028164e-06s
Round time = 197.95517744766795 +- 64.23538452282517s
Energy = 65306.27273220001 +- 6049.897633635618s
Energy drop factor = 0.018310633116295792 +- 0.0018599255948579143s
Utility = 95.64558593545496 +- 0.8534294197512975s
Gap = 0.3688981733895055 +- 0.04253268502596688s
Energy std. dev. = 11265.348116823223 +- 798.8560930979041s
-----------------------------
Proportional to initial energy
Execution time = 5.278587341308594e-05 +- 3.2537010806681493e-06s
Round time = 213.42836710860556 +- 63.541145185433294s
Energy = 65302.15650857845 +- 6038.237258067017s
Energy drop factor = 0.018363790734280606 +- 0.0016715601488812761s
Utility = 95.67112320958726 +- 0.8504743438504588s
Gap = 0.36428339882233485 +- 0.041707144737293256s
Energy std. dev. = 11059.317083351216 +- 792.8897426667343s
-----------------------------
Proportional to device efficiency
Execution time = 5.7649612426757815e-05 +- 1.8886061041282134e-06s
Round time = 225.93765223650195 +- 63.938271065948285srepetição
Energy = 65316.85825937967 +- 6052.531772450024s
Energy drop factor = 0.01815281831592186 +- 0.0018861655360560862s
Utility = 95.64560283425389 +- 0.8514220924603362s
Gap = 0.3693496345155407 +- 0.043304968694702656s
Energy std. dev. = 11282.148916719874 +- 806.8161965918118s
```

Para finalizar, volte para a raiz do repositório: `cd ..`


 ## Parte 3 - Resultados dos problemas aleatórios

```bash
cd results_random_problems
bash config_and_run.sh
```
Intel(R) Xeon(R) Gold 5416SIntel(R) Xeon(R) Gold 5416S
Este comando irá apenas gerar no diretório `results_random_problems/figures` 4 arquivos de imagem (`.png`) com os resultados do Experimento 1 do artigo. Apesar desses gráficos do artigo terem sido obtidos utilizando os scripts em `random_problems` **neste tutorial, apenas poucas rodadas foram executadas**. Volte para a raiz do repositório: `cd ..`

 ## Parte 4 - Geração dos dados para o FL

Acesse o diretório `cd data` 

Dentro deste diretório, há um arquivo chamado `config.ini` que define como o conjunto de dados MNIST será particionado entre N clientes do aprendizado federado. Ademais, o arquivo também define a fração de treino e teste e o tamanho do batch. Para reproduzir os experimentos do artigo, mantenha as configurações padrão.

Execute `bash config_and_run.sh`

Este script cria um diretório chamado `MNIST` com os dados com a seguinte estrutura:

```bash
.
├── info
├── private_dataloaders_clear
│   ├── client_0_testloader.pth
│   ├── client_0_trainloader.pth
│   ├── client_1_testloader.pth
│   ├── client_1_trainloader.pth
│   ├── client_2_testloader.pth
│   ├── client_2_trainloader.pth
│   ├── client_3_testloader.pth
│   ├── client_3_trainloader.pth
│   ├── client_4_testloader.pth
│   ├── client_4_trainloader.pth
│   ├── client_5_testloader.pth
│   ├── client_5_trainloader.pth
│   ├── client_6_testloader.pth
│   ├── client_6_trainloader.pth
│   ├── client_7_testloader.pth
│   ├── client_7_trainloader.pth
│   ├── client_8_testloader.pth
│   ├── client_8_trainloader.pth
│   ├── client_9_testloader.pth
│   └── client_9_trainloader.pth
├── public_dataloaders
│   └── server_testloader.pth
└── raw
    ├── t10k-images-idx3-ubyte
    ├── t10k-images-idx3-ubyte.gz
    ├── t10k-labels-idx1-ubyte
    ├── t10k-labels-idx1-ubyte.gz
    ├── train-images-idx3-ubyte
    ├── train-images-idx3-ubyte.gz
    ├── train-labels-idx1-ubyte
    └── train-labels-idx1-ubyte.gz
```

O arquivo `client_X_trainloader.pth` contém os batches usados para o treinamento pelo cliente identificado pelo número `X` 

A próxima etapa utilizará esses dados. Execute `cd ..` para voltar à raiz do repositório 

 ## Parte 5 - Integração com o Flower

Esta etapa utiliza os dados gerados na etapa anterior

```bash
cd flower
bash config_and_run.sh 0 100
```

Esse script irá criar containeres na máquina para executar o aprendizado federado com dez clientes e um servidor. O servidor aloca 100 épocas de forma variável entre os 10 clientes de forma a maximizar a justiça no nível de energia ao final de cada rodada. São gerados arquivos de log em `logs/fixed_0_variable_100`, que serão usados na próxima parte. 

O experimento será repetido 4 vezes para garantir significância estatística. No artigo, o experimento é repetido mais vezes. Entretanto, o objetivo deste artefato é apenas demonstrar a funcionalidade. Se quiser mudar o número de rodadas, basta passar um terceiro argumento (opicional) para o comando.

O experimento utiliza apenas 5 rodadas globais para agilizar o processo. A learning rate é maior para garantir a convergência em menos rodadas. Dessa forma, é compreensível que os resultados obtidos aqui **não serão idênticos aos do artigo**, mas podem ser ajustados para execuções mais longas, se necessário. 

Após o treinamento anterior encerrar, repita o procedimento com o segunte comando:

```bash
bash config_and_run.sh 100 0
```

Nesse caso, o servidor distribui igualmente 100 épocas entre os clientes, de forma que cada um irá treinar por exatas 10 épocas. Os logs, nesse caso, serão gerados em `logs/fixed_100_variable_0`.

Após o treinamento anterior encerrar, repita o procedimento com o segunte comando:

```bash
bash config_and_run.sh 50 50
```

Nesse caso, 50 épocas são divididas igualmente e outras 50 são alcoadas pelo algoritmo de otimização do servidor. Cada cliente treina por 5+x épocas, onde x é variável, gerando logs em `logs/fixed_50_variable_50`.

Fim da parte 5. `cd ..`

 ## Parte 6 - Resultados da integração com o Flower

Acesse `cd results_flower` e execute `bash config_and_run.sh`. Este script pega os logs gerados na parte 5 e gera gráficos similares aos do artigo no diretório `figures`

Claro que os resultados serão diferentes pelo fato de que o treinamento foi feito com menos rodadas globais, além de que foram feitas menos repetições, modificando a significância estatística.
