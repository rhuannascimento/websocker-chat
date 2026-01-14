#!/bin/bash

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Iniciando Cenário de Chat Seguro com MitM ===${NC}"

# 1. Build e Start da Infraestrutura (Server + MitM)
echo -e "${GREEN}[1/4] Subindo Servidor e Proxy MitM...${NC}"
docker-compose down
docker-compose build
docker-compose up -d server mitm

# Aguarda um pouco para garantir que os serviços subiram
sleep 3

# 2. Abre terminal para logs do MitM
echo -e "${GREEN}[2/4] Abrindo logs do MitM (Atacante)...${NC}"
osascript -e 'tell application "Terminal" to do script "cd \"'$(pwd)'\" && echo \"=== LOGS DO ATACANTE (MitM) ===\" && docker-compose logs -f mitm"'

# 3. Abre terminal para Alice
echo -e "${GREEN}[3/4] Iniciando Cliente Alice (Vítima 1)...${NC}"
osascript -e 'tell application "Terminal" to do script "cd \"'$(pwd)'\" && echo \"=== CLIENTE ALICE ===\" && docker-compose run --rm client_alice python src/infrastructure/cli/client.py Alice ws://mitm:8766"'

# 4. Abre terminal para Bob
echo -e "${GREEN}[4/4] Iniciando Cliente Bob (Vítima 2)...${NC}"
osascript -e 'tell application "Terminal" to do script "cd \"'$(pwd)'\" && echo \"=== CLIENTE BOB ===\" && docker-compose run --rm client_bob python src/infrastructure/cli/client.py Bob ws://mitm:8766"'

echo -e "${BLUE}=== Tudo pronto! Verifique as novas janelas do Terminal. ===${NC}"
