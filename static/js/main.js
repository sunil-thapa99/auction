(function($) {
    "use strict";

    $('.next').click(function(){ $('#event_carousel').carousel('next');return false; });
    $('.prev').click(function(){ $('#event_carousel').carousel('prev');return false; });
    
})(jQuery);

$('#datepicker').datepicker({
    uiLibrary: 'bootstrap4',
    format: 'yyyy-dd-mm'
});
$('#datepicker1').datepicker({
    uiLibrary: 'bootstrap4',
    format: 'yyyy-dd-mm'
});

$("#category").change(function () {
	var url = $("#search_form").attr("data-medium-url"); 
	var cat_id = $(this).val(); 
	$.ajax({                      
		url: url,                   
		data: {
		  'category': cat_id      
		},
		success: function (data) {
		  	$("#prod-med").html(data); 
		}
	});

});

function display_div(){
	var ad = document.getElementById('advance_search')
	if (ad.style.display === 'none'){
		ad.style.display = 'block';
	}else{
		ad.style.display = 'none';
	}
}

// Lightbox
$(function () {
	$("#mdb-lightbox-ui").load("static/mdb-addons/mdb-lightbox-ui.html");
});