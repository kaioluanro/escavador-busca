$(document).ready(function() {
    $.get('/info_db', function(data) {
        
        var total_pages = data.pages_all;
        var num_doms = data.num_doms;
        var dom_current = data.current_dom;
        
        $('#label_bar_div1').removeClass('me-3');
        $('#label_bar_div2').removeClass('me-3');
        $('#label_DOMs').removeClass('ms-4');
        $('#label_DOMs').addClass('ms-1');
        $('#label_pages_all').removeClass('ms-4');
        $('#label_pages_all').addClass('ms-1');
        $('#label_DOM_current').removeClass('ms-4');
        $('#label_DOM_current').addClass('ms-1');
        $('#dom_current').text(dom_current);
        $('#num_all_pages').text(total_pages);
        $('#num_doms').text(num_doms);
    });
});