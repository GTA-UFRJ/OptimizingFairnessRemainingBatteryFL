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


 ## Parte 2 - Problemas aleatórios


 ## Parte 3 - Resultados dos problemas aleatórios


 ## Parte 4 - Geração dos dados para o FL


 ## Parte 5 - Integração com o Flower


 ## Parte 6 - Resultados da integração com o Flower
