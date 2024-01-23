from flask import (
    Flask,
    render_template,
    request,
    session,
    redirect,
    jsonify,
    g
)
import pandas as pd
from werkzeug.security import generate_password_hash, check_password_hash
from utils import gera_timestamp


app = Flask(__name__)
app.secret_key = "{8y8+f8wF=W1"

#df priorizacao
colunas_priorizacao = ["Ordem", "Origem", "Destino", "Lead Time"]
priorizacao_df = pd.DataFrame(columns=colunas_priorizacao)

#df origem e destino
origem_destino_df = pd.read_excel('./bases_balanceamento_teste/OrigemDestino.xlsx')

#df nivel_servico
nivel_servico_df = pd.read_excel('./bases_balanceamento_teste/NivelServico.xlsx')
nivel_servico_df["NS DIA"] = nivel_servico_df["NS DIA"] * 100
nivel_servico_df["NS DIA"] = nivel_servico_df["NS DIA"].map('{:.2f}%'.format)

#df excluir
colunas_excluir = ["COD_PROD", "DESC_PROD", "Origem"]
excluir_df = pd.DataFrame(columns=colunas_excluir)

#df log de atividade
colunas_log = ["hora", "usuario", "atividade"]
log_df = pd.DataFrame(columns=colunas_log)


def registra_atividade_usuario(atividade):
    """
        Registra uma nova atividade no DataFrame de log de atividades dos usuários.

        Parâmetros:
        - atividade (str): String que descreve a atividade realizada pelo usuário.
    """
    nova_linha_log = {
        "hora": gera_timestamp(),
        "usuario": session["usuario_logado"],
        "atividade": atividade
    }
    # TODO - salvar cada alteração no banco
    log_df.loc[len(log_df) + 1] = nova_linha_log


@app.before_request
def before_request():
    if "usuario_logado" in session and session["usuario_logado"] is not None:
        g.usuario = session["usuario_logado"]
    else:
        g.usuario = None


@app.route("/")
def home():
    session["sucesso_autenticacao"] = False
    session["usuario_logado"] = None
    return render_template("home.html")


@app.route("/login-usuario", methods=["POST",])
def login_usuario():
    nome_login = request.form["nome_login"]
    senha_login = request.form["senha_login"]
    #TODO - lógica temporária, autenticação de usuário deve ser conferida no banco
    if nome_login == session["nome_usuario_cadastro"] and check_password_hash(session["senha_usuario_cadastro"], senha_login):
        session["sucesso_autenticacao"] = True
        session["usuario_logado"] = nome_login
        registra_atividade_usuario("login")

        return redirect("/processo")
    else:
        return render_template("home.html")


@app.route("/logout-usuario")
def logout_usuario():
    #TODO - realizar lógica pra salvar caminho feito pelo usuário
    registra_atividade_usuario("logout")
    session["sucesso_autenticacao"] = False
    session["usuario_logado"] = None

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
    if session["sucesso_autenticacao"] and "sucesso_autenticacao" in session:
        registra_atividade_usuario("acessou tela: processo")

        return render_template("processo.html")
    else:
        return redirect("/")


@app.route("/processo-salvar", methods=["POST",])
def processo_salvar():
    session["checkbox_mata_falta"] = request.form.get("checkbox_mata_falta")
    session["checkbox_excesso"] = request.form.get("checkbox_excesso")
    session["input_cobertura_origem"] = request.form["input_cobertura_origem"]
    session["input_cobertura_destino"] = request.form["input_cobertura_destino"]

    atividade_processo = (f"modificação de parâmetros processo: "
                          f"Mata Falta {session["checkbox_mata_falta"]}"
                          f" - Excesso {session["checkbox_excesso"]}"
                          f" - Cobertura Origem {session["input_cobertura_origem"]}"
                          f" - Cobertura Destino {session["input_cobertura_destino"]}")
    registra_atividade_usuario(atividade_processo)

    return redirect("/trechos")


@app.route("/trechos")
def trechos():
    if session["sucesso_autenticacao"] and "sucesso_autenticacao" in session:
        registra_atividade_usuario("acessou tela: trechos")
        session["input_destino"] = 'ES01'
        return render_template("trechos.html", tabela_priorizacao=priorizacao_df, tabela_nivel_servico=nivel_servico_df)
    else:
        return redirect("/")

@app.route("/nova-priorizacao")
def nova_priorizacao():
    lista_origem = origem_destino_df.query(f"DESTINO == '{session["input_destino"]}'")["ORIGEM"].to_list()
    return render_template(
        "nova_priorizacao.html",
        lista_destino=nivel_servico_df["DESTINO"].to_list(),
        lista_origem=lista_origem,
        destino_selecionado=session["input_destino"]
    )


@app.route("/atualiza-parametros-priorizacao", methods=["POST",])
def atualiza_nova_priorizacao():
    data = request.json
    input_destino = data.get("input_destino")
    session["input_destino"] = input_destino

    return jsonify({"status": "Dados recebidos com sucesso!"})

@app.route("/salvar-nova-priorizacao", methods=["POST",])
def salvar_nova_priorizacao():
    nova_priorizacao = {
        'Ordem': request.form["ordem"],
        'Origem': request.form["origem"],
        'Destino': request.form["destino"],
        'Lead Time': request.form["leadtime"]
    }

    if len(priorizacao_df) == 1 and priorizacao_df.iloc[0].eq('').all():
        tamanho_df = 0
    else:
        tamanho_df = len(priorizacao_df)
    priorizacao_df.loc[tamanho_df] = nova_priorizacao

    atividade_priorizacao = (f"linha adicionada à tabela de priorizacao: "
                             f"Ordem {nova_priorizacao["Ordem"]}"
                             f" - Origem {nova_priorizacao["Origem"]}"
                             f" - Destino {nova_priorizacao["Destino"]}"
                             f" - Lead Time {nova_priorizacao["Lead Time"]}")
    registra_atividade_usuario(atividade_priorizacao)

    return redirect("/trechos")


@app.route("/excluir-tabela-priorizacao", methods=["POST",])
def excluir_tabela_priorizacao():
    data = request.json
    linha_excluir = int(data.get("linha_excluir"))

    if "trechos" in data.get("final_url"):
        global priorizacao_df
        atividade_priorizacao = (f"linha excluída na tabela de priorizacao: "
                                 f"Ordem {priorizacao_df.loc[linha_excluir, "Ordem"]}"
                                 f" - Origem {priorizacao_df.loc[linha_excluir, "Origem"]}"
                                 f" - Destino {priorizacao_df.loc[linha_excluir, "Destino"]}"
                                 f" - Lead Time {priorizacao_df.loc[linha_excluir, "Lead Time"]}")
        priorizacao_df = priorizacao_df.drop(linha_excluir)
        registra_atividade_usuario(atividade_priorizacao)
        print(log_df)
    elif "excluir" in data.get("final_url"):
        global excluir_df
        atividade_exclusao = (f"linha excluída na tabela de exclusão: "
                              f"COD_PROD {excluir_df.loc[linha_excluir, "COD_PROD"]}"
                              f" - DESC_PROD {excluir_df.loc[linha_excluir, "DESC_PROD"]}"
                              f" - Origem {excluir_df.loc[linha_excluir, "Origem"]}")
        excluir_df = excluir_df.drop(linha_excluir)
        registra_atividade_usuario(atividade_exclusao)
        print(log_df)

    return jsonify({"status": "Dados recebidos com sucesso!"})


@app.route("/trechos-salvar", methods=["POST",])
def trechos_salvar():
    return redirect("/regras")


@app.route("/regras")
def regras():
    if session["sucesso_autenticacao"] and "sucesso_autenticacao" in session:
        registra_atividade_usuario("acessou tela: regras")
        return render_template("regras.html", tabela_regras=priorizacao_df)
    else:
        return redirect("/")


@app.route("/excluir")
def excluir():
    if session["sucesso_autenticacao"] and "sucesso_autenticacao" in session:
        registra_atividade_usuario("acessou tela: excluir")
        return render_template("excluir.html", tabela_excluir=excluir_df)
    else:
        return redirect("/")


@app.route("/nova-exclusao")
def nova_exclusao():
    return render_template("nova_exclusao.html")


@app.route("/excluir-salvar", methods=["POST",])
def excluir_salvar():
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

    atividade_exclusao = (f"linha adicionada à tabela de priorizacao: "
                          f"COD_PROD {nova_exclusao["COD_PROD"]}"
                          f" - DESC_PROD {nova_exclusao["DESC_PROD"]}"
                          f" - Origem {nova_exclusao["Origem"]}")
    registra_atividade_usuario(atividade_exclusao)

    return redirect("/excluir")


@app.route("/consolidado")
def consolidado():
    if session["sucesso_autenticacao"] and "sucesso_autenticacao" in session:
        registra_atividade_usuario("acessou tela: conoslidado")
        return render_template("consolidado.html", tabela_consolidado=excluir_df)
    else:
        return redirect("/")


app.run(debug=True)
