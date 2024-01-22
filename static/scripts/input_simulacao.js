//excluir linha tabela
url_atual = window.location.href
url_atual_split = url_atual.split("/")
final_url_atual = url_atual_split[url_atual_split.length - 1]

if(final_url_atual.includes("processo")) {
    
    let chk_mata_falta = document.querySelector("#checkbox_mata_falta")
    let chk_excesso = document.querySelector("#checkbox_excesso")
    let input_cobertura_origem = document.querySelector("#input_cobertura_origem")
    let input_cobertura_destino = document.querySelector("#input_cobertura_destino")

    console.log(typeof input_cobertura_destino.value)

    chk_mata_falta.addEventListener("change", () => {
        if(chk_mata_falta.checked === true) {
            if(chk_excesso.checked === false) {
                input_cobertura_origem.value = 30
            } else {
                input_cobertura_origem.value = 30
                input_cobertura_origem.removeAttribute('readonly')
                input_cobertura_destino.removeAttribute('readonly')
            }
        } else {
            input_cobertura_origem.setAttribute('readonly',"readonly")
            input_cobertura_destino.setAttribute('readonly', "readonly")
            if(chk_excesso.checked === true) {
                input_cobertura_origem.value = ''
                input_cobertura_destino.value = 90
            }
            else {
                input_cobertura_origem.value = ''
            }
        }
    })

    chk_excesso.addEventListener("change", () => {
        if(chk_excesso.checked === true) {
            if(chk_mata_falta.checked === false) {
                input_cobertura_destino.value = 90
            }
            else {
                input_cobertura_destino.value = 90
                input_cobertura_origem.removeAttribute('readonly')
                input_cobertura_destino.removeAttribute('readonly')
            }
        } else {
            input_cobertura_origem.setAttribute('readonly',"readonly")
            input_cobertura_destino.setAttribute('readonly', "readonly")
            if(chk_mata_falta.checked === true) {
                input_cobertura_origem.value = 30
                input_cobertura_destino.value = ''
            }
            else {
                input_cobertura_destino.value = ''
            }
        }
    })
}  
