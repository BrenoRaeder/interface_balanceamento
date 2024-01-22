from flask import (
    Flask,
    render_template,
    request,
    session,
    redirect,
    jsonify
)
import pandas as pd
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = "{8y8+f8wF=W1"


priorizacao_dados = {
    'Ordem': [''],
    'Origem': [''],
    'Destino': [''],
    'Validador': [''],
    'Lead Time': ['']
}

priorizacao_df = pd.DataFrame(priorizacao_dados)
origem_destino_df = pd.read_excel('../bases_balanceamento_teste/OrigemDestino.xlsx')
nivel_servico_df = pd.read_excel('../bases_balanceamento_teste/NivelServico.xlsx')
nivel_servico_df["NS DIA"] = nivel_servico_df["NS DIA"] * 100
nivel_servico_df["NS DIA"] = nivel_servico_df["NS DIA"].map('{:.2f}%'.format)


excluir_dados = {
    'COD_PROD': [''],
    'DESC_PROD': [''],
    'Origem': ['']
}
excluir_df = pd.DataFrame(excluir_dados)


@app.route("/")
def home():
    if session["senha_usuario_cadastro"] is not None:
        print(session["senha_usuario_cadastro"])
    return render_template("home.html")


@app.route("/login-usuario", methods=["POST",])
def login_usuario():
    nome_login = request.form["nome_login"]
    senha_login = request.form["senha_login"]
    #TODO - lógica temporária, autenticação de usuário deve ser salva em banco
    if nome_login == session["nome_usuario_cadastro"] and check_password_hash(session["senha_usuario_cadastro"], senha_login):
        return redirect("/processo")
    else:
        return redirect("/")

@app.route("/cadastro-usuario")
def cadastro_usuario():
    return render_template("cadastro_usuario.html")


@app.route("/salvar-cadastro-usuario", methods=["POST",])
def salvar_cadastro_usuario():
    # TODO - lógica temporária, autenticação de usuário deve ser salva em banco
    session["nome_usuario_cadastro"] = request.form["nome_cadastro"]
    session["senha_usuario_cadastro"] = generate_password_hash(request.form["senha_cadastro"], method="pbkdf2:sha256")
    return redirect("/")


@app.route("/processo")
def processo():
    return render_template("processo.html")


@app.route("/processo-salvar", methods=["POST",])
def processo_salvar():
    session["checkbox_mata_falta"] = request.form.get("checkbox_mata_falta")
    session["checkbox_excesso"] = request.form.get("checkbox_excesso")
    session["input_cobertura_origem"] = request.form["input_cobertura_origem"]
    session["input_cobertura_destino"] = request.form["input_cobertura_destino"]

    return redirect("/trechos")


@app.route("/trechos")
def trechos():
    session["input_destino"] = 'ES01'
    return render_template("trechos.html", tabela_priorizacao=priorizacao_df, tabela_nivel_servico=nivel_servico_df)


@app.route("/nova-priorizacao")
def nova_priorizacao():
    lista_origem = origem_destino_df.query(f"DESTINO == '{session["input_destino"]}'")["ORIGEM"].to_list()
    ordem = nivel_servico_df.query(f"DESTINO == '{session["input_destino"]}'")["ORDEM"].to_list()[0]
    return render_template(
        "nova_priorizacao.html",
        ordem=ordem,
        lista_destino=nivel_servico_df["DESTINO"].to_list(),
        lista_origem=lista_origem,
        destino_selecionado=session["input_destino"]
    )

@app.route("/atualiza-parametros-priorizacao", methods=["POST",])
def atualiza_nova_priorizacao():
    data = request.json
    input_destino = data.get("input_destino")
    session["input_destino"] = input_destino
    print(input_destino)

    return jsonify({"status": "Dados recebidos com sucesso!"})

@app.route("/salvar-nova-priorizacao", methods=["POST",])
def salvar_nova_priorizacao():
    nova_priorizacao = {
        'Ordem': request.form["ordem"],
        'Origem': request.form["origem"],
        'Destino': request.form["destino"],
        'Validador': request.form["validador"],
        'Lead Time': request.form["leadtime"]
    }

    if len(priorizacao_df) == 1 and priorizacao_df.iloc[0].eq('').all():
        tamanho_df = 0
    else:
        tamanho_df = len(priorizacao_df)
    priorizacao_df.loc[tamanho_df] = nova_priorizacao

    return redirect("/trechos")


@app.route("/excluir-tabela-priorizacao", methods=["POST",])
def excluir_tabela_priorizacao():
    data = request.json
    linha_excluir = int(data.get("linha_excluir"))

    if "trechos" in data.get("final_url"):
        global priorizacao_df
        priorizacao_df = priorizacao_df.drop(linha_excluir)
    elif "excluir" in data.get("final_url"):
        global excluir_df
        excluir_df = excluir_df.drop(linha_excluir)

    return jsonify({"status": "Dados recebidos com sucesso!"})


@app.route("/trechos-salvar", methods=["POST",])
def trechos_salvar():
    '''for indice, linha in priorizacao_df.iterrows():
        for coluna in priorizacao_df.columns:
            if not (coluna == "Ordem"):
                priorizacao_df.at[indice, coluna] = request.form.get(f"{coluna}_{indice}")'''
    return redirect("/regras")


@app.route("/regras")
def regras():
    return render_template("regras.html", tabela_regras=priorizacao_df)


@app.route("/excluir")
def excluir():
    return render_template("excluir.html", tabela_excluir=excluir_df)


@app.route("/nova-exclusao")
def nova_exclusao():
    return render_template("nova_exclusao.html")


@app.route("/excluir-salvar", methods=["POST",])
def excluir_salvar():
    '''for indice, linha in excluir_df.iterrows():
        for coluna in excluir_df.columns:
            excluir_df.at[indice, coluna] = request.form.get(f"{coluna}_{indice}")'''
    return redirect("/consolidado")


@app.route("/salvar-nova-exclusao", methods=["POST",])
def salvar_nova_exclusao():
    nova_exclusao = {
        "COD_PROD": request.form["cod_prod"],
        "DESC_PROD": request.form["desc_prod"],
        "Origem": request.form["origem"]
    }

    if len(excluir_df) == 1 and excluir_df.iloc[0].eq('').all():
        tamanho_df = 0
    else:
        tamanho_df = len(excluir_df)
    excluir_df.loc[tamanho_df] = nova_exclusao

    return redirect("/excluir")


@app.route("/consolidado")
def consolidado():
    return render_template("consolidado.html", tabela_consolidado=excluir_df)


app.run(debug=True)
