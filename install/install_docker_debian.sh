#!/bin/bash
# Script de instalação do Docker Engine para Debian com verificação prévia

set -e # Interrompe o script se ocorrer algum erro

echo "=== Verificando instalação atual do Docker ==="
if command -v docker &> /dev/null && docker compose version &> /dev/null; then
    echo "✅ Uma versão moderna do Docker com o plugin Compose V2 já está instalada!"
    docker --version
    docker compose version
    echo "Nenhuma ação necessária. Encerrando o script."
    exit 0
else
    echo "⚠️ Docker moderno não encontrado ou versão antiga detectada."
    echo "Iniciando processo de limpeza e instalação..."
fi

echo "=== Desinstalando versões antigas do Docker e Docker Compose ==="
for pkg in docker.io docker-doc docker-compose podman-docker containerd runc; do 
    sudo apt-get remove -y $pkg || true
done
# Remove o binário antigo do docker-compose caso tenha sido instalado manualmente
sudo rm -f /usr/local/bin/docker-compose

echo "=== Atualizando pacotes e instalando dependências ==="
sudo apt-get update
sudo apt-get install -y ca-certificates curl

echo "=== Adicionando a chave GPG oficial do Docker (Debian) ==="
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

echo "=== Adicionando o repositório do Docker ==="
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

echo "=== Instalando o Docker Engine e o plugin do Docker Compose ==="
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

echo "=== Instalação concluída com sucesso no Debian! ==="
sudo docker --version
sudo docker compose version