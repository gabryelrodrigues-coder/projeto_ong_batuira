from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import os

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():

    msg = request.form.get("Body").strip().lower()
    resp = MessagingResponse()

    # MENU PRINCIPAL (quando digita 0 ou qualquer coisa desconhecida)
    if msg == "0":
        resp.message(
            "👋 *Bem-vindo à ONG*\n\n"
            "Escolha uma opção:\n\n"
            "1️⃣ Doações\n"
            "2️⃣ Conhecer a ONG\n"
            "3️⃣ Falar com um responsável\n"
            "4️⃣ Projetos"
        )

    # MENU DOAÇÕES
    elif msg == "1":
        resp.message(
            "💳 *Doações*\n\n"
            "Escolha uma opção:\n\n"
            "1️⃣ Fazer uma doação\n"
            "2️⃣ Consultar doações\n\n"
            "Digite: doar ou consultar"
        )

    # FAZER DOAÇÃO
    elif msg == "doar":
        resp.message(
            "💙 *Fazer Doação*\n\n"
            "Acesse o link abaixo:\n"
            "https://gabryelrodrigues-coder.github.io/projeto_ChatBot/\n\n"
            "Obrigado por ajudar ❤️\n\n"
            "Digite 0 para voltar"
        )

    # CONSULTAR DOAÇÕES
    elif msg == "consultar":
        resp.message(
            "📊 *Consulta de Doações*\n\n"
            "Entre em contato com a ONG para verificar suas doações.\n\n"
            "Digite 0 para voltar"
        )

    # SOBRE A ONG
    elif msg == "2":
        resp.message(
            "🏢 *Sobre a ONG*\n\n"
            "Somos uma organização sem fins lucrativos que ajuda pessoas em situação de vulnerabilidade.\n\n"
            "Acesse nosso site:\n"
            "https://gabryelrodrigues-coder.github.io/projeto_ChatBot/\n\n"
            "Digite 0 para voltar"
        )

    # CONTATO
    elif msg == "3":
        resp.message(
            "📞 *Contato*\n\n"
            "📍 Rua Segundo Tenente Renato Ometi, nº 65 – Cumbica\n"
            "📧 contato@nucleobatuira.org.br\n"
            "📞 (11) 2412-2186 / (11) 2412-1659\n"
            "🕒 Seg a Sex: 07h às 18h\n\n"
            "Digite 0 para voltar"
        )

    # PROJETOS
    elif msg == "4":
        resp.message(
            "📌 *Projetos*\n\n"
            "• Apoio Educacional\n"
            "• Alimentação Solidária\n"
            "• Apoio às Famílias\n"
            "• Cursos Profissionalizantes\n"
            "• Ações de Saúde\n\n"
            "Digite 0 para voltar"
        )

    # QUALQUER OUTRA COISA → MOSTRA MENU
    else:
        resp.message(
            "👋 *Bem-vindo à ONG*\n\n"
            "Escolha uma opção:\n\n"
            "1️⃣ Doações\n"
            "2️⃣ Conhecer a ONG\n"
            "3️⃣ Falar com um responsável\n"
            "4️⃣ Projetos\n\n"
            "Digite o número da opção"
        )

    return str(resp)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))