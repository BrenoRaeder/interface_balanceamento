function alteraParametroPriorizacao() {
    //excluir linha tabela
    url_atual = window.location.href
    url_atual_split = url_atual.split("/")
    final_url_atual = url_atual_split[url_atual_split.length - 1]
    
    if(final_url_atual.includes("nova-priorizacao")) {

        let input_destino = document.querySelector("#destino").value

        // Envia o ID para o Flask usando Fetch API
        fetch('/atualiza-parametros-priorizacao', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                "input_destino" : input_destino
            }),
        }).then(response => response.json())
            .then(data => {
                console.log(data);
                location.reload()
            })
            .catch(error => {
                console.error("Erro ao enviar dados para o Flask:", error);
            });
    }
}
    