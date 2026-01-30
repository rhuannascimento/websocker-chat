# Relatório Técnico: Implementação de Chat Seguro com Criptografia Ponta a Ponta (E2E)

**Disciplina:** Segurança em Sistemas de Computação  
**Projeto:** Secure Chat - E2E Encryption Proof of Concept  
**Data:** 30 de janeiro de 2026

---

## 1. Introdução

Este relatório documenta a implementação de um sistema de chat seguro desenvolvido como prova de conceito para demonstrar princípios de confidencialidade, integridade e autenticidade em comunicações de rede.

O objetivo principal foi criar uma aplicação de mensagens onde o servidor atua apenas como um *relay* (repassador) sem capacidade de decifrar o conteúdo das mensagens, garantindo criptografia ponta a ponta (E2E). Além disso, foi implementado um cenário de ataque *Man-in-the-Middle* (MitM) para validar a robustez da criptografia contra interceptações passivas.

## 2. Tecnologias e Algoritmos

A segurança da aplicação baseia-se em um esquema híbrido de criptografia, combinando troca de chaves assimétrica com cifragem simétrica:

### 2.1. Troca de Chaves: ECDH (Elliptic Curve Diffie-Hellman)
Para estabelecer um segredo compartilhado em um canal inseguro sem a necessidade de transmitir a chave privada, utilizou-se o protocolo ECDH sobre uma curva elíptica.

- **Justificativa:** Curvas elípticas oferecem segurança equivalente ao RSA com chaves significativamente menores, resultando em menor custo computacional e de rede durante o *handshake*.
- **Funcionamento:**
  1. Cliente A e Cliente B geram pares de chaves efêmeras (Pública/Privada).
  2. As chaves públicas são trocadas através do servidor.
  3. Cada cliente deriva o segredo compartilhado (Shared Secret) usando sua chave privada e a chave pública do par.

### 2.2. Derivação de Chave: HKDF (HMAC-based Key Derivation Function)
O segredo compartilhado bruto resultante do ECDH não é adequado para uso direto como chave de cifragem. Utilizou-se o **HKDF** com algoritmo de hash **SHA-256** para derivar uma chave simétrica criptograficamente forte e uniforme de 32 bytes.

### 2.3. Cifragem Simétrica: AES-GCM
Para a troca de mensagens de texto, adotou-se o algoritmo **AES** (Advanced Encryption Standard) no modo **GCM** (Galois/Counter Mode).

- **Confidencialidade:** Garante que apenas os detentores da chave simétrica possam ler a mensagem.
- **Integridade e Autenticidade:** O modo GCM produz uma *Authentication Tag*. Se a mensagem for adulterada no trânsito (por exemplo, pelo servidor ou um atacante), a verificação da tag falhará e o cliente rejeitará a mensagem.
- **Nonce:** Um número único é gerado para cada mensagem para prevenir ataques de repetição (*Replay Attacks*) e garantir que a mesma mensagem cifrada duas vezes produza textos cifrados diferentes.

## 3. Arquitetura de Software

O projeto segue os princípios da **Clean Architecture** para desacoplar a lógica de criptografia da infraestrutura de rede, facilitando testes e manutenção.

### 3.1. Estrutura de Pastas
- **`src/domain`**: Contém as entidades principais (`Message`, `User`) e interfaces (`ICryptoService`). Esta camada não depende de bibliotecas externas.
- **`src/application`**: Contém a lógica de negócio, principalmente o `CryptoService`, responsável por orquestrar a geração de chaves, derivação e cifragem/decifragem.
- **`src/infrastructure`**:
  - **`network/`**: Implementação do WebSocket Server (`server.py`).
  - **`cli/`**: Interface de linha de comando para o cliente (`client.py`).

### 3.2. Fluxo de Execução
1. **Conexão:** O cliente se conecta ao servidor via WebSocket.
2. **Registro:** O cliente envia sua Chave Pública ECDH para o servidor.
3. **Handshake:** Ao selecionar um destinatário, o cliente solicita a Chave Pública dele ao servidor e deriva a Chave Simétrica localmente.
4. **Comunicação:** As mensagens digitadas são cifradas com AES-GCM e enviadas ao servidor, que as encaminha ao destinatário sem ter acesso ao conteúdo (apenas metadados de roteamento).

## 4. Análise de Segurança e Ameaças (MitM)

Foi desenvolvido um componente `mitm_proxy.py` para simular um atacante posicionado na rede entre os clientes e o servidor.

### 4.1. Cenário de Teste
- Uma instância do MitM escuta na porta `8766` e encaminha tráfego para o servidor real na porta `8765`.
- Um usuário do chat conecta-se na porta do MitM (acreditando ser o servidor legítimo).

### 4.2. Resultados Observados
Ao interceptar o tráfego:
1. **Metadados Visíveis:** O atacante consegue ver quem está falando com quem (ex: `{"type": "message", "to": "Bob", ...}`).
2. **Conteúdo Protegido:** O campo `content` da mensagem trafega como uma string ilegível (ex: bytes codificados em Base64 ou Hex).
3. **Conclusão:** Mesmo interceptando todos os pacotes, o atacante **não consegue recuperar o texto original** sem a chave privada de uma das partes, validando a eficácia da Criptografia E2E.

## 5. Requisitos e Execução

### 5.1. Dependências
- Python 3.9+
- Bibliotecas: `cryptography`, `websockets`

### 5.2. Como reproduzir
Os passos detalhados para execução local e via Docker encontram-se documentados no arquivo `README.md`.

## 6. Conclusão

O projeto atingiu com sucesso o objetivo de implementar um canal de comunicação seguro. A utilização de ECDH para troca de chaves elimina a necessidade de pré-compartilhamento de segredos, enquanto o AES-GCM garante confidencialidade e integridade. A demonstração com o proxy MitM comprova que a arquitetura protege o conteúdo das mensagens contra espionagem na camada de transporte.
