
$(document).ready(function() {
    var socketData;

    socket.on('result_end',function(data) {
        socketData = data.data;
        
        if (socketData.hasOwnProperty('None')) {return;}

        // Convert JSON into a flat array
        var flatData = [];
        var name_file = '';
        var head = [["DOM", "PAGINA", "TAXA DE IMPUREZA", "LINK", 'ACHEI/NÃO ACHEI']];
        var body = [];
        for (var termo in socketData) {
            name_file = termo;
            if (termo != 'None') {
                for (var title in socketData[termo]['titles']) {
                    for (var i = 0; i < socketData[termo]['titles'][title].length; i++) {
                        var item = socketData[termo]['titles'][title][i];
                        item.title = title;

                        // If score is null, assign it a value
                        item.score = item.score == null ? "T.E.R" : item.score;
                                
                        flatData.push(item);
                        body.push([item.title, item.page, item.score, 'https://dom.pmt.pi.gov.br/admin/upload/'+item.title+'.pdf#page='+item.page]);
                    }
                }
            }
        }


        var maxLength = 30;
        title_doc = name_file.length > maxLength ? name_file.substring(0, maxLength) : name_file;
        title_doc = title_doc.toUpperCase()
        // Convert flat array into CSV
        var csv = "DOM,PAGINA,TAXA DE IMPUREZA,LINK,ACHEI/NÃO ACHEI\n";
        for (var i = 0; i < flatData.length; i++) {
            var item = flatData[i];
            csv += item.title + ',' + item.page + ',' + item.score + ','  + 'https://dom.pmt.pi.gov.br/admin/upload/'+item.title+'.pdf#page='+item.page+'\n';
        }

        // Create a Blob from the CSV string
        var csvBlob = new Blob([csv], {type: 'text/csv'});

        // Create a URL for the Blob
        var csvUrl = URL.createObjectURL(csvBlob);

        // Set the href of the link to the Blob URL and add the download attribute
        var downloadLink = document.getElementById('download-link');        
        downloadLink.download = 'Escavador_'+title_doc+'.csv'; // This will be the name of the downloaded file
        downloadLink.href = csvUrl;

        //window.jsPDF = window.jspdf.jsPDF;
        const { jsPDF } = window.jspdf;
        // Create a jsPDF instance
        var doc = new jsPDF();

        
        
        //Interne struct pdf
        doc.setFontSize(10);
        doc.text('Documento gerado em https://' + document.domain, 15, 5);

        doc.setFontSize(24);
        doc.text('Resultado da Buscar no Escavador', 15, 20);
        
        var pos_y_table = 12
        var lines = doc.splitTextToSize('Texto procurado: '+ name_file, 350);
        var textHeight = doc.getTextDimensions(lines).h;
        pos_y_table += textHeight + 20;
        doc.setFontSize(12);
        doc.text(lines, 15, 30);
        
        doc.autoTable({
            startY: pos_y_table,
            head: head,
            body: body,
            styles: { fontSize: 8, textColor: [30,30,30] }, 
            headStyles: { fillColor: [131, 117, 255], textColor: [30,30,30], halign: 'center' },
            columnStyles: { 
                0: {cellWidth: 58}, 
                1: {cellWidth: 15,halign: 'center'}, 
                2: {cellWidth: 25,halign: 'center'},
                3: {cellWidth: 'auto', halign:'right'},
                4: {cellWidth: 25},
                
            }
        });

        $(document).ready(function(){
            $("#download-btn").click(function(e){
                e.stopPropagation();  
                $('#alert-d').removeClass('d-none');
            });
          });

        $('#donwload-csv').click((e)=> {
            downloadLink.click();
            
        })
        $('#donwload-pdf').click((e)=> {
            doc.save('Escavador_'+title_doc+'.pdf');
            
        })
    });
});


