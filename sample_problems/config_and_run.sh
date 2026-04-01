#!/bin/bash

# 1. Verifica se o usuário passou o argumento (o número do caso)
if [ -z "$1" ]; then
  echo "Erro: Você precisa informar o número do caso."
  echo "Uso correto: bash config_and_run.sh <numero_do_caso>"
  exit 1
fi

# 2. Prepara o ambiente
mkdir -p logs
rm -rf --interactive=never wf_solver
cp -r ../wf_solver .

# 3. Executa o docker compose
# Se você realmente precisa rodar com sudo, a forma correta de passar a variável é usando o 'env'
sudo env CASE=$1 docker compose up --build 

# 4. Limpa o contexto de build
rm -rf wf_solver

# 5. Mostra o resultado, verificando se o arquivo realmente foi gerado
if [ -f "logs/case$1.txt" ]; then
  echo "--- Resultados do Caso $1 ---"
  cat logs/case$1.txt
else
  echo "Erro: O arquivo logs/case$1.txt não foi gerado. Verifique os logs do Docker."
fi

rm -rf logs/*