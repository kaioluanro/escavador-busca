
function checkTaskStatus1() {
    $.get('/task_status1')
        .done(function(data) {
            if (data.complete) {
                // Loading DataFrame
                $('#info-panel-1').text('EM ESCAVAÇÃO');
                $('#info-panel-2').text('pode levar alguns segundos.');
                $('#info-panel-4').text('verificando...');
                checkChangesInterval = setInterval(function() {
                    $.ajax({
                        url: '/consulta',
                        type: 'GET',
                        data: {text_search: $('#message-text').val()},
                        dataType: 'json',
                        success: function(data) {  
                            var html_content1 = ''
                            termo_isNone = true
                            for(var termo in data) {
                                
                                // SUCESS SEARCH
                                $('#info-panel-1').text('FINALIZADO');
                                $('#info-panel-2').text('Foi difícil, mas conseguir!');
                                $('#info-panel-4').text('Completo');

                                var html_content = '';
                                if (termo != 'None'){
                                    
                                    termo_isNone = false
                                    for(var title in data[termo]['titles']) {
                                        for(var i=0; i < data[termo]['titles'][title].length; i++) {
                                            var page = data[termo]['titles'][title][i]['page'];
                                            var score = data[termo]['titles'][title][i]['score'];
                            
                                            html_content += `
                                            <p class="mt-1 text-break text-start font-h1-2 fs-4 font-head color-yellow">
                                            <table class="table table-dark table-striped">
                                                <tr>
                                                <td>
                                                    <img src="/static/img/doc_icon.svg" alt="Logo" width="30" height="24" class="d-inline-block align-text-top color-whiter">
                                                </td>
                                                <td>
                                                    <a class="color-font font-head fs-4" href="https://dom.pmt.pi.gov.br/admin/upload/${title}.pdf#page=${page}" target="_blank">${title}</a>
                                                </td>
                                                <td class="font-h1-2 font-head color-yellow">página : <span class="color-font font-head fs-4"> ${page}</span></td>
                                                <td class="font-h1-2 font-head color-yellow">Taxa de Impureza: <span class="color-font font-head fs-4"> ${(score == null) ? score = "T.E.R" : score }</span></td>
                                                
                                                </tr>
                                            </table>
                                            </p>
                                            `;
                                        }
                                    }
                                    html_content1 +=`
                                    <div class="h-100 d-flex align-items-center justify-content-center">
                                            <div class="row w-100">
                                                    <span class="font-h1-2 fs-5 text-center color-font">TERMO PROCURADO</span>
                                                    <span class="mt-1 font-h1-1 fs-3 color-font text-center">

                                                            <span>-&nbsp;<u>${termo}</u>&nbsp;-</span>
                                                            <button id="download-btn" type="button" class="btn btn-secondary">
                                                                <a id="download-link" class="d-none"></a>
                                                                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-download" viewBox="0 0 16 16">
                                                                <path d="M.5 9.9a.5.5 0 0 1 .5.5v2.5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-2.5a.5.5 0 0 1 1 0v2.5a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2v-2.5a.5.5 0 0 1 .5-.5z"></path>
                                                                <path d="M7.646 11.854a.5.5 0 0 0 .708 0l3-3a.5.5 0 0 0-.708-.708L8.5 10.293V1.5a.5.5 0 0 0-1 0v8.793L5.354 8.146a.5.5 0 1 0-.708.708l3 3z"></path>
                                                                </svg>
                                                            </button>
                                                    </span>
                                                    <div class="mt-2 row justify-content-center">
                                                            <div class="col-md-7">
                                                                    <div class="card bg-color-gray">
                                                                            <div class="mt-2 card-body div-limited">
                                                                                ${html_content}   
                                                                            </div>
                                                                    </div>
                                                            </div>
                                                    </div>
                                            </div>
                            
                                    </div>
                                    `
                                }
                                else if (termo == 'Error') {
                                    console.log('RETORNO ERROR = ' + termo)
                                    
                                    $('#list_doc').empty();
                                    $('#list_doc').append(html_info_panel);

                                    $('#info-panel-1').text('⚠️ NADA FOI ENCONTRAR! ⚠️');
                                    $('#info-panel-2').text(`Essa escavação foi difícil, mas, não foi possível encontrar o que estar procurando.
                                    Por favor, tente ajustar o Filtro temporal para um período mais curto (porem no caso do comando especifico "dom:", não ha necessidade, pois o filtro temporal não tem efeito nesse comando.), ou mais seja mais específico com assunto procurado na caixa de pesquisa.`);
                                    $('#info-panel-3').addClass('d-none');
                                }
                                else{
                                    console.log('RETORNO VAZIO = ' + termo)
                                    
                                    $('#list_doc').empty();
                                    $('#list_doc').append(html_info_panel);

                                    $('#info-panel-1').text('⚠️ NADA FOI ENCONTRAR! ⚠️');
                                    $('#info-panel-2').text(`Essa escavação foi difícil, mas, não foi possível encontrar o que estar procurando.
                                    Por favor, tente ajustar o Filtro temporal para um período mais curto (porem no caso do comando especifico "dom:", não ha necessidade, pois o filtro temporal não tem efeito nesse comando.), ou mais seja mais específico com assunto procurado na caixa de pesquisa.`);
                                    $('#info-panel-3').addClass('d-none');
                                }
                            }
                            
                            if (termo_isNone == false) {
                                $('#list_doc').empty(); 
                                $('#list_doc').append(html_content1);
                            }
                        
                            $('#loading-element').addClass('d-none');
                            // A tarefa está completa, então altera o botão de volta.
                            showCancelSend('','', false);
                        }
                    });
                }, 5000); // Verifica a cada 30 segundos

                // Parar a verificação após 5 minutos
                setTimeout(function() {
                    clearInterval(checkChangesInterval);
                }, 2 * 60 * 1000);
            }
            else {
                setTimeout(checkTaskStatus1, 2000);
            }
        });
};