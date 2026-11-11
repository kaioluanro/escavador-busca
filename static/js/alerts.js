socket.on('alert-e', function(data) {
    $('#alert-message').text(data.message);
    $('#alert-e').removeClass('d-none');
    isOkInfoForSearch = false;
  });

$(document).ready(function(){
    $(".alert-close-e").click(function(e){
        e.stopPropagation();  
        $('#alert-e').addClass('d-none');
        WriteInfoPanel('VAMOS LÁ!', 'Tente fazer os ajuste necessarios para começar as escavação. ');
    });
});

$(document).ready(function(){
  $(".alert-close-d").click(function(e){
      e.stopPropagation(); 
      $('#alert-d').addClass('d-none');
  });
});