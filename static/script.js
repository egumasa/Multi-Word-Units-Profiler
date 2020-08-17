$(document).ready(function() {
	$('table.display').DataTable({
    	"paging": false // false to disable pagination (or any other option)
	});
	// this is about spinner
	$('#submit').on('click', function()
  	{
		$('body').addClass('busy');  	
	});

});
