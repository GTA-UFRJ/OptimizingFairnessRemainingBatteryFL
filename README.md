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
* CPU mínima: 4 núcleos. ... GHz
* RAM mínima: 4GB
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

Logs esperados no terminal:


Para finalizar, volte para a raiz do repositório: `cd ..`

 ## Parte 2 - Problemas aleatórios

Execute os seguintes comandos

```bash
cd sample_problems
bash config_and_run.sh
```

A máquina irá executar apenas 5 repetições de um problema de otimização. O problema em questão possui parâmetros gerados aleatoriamente. O objetivo é apenas **ilustrar** como os resultados do artigo foram gerados.

Nos logs esperados, é possível observar parâmetros importantes de cada repetição:

Para finalizar, volte para a raiz do repositório: `cd ..`


 ## Parte 3 - Resultados dos problemas aleatórios

```bash
cd results_random_problems
bash config_and_run.sh
```

Este comando irá apenas gerar no diretório `results_random_problems/figures` arquivos de imagem (`.png`) com os resultados do Experimento 1 do artigo. Apesar desses gráficos do artigo terem sido obtidos utilizando os scripts em `random_problems` **neste tutorial, apenas poucas rodadas foram executadas**. Volte para a raiz do repositório: `cd ..`

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
