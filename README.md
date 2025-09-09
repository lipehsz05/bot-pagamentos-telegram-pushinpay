<h1 align="center">Bot de Pagamentos Telegram PushinPay 🤖</h1>

<p align="center">
  <b>Automatize o acesso ao seu grupo VIP do Telegram com pagamentos via PIX!</b><br>
  <i>Bot completo, open source, com banco de dados integrado, painel de planos e expulsão automática de usuários expirados.</i>
</p>

---

## 🚀 Sobre o Projeto

O <b>Bot de Pagamentos Telegram PushinPay</b> é um bot de Telegram pronto para uso, que automatiza o acesso a grupos VIP mediante pagamento via PIX (PushinPay). Ele já vem com integração ao banco de dados SQLite para controle de usuários, planos, expiração automática e muito mais!

- <img src="https://media.licdn.com/dms/image/v2/D4D0BAQGMvyp3vXJOBw/company-logo_200_200/company-logo_200_200/0/1721991888260/pushin_pay_logo?e=2147483647&v=beta&t=eTbieyI-wGHv93hNKomv0nVLE_kcmhBl8LDKB762QCs" 
       width="16" height="16" 
       style="vertical-align: middle; margin-left: 4px; margin-right: 4px;"/>
- 🔒 Controle de acesso automático ao grupo
- 🗃️ Banco de dados SQLite integrado
- 📅 Expiração automática de assinaturas
- 👤 Painel de planos e suporte
- 📸 Envio de imagem de boas-vindas (personalizável)
- 🚪 Expulsão automática do grupo após expiração da assinatura
- Código aberto para a comunidade!

---

## 🛠️ Como Usar

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/lipehsz05/bot-pagamentos-telegram-pushinpay.git
   cd bot-pagamentos-telegram-pushinpay
   ```

2. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure o arquivo `senhas.py`:**
   - Insira seu token do bot, ID do grupo, token PushinPay, ID do dono e link de suporte.
   - Exemplo:
     ```python
     TELEGRAM_BOT_TOKEN = 'Seu Token'
     GRUPO_ID = 'Seu ID do grupo'
     PUSHINPAY_TOKEN = 'Seu Token PushinPay'
     ID_DONO = 'Seu ID'
     LINK_SUPORTE = 'Seu link de suporte'
     ```

4. **Adicione sua imagem de boas-vindas:**
   - Coloque uma imagem de boas-vindas na raiz do projeto com o nome <b>inicio.png</b>.
   - <b>Importante:</b> Essa imagem é apenas um exemplo! Substitua por uma imagem personalizada para o seu grupo. Ela será enviada automaticamente para cada novo usuário.

5. **Execute o bot:**
   ```bash
   python main.py
   ```

---

## 🧑‍💻 Funcionalidades

- <b>Banco de dados SQLite</b> para armazenar usuários, planos e datas de expiração.
- <b>Expulsão automática</b> de usuários com assinatura expirada (o bot remove do grupo automaticamente!).
- <b>Botões interativos</b> para planos, suporte e acesso ao grupo.
- <b>Notificações automáticas</b> para o dono do bot a cada venda.
- <b>Fácil personalização</b> de mensagens, planos e valores.

---

## 📦 Estrutura do Projeto

```
├── main.py           # Código principal do bot
├── senhas.py         # Tokens, IDs e configurações sensíveis
├── usuarios.db       # Banco de dados SQLite (gerado automaticamente)
├── inicio.png        # Imagem de boas-vindas (adicione a sua!)
├── requirements.txt  # Dependências Python
```

---

## 🌟 Contribua!

Este projeto é <b>open source</b>! Sinta-se livre para abrir issues, enviar pull requests ou sugerir melhorias.

💡 <b>Novas ideias e implementações são muito bem-vindas!</b>

---

## 📄 Licença

Este projeto está licenciado sob a licença MIT. Você pode usar, modificar, distribuir e até vender este código, desde que mantenha os créditos ao autor original.

> **Atenção:** O uso deste bot é de sua total responsabilidade. Não me responsabilizo por eventuais problemas, prejuízos, banimentos ou uso indevido. Use com consciência!

Se for utilizar comercialmente, mantenha os créditos e, se possível, divulgue o projeto para ajudar a comunidade!

---

## 👤 Contato & Redes

<div align="center"> 
  <a href="https://instagram.com/lipehsz" target="_blank" style="text-decoration:none;">
    <img src="https://img.shields.io/badge/-Instagram-%23E4405F?style=for-the-badge&logo=instagram&logoColor=white"/>
  </a>
  <a href="mailto:ftsu2570@gmail.com" style="text-decoration:none;">
    <img src="https://img.shields.io/badge/-Gmail-%23333?style=for-the-badge&logo=gmail&logoColor=white"/>
  </a>
  <a href="https://www.linkedin.com/in/lipehsz" target="_blank" style="text-decoration:none;">
    <img src="https://img.shields.io/badge/-LinkedIn-%230077B5?style=for-the-badge&logo=linkedin&logoColor=white"/>
  </a> 
</div>

---

<p align="center">
  <b>Feito com 💙 para a comunidade Python & Telegram!</b><br>
  <i>Deixe sua estrela ⭐ e compartilhe!</i>
</p>
