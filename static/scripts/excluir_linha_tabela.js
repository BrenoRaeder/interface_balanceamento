//excluir linha tabela
url_atual = window.location.href
url_atual_split = url_atual.split("/")
final_url_atual = url_atual_split[url_atual_split.length - 1]

if(final_url_atual.includes("trechos") || final_url_atual.includes("excluir")) {
    let btnsExcluirTabela = document.querySelectorAll(".excluir_tabela")
    btnsExcluirTabela.forEach( btn => {
        btn.addEventListener("click", (e) => {
    
            let linha_excluir = e.target.id

            // Envia o ID para o Flask usando Fetch API
            fetch('/excluir-tabela-priorizacao', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    "linha_excluir" : linha_excluir,
                    "final_url" : final_url_atual
                }),
            })
            .then(response => response.json())
            .then(data => {
                console.log(data);
                location.reload()
            })
            .catch(error => {
                console.error("Erro ao enviar dados para o Flask:", error);
            });
        })
    });
}
