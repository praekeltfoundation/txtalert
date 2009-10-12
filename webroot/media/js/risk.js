// jquery document ready magic
$(function() {
	// get all risk inputs
	inputs = $('input.riskField');
	
	// apply change event listeners to all
	inputs.change(function(event) {
		// input element is piggy backed in event.target
		check_risk_for_field($(event.target));
	});
	
	// add calendar link after each
	inputs.each(function() {
		$(this).after('<a href="#" name="calendar-' + this.id + '" class="open_calender"><img src="/media/img/admin/icon_calendar.gif"></a>');
	});
	
	// after adding the calendar links, add event handlers
	// left off here 
});

function check_risk_for_field(input) {
	// make user aware something is happening
	input.addClass('loading');
	// for each event, get the json for the given date value
	$.getJSON('/bookingtool/risk.js', {"date": input.attr('value')}, function(data) {
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
};