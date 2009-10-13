BookingTool = {
	init: function() {
		
	},
	
	calendars: [],
	
	show_calendar: function(calendar_id, img) {
		
	},
	
	check_risk_for_field: function(input) {
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
	}
};

$(BookingTool.init);