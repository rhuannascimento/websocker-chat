# Secure Chat - E2E Encryption Proof of Concept

Este projeto implementa um chat seguro com criptografia ponta a ponta (E2E) para a disciplina de Segurança em Sistemas de Computação.

## Arquitetura

O projeto segue os princípios de Clean Architecture:

- **src/domain**: Entidades e interfaces fundamentais.
- **src/application**: Regras de negócio (Criptografia, Handshake).
- **src/infrastructure**: Implementações concretas (WebSockets, Console UI).

## Componentes

1.  **Server**: Um relay simples de mensagens (não sabe ler o conteúdo).
2.  **Client**: Realiza o handshake ECDH e troca mensagens AES-GCM.
3.  **MitM (Eve)**: Um proxy que intercepta a conexão para provar a segurança.

## Como rodar (Localmente)

1.  **Instalar dependências**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Iniciar o Servidor**:
    ```bash
    python src/infrastructure/network/server.py
    ```

3.  **Iniciar Clientes (em terminais separados)**:
    ```bash
    python src/infrastructure/cli/client.py Alice ws://localhost:8765
    python src/infrastructure/cli/client.py Bob ws://localhost:8765
    ```

## Como rodar (Docker)

1.  **Subir a infraestrutura (Server + MitM)**:
    ```bash
    docker-compose up -d server mitm
    ```

2.  **Rodar Clientes Interativos**:
    *   Terminal 1 (Alice):
        ```bash
        docker-compose run --rm client_alice
        ```
    *   Terminal 2 (Bob):
        ```bash
        docker-compose run --rm client_bob
        ```

## Prova de Conceito (MitM Attack)

Para testar a interceptação:

1.  Rode o MitM (já sobe com o docker-compose ou `python mitm_attack/mitm_proxy.py`).
2.  Conecte os clientes na porta do MitM (**8766**) em vez da porta do servidor (8765).
    ```bash
    # Exemplo local
    python src/infrastructure/cli/client.py EveVictim ws://localhost:8766
    ```
3.  Observe os logs do MitM. Você verá o tráfego passando, mas o conteúdo das mensagens de texto estará ilegível (criptografado), provando a segurança E2E.
