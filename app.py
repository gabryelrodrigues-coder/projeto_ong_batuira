from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from twilio.twiml.messaging_response import MessagingResponse
import os

app = Flask(__name__)

# Configuração do Banco de Dados
# O arquivo 'doacoes.db' será criado automaticamente na pasta do projeto
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'doacoes.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo do Banco de Dados
class Doacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(50), nullable=False) # Formato whatsapp:+55...
    valor = db.Column(db.Float, nullable=False)

# Cria o banco de dados
with app.app_context():
    db.create_all()

# --- ROTA WEB PARA DOAÇÃO ---
@app.route("/doar", methods=["GET", "POST"])
def pagina_doacao():
    if request.method == "POST":
        nome = request.form.get("nome")
        tel_bruto = request.form.get("telefone")
        valor = request.form.get("valor")

        # Limpeza do telefone para garantir o padrão do Twilio
        apenas_numeros = "".join(filter(str.isdigit, tel_bruto))
        if not apenas_numeros.startswith("55"):
            apenas_numeros = "55" + apenas_numeros
        tel_final = f"whatsapp:+{apenas_numeros}"

        # Salva no banco
        nova_doacao = Doacao(nome=nome, telefone=tel_final, valor=float(valor))
        db.session.add(nova_doacao)
        db.session.commit()
        
        return "<h1>Obrigado! ❤️</h1><p>Sua doação foi registrada. Digite 'consultar' no nosso WhatsApp para ver seu histórico.</p><a href='/doar'>Voltar</a>"
    
    return render_template("doar.html")

# --- ROTA DO CHATBOT (WHATSAPP) ---
@app.route("/webhook", methods=["POST"])
def webhook():
    msg = request.form.get("Body").strip().lower()
    remetente = request.form.get("From") # O número de quem enviou a mensagem
    resp = MessagingResponse()

    if msg in ["0", "oi", "ola", "olá"]:
        resp.message(
            "👋 *Bem-vindo à ONG*\n\n"
            "Escolha uma opção:\n"
            "1️⃣ Doações\n"
            "2️⃣ Conhecer a ONG\n"
            "3️⃣ Contato\n"
            "4️⃣ Projetos"
        )

    elif msg == "1":
        resp.message(
            "💳 *Menu de Doações*\n\n"
            "• Digite *doar* para receber o link.\n"
            "• Digite *consultar* para ver seu histórico."
        )

    elif msg == "doar":
        # Substitua pelo link real do seu site quando estiver online
        resp.message("💙 Acesse o link para doar:\nhttp://localhost:5000/doar")

    elif msg == "consultar":
        # Busca todas as doações desse número no banco
        minhas_doacoes = Doacao.query.filter_by(telefone=remetente).all()
        
        if minhas_doacoes:
            relatorio = "📊 *Seu Histórico de Doações:*\n\n"
            total = 0
            for d in minhas_doacoes:
                relatorio += f"✅ R$ {d.valor:.2f}\n"
                total += d.valor
            relatorio += f"\n💰 *Total doado: R$ {total:.2f}*"
            relatorio += "\n\nMuito obrigado por transformar vidas! ❤️"
        else:
            relatorio = "❌ Não encontramos doações vinculadas ao seu número.\n\n_Dica: No formulário, use o número que você usa no WhatsApp._"
        
        resp.message(relatorio)

    elif msg == "2":
        resp.message("🏢 *Sobre nós*\nSomos uma ONG dedicada a apoiar famílias em vulnerabilidade em Cumbica.")

    elif msg == "3":
        resp.message("📞 *Contato*\n📍 Rua Segundo Tenente Renato Ometi, 65\n📧 contato@nucleobatuira.org.br")

    elif msg == "4":
        resp.message("📌 *Projetos*\n• Alimentação\n• Cursos\n• Apoio Familiar")

    else:
        resp.message("Ops! Não entendi. Digite *0* para ver as opções.")

    return str(resp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)