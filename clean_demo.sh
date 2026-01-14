#!/bin/bash

# Cores para output
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${RED}=== Limpando Ambiente do Chat ===${NC}"

# 1. Para e remove containers
echo -e "${YELLOW}[1/2] Parando e removendo containers...${NC}"
docker-compose down --volumes --remove-orphans

# 2. Limpa imagens dangling (opcional, mas bom para economizar espaço)
# echo -e "${YELLOW}[2/2] Limpando imagens não utilizadas...${NC}"
# docker image prune -f

echo -e "${RED}=== Ambiente Limpo! ===${NC}"
