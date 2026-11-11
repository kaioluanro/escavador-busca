

var html_info_panel = `<div class="d-flex justify-content-center align-items-center color-font" style="height: 60vh;">
        <div class="col-md-7 text-center">
          <div class="row">
            <span name="info-panel-1" id="info-panel-1" class="font-h1-3 fs-3">BEM-VINDO ESCAVADOR</span>
          </div>
          <div class="row">
            <span name="info-panel-2" id="info-panel-2" class="font-h1-2 fs-3">Fique à vontade para começar a escavar em buscar do material procurando!</span>
          </div>
          <div id="info-panel-3" class="col d-none">
            <span id="info-panel-4" class="font-h1-2-i fs-5">
              Carregando...
            </span>
          </div>
        </div>
      </div>
        
        `;

var socket = io.connect('https://' + document.domain + ':' + location.port);

var sid = $.cookie('sid');

socket.on('set_sid_cookie', function(data) {
    sid = data.sid
    $.cookie('sid', data.sid);
    //console.log('=============== CLIENT SID');
    //console.log(sid);
});

var checkChangesInterval = null;
var isOkInfoForSearch = true;


function WriteInfoPanel(Title,subTitle) {
    $('#info-panel-1').text(Title);
    $('#info-panel-2').text(subTitle);
}

$(document).ready(function() {
    
    socket.on('load_config',function(data) {
        if (data['isValid'] == false) {
            $('#hud').addClass('d-none');
            WriteInfoPanel('CONFIGURANDO SITE!','Executando as configurações necessárias para o funcionamento da ferramenta.')        
        }
        else{
            if ($('#hud').hasClass('d-none')) {
                $('#hud').removeClass('d-none');
                WriteInfoPanel('BEM-VINDO ESCAVADOR','Fique à vontade para começar a escavar em buscar do material procurando!')
            }    
        }
    })
})

function showCancelSend(infopanel1_txt,infopanel2_txt,panelChangeInfo) {
    $('#submit-button').show();
    $('#loading-element1').addClass('d-none');
    //$('#loading-element').addClass('d-none');
    if (panelChangeInfo) {
        $('#info-panel-3').addClass('d-none');
        $('#info-panel-1').text(infopanel1_txt);
        $('#info-panel-2').text(infopanel2_txt);
    }
}

$(document).ready(function() {
    // Seu código JavaScript vai aqui
    $('#submit-button').click(function(e) {
        e.preventDefault();
        


        if (!$('#alert-e').hasClass('d-none')) {
            $('#alert-e').addClass('d-none');
        }

        isOkInfoForSearch = true;
        clearInterval(checkChangesInterval);

        $('#list_doc').empty();
        $('#list_doc').append(html_info_panel);

        // Buttom Status
        $(this).hide();
        //$('#loading-element').removeClass('d-none');
        $('#loading-element1').removeClass('d-none');
        // Loading Bar
        $('#info-panel-3').removeClass('d-none');
        // Loading DataFrame
        $('#info-panel-1').text('PARANDO O TERRENO PARA ESCAVAÇÃO');
        $('#info-panel-2').text('Isso pode levar alguns segundos.');
        $('#info-panel-4').text('Carregando...');

        var formData = {
            'start_day': $('select[name=start_day]').val(),
            'start_month': $('select[name=start_month]').val(),
            'start_year': $('select[name=start_year]').val(),
            'end_day': $('select[name=end_day]').val(),
            'end_month': $('select[name=end_month]').val(),
            'end_year': $('select[name=end_year]').val(),
            'text_search': $('textarea[name=text_search]').val(),
            'client_sid': sid,
        };

        $.ajax({
            type: 'POST',
            url: '',  // A URL onde você quer enviar os dados
            data: formData,
            dataType: 'json',
            encode: true
        })
        .done(function(data) {
            console.log(data);
        });

        $.post('/start_task', $('#message-text').val())
            .done(function() {
                // Inicia a verificação do status da tarefa.
                checkTaskStatus();
                
            })

    });

});

var progressValue = 0;

function checkTaskStatus() {
    $.get('/task_status')
        .done(function(data) {
            
            if (data.complete) {
                

                $('#info-panel-3').addClass('d-none');
                // Loading DataFrame
                //$('#info-panel-1').text('PRONTO PARA COMEÇA A ESCAVAÇÃO');
                //$('#info-panel-2').text('Os dados estão prontos para serem escavar.');
                //$('#info-panel-4').text('Completo');

                progressValue = 100;
                $('.progress-bar').css('width', progressValue + '%');
                $('.progress-bar').attr('aria-valuenow', progressValue);
                

            } else {
                if (isOkInfoForSearch){
                    // A tarefa não está completa, então verifica novamente depois de um segundo.
                    if (progressValue != 100){progressValue = progressValue + 2;}
                    else {progressValue = 0;}
                    $('.progress-bar').css('width', progressValue + '%');
                    $('.progress-bar').attr('aria-valuenow', progressValue);
                    setTimeout(checkTaskStatus, 2000);
                } 
                else{
                    showCancelSend('ALGO ERRADO!','Verifique pop-up de "Error".', true);
                }
            }
        });
}

socket.on('inf_process_data',function(data) {
    $('#info-panel-1').text('EM ESCAVAÇÃO');
    $('#info-panel-2').text('pode levar alguns segundos.');
    $('#info-panel-4').text('verificando...');

})

socket.on('result_end',function(data) {
        data= data.data
        
        var html_content1 = ''
        termo_isNone = true
        for(var termo in data) {
            
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

                var maxLength = 60;
                title = termo.length > maxLength ? termo.substring(0, maxLength) + "..." : termo;
                html_content1 +=`
                <div class="h-100 d-flex align-items-center justify-content-center">
                        <div class="row w-100">
                                <span class="font-h1-2 fs-5 text-center color-font">TERMO PROCURADO</span>
                                <span class="mt-1 font-h1-1 fs-3 color-font text-center">

                                        <span title="${termo}">-&nbsp;<u>${title.toUpperCase()}</u>&nbsp;-</span>
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
                //console.log('RETORNO ERROR = ' + termo)
                
                $('#list_doc').empty();
                $('#list_doc').append(html_info_panel);

                $('#info-panel-1').text('⚠️ NADA FOI ENCONTRAR! ⚠️');
                $('#info-panel-2').text(`Essa escavação foi difícil, mas, não foi possível encontrar o que estar procurando.
                Por favor, tente ajustar o Filtro temporal para um período mais curto (porem no caso do comando especifico "dom:", não ha necessidade, pois o filtro temporal não tem efeito nesse comando.), ou mais seja mais específico com assunto procurado na caixa de pesquisa.`);
                $('#info-panel-3').addClass('d-none');
            }
            else{
                //console.log('RETORNO VAZIO = ' + termo)
                
                $('#list_doc').empty();
                $('#list_doc').append(html_info_panel);

                $('#info-panel-1').text('⚠️ NADA FOI ENCONTRAR! ⚠️');
                $('#info-panel-2').text(`Essa escavação foi difícil, mas, não foi possível encontrar o que estar procurando.
                Por favor, tente ajustar o Filtro temporal para um período mais curto (porem no caso do comando especifico "dom:", não ha necessidade, pois o filtro temporal não tem efeito nesse comando.), ou mais seja mais específico com assunto procurado na caixa de pesquisa.`);
                $('#info-panel-3').addClass('d-none');
            }
        }

        $('#text_search').val('');
        $('.progress-bar').css('width', 0 + '%');
        $('.progress-bar').attr('aria-valuenow', 0);

        if (termo_isNone == false) {
            $('#list_doc').empty(); 
            $('#list_doc').append(html_content1);
        }
    
        //$('#loading-element').addClass('d-none');
        // A tarefa está completa, então altera o botão de volta.
        showCancelSend('','', false);

    
});
