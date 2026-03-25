from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from twilio.twiml.messaging_response import MessagingResponse
import os

app = Flask(__name__)

# Configuração do Banco de Dados
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'doacoes.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo do Banco de Dados
class Doacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(50), nullable=False)
    valor = db.Column(db.Float, nullable=False)

with app.app_context():
    db.create_all()

# --- ROTA WEB PARA DOAÇÃO ---
@app.route("/doar", methods=["GET", "POST"])
def pagina_doacao():
    if request.method == "POST":
        nome = request.form.get("nome")
        tel_bruto = request.form.get("telefone")
        valor = request.form.get("valor")

        apenas_numeros = "".join(filter(str.isdigit, tel_bruto))
        if not apenas_numeros.startswith("55"):
            apenas_numeros = "55" + apenas_numeros
        tel_final = f"whatsapp:+{apenas_numeros}"

        nova_doacao = Doacao(nome=nome, telefone=tel_final, valor=float(valor))
        db.session.add(nova_doacao)
        db.session.commit()
        
        return "<h1>Obrigado! ❤️</h1><p>Sua doação foi registrada no sistema.</p><a href='/doar'>Voltar</a>"
    
    return render_template("doar.html")

# --- ROTA DO CHATBOT (WHATSAPP) ---
@app.route("/webhook", methods=["POST"])
def webhook():
    # TRATAMENTO DE ERRO: Verifica se a mensagem existe antes de processar
    raw_body = request.form.get("Body")
    msg = raw_body.strip().lower() if raw_body else ""
    
    remetente = request.form.get("From")
    resp = MessagingResponse()

    # MENU PRINCIPAL
    if msg in ["0", "oi", "ola", "olá", "menu", "voltar"]:
        resp.message(
            "👋 *Bem-vindo ao Núcleo Batuíra*\n\n"
            "Como podemos ajudar hoje?\n\n"
            "1️⃣ *Doações*\n"
            "2️⃣ *Conhecer a ONG*\n"
            "3️⃣ *Contato*\n"
            "4️⃣ *Nossos Projetos*\n\n"
            "👉 _Digite o número da opção desejada._"
        )

    # 1. MENU DE DOAÇÕES
    elif msg == "1":
        resp.message(
            "💳 *Central de Doações*\n\n"
            "5️⃣ *Quero Doar*\n"
            "6️⃣ *Consultar Histórico*\n\n"
            "0️⃣ Voltar ao Menu Principal"
        )

    # 2. CONHECER A ONG
    elif msg == "2":
        resp.message(
            "🏢 *Sobre o Núcleo Batuíra*\n\n"
            "Fundado em 1939, o Núcleo Batuíra é uma organização sem fins lucrativos que promove assistência social e educação em Guarulhos.\n\n"
            "🌐 *Acesse nosso site:* https://nucleobatuira.org.br/\n\n"
            "0️⃣ Voltar ao Menu Principal"
        )

    # 3. CONTATO
    elif msg == "3":
        resp.message(
            "📞 *Informações de Contato*\n\n"
            "📍 *Endereço:*\n"
            "Rua Segundo Tenente Renato Ometi, nº 65, Cumbica\n"
            "Guarulhos / SP\n\n"
            "📧 *E-mail:* contato@nucleobatuira.org.br\n\n"
            "☎️ *Telefones:*\n"
            "+55 (11) 2412-2186\n"
            "+55 (11) 2412-1659\n\n"
            "⏰ *Horário de Atendimento:*\n"
            "Segunda à Sexta-feira: 07:00 às 18:00\n\n"
            "0️⃣ Voltar ao Menu Principal"
        )

    # 4. PROJETOS (SEM NÚMEROS)
    elif msg == "4":
        resp.message(
            "📌 *Nossos Principais Projetos:*\n\n"
            "• *Educação Infantil:* Creches para crianças em período integral.\n"
            "• *Batuíra em Ação:* Cursos profissionalizantes para a comunidade.\n"
            "• *Serviço de Convivência:* Fortalecimento de vínculos familiares.\n"
            "• *Entrega de Alimentos:* Combate à insegurança alimentar.\n"
            "• *Apoio Psicológico:* Atendimento especializado para famílias.\n\n"
            "0️⃣ Voltar ao Menu Principal"
        )

    # 5. LINK PARA DOAR
    elif msg == "5":
        resp.message(
            "💙 *Que alegria contar com você!*\n\n"
            "Acesse o link abaixo para realizar sua doação:\n"
            "https://projeto-ong-batuira.onrender.com/doar\n\n"
            "0️⃣ Voltar ao Menu Principal"
        )

    # 6. CONSULTAR HISTÓRICO
    elif msg == "6":
        minhas_doacoes = Doacao.query.filter_by(telefone=remetente).all()
        if minhas_doacoes:
            relatorio = "📊 *Seu Histórico de Doações:*\n\n"
            total = 0
            for d in minhas_doacoes:
                relatorio += f"✅ R$ {d.valor:.2f}\n"
                total += d.valor
            relatorio += f"\n💰 *Total acumulado: R$ {total:.2f}*"
            relatorio += "\n\nMuito obrigado! ❤️\n\n0️⃣ Voltar ao Menu"
        else:
            relatorio = "❌ Não encontramos doações vinculadas a este número.\n\n0️⃣ Voltar ao Menu"
        resp.message(relatorio)

    # TRATAMENTO PARA MENSAGENS NÃO RECONHECIDAS
    else:
        resp.message("Ops! Não entendi. Digite *0* para ver as opções do Menu.")

    return str(resp)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)