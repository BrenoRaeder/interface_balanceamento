from flask import (
    Flask,
    render_template,
    request,
    session,
    redirect
)
import pandas as pd


app = Flask(__name__)
app.secret_key = "{8y8+f8wF=W1"


priorizacao_dados = {
    'Ordem': [''],#, '', '', '', ''],
    'Origem': [''],#, '', '', '', ''],
    'Destino': [''],#, '', '', '', ''],
    'Validador': [''],#, '', '', '', ''],
    'Lead Time': ['']#, '', '', '', '']
}
priorizacao_df = pd.DataFrame(priorizacao_dados)


nivel_servico_dados = {
    'Ordem': [1, 2, 3, 4, 5],
    'Destino': ['ES01', 'RN01', 'SP07', 'RS01', 'PR01'],
    'NS DIA': [77.78, 79.66, 81.54, 82.55, 83.42]
}
nivel_servico_df = pd.DataFrame(nivel_servico_dados)


excluir_dados = {
    'COD_PROD': ['', '', '', '', ''],
    'DESC_PROD': ['', '', '', '', ''],
    'Origem': ['', '', '', '', '']
}
excluir_df = pd.DataFrame(excluir_dados)


@app.route("/")
def home():
    return render_template("home.html")


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
    return render_template("trechos.html", tabela_priorizacao=priorizacao_df, tabela_nivel_servico=nivel_servico_df)


@app.route("/nova-priorizacao")
def nova_priorizacao():
    return render_template("nova_priorizacao.html")


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


@app.route("/excluir-salvar", methods=["POST",])
def excluir_salvar():
    for indice, linha in excluir_df.iterrows():
        for coluna in excluir_df.columns:
            excluir_df.at[indice, coluna] = request.form.get(f"{coluna}_{indice}")
    return redirect("/consolidado")


@app.route("/consolidado")
def consolidado():
    return render_template("consolidado.html", tabela_consolidado=excluir_df)


app.run(debug=True)
