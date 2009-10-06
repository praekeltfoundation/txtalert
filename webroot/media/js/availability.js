// jquery document ready magic
$(function() {
	// get all availability inputs, apply change event listeners to all
	$('input.availability').change(function(event) {
		// input element is piggy backed in event.target
		input = $(event.target);
		// make user aware something is happening
		input.addClass('loading');
		// for each event, get the json for the given date value
		$.getJSON('/bookingtool/availability.js', {"date": input.attr('value')}, function(data) {
			// reset risk levels
			$.each(['high', 'medium', 'low'], function() {
				if(input.hasClass(this)) {
					input.removeClass(this);
				}
			});
			// set risk level
			input.addClass(data.risk);
			input.removeClass('loading');
		});
	});
});