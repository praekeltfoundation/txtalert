BookingTool = {
	init: function() {
		// get all risk inputs
		inputs = $('input.risk-field');
		inputs.each(function(idx) {
			BookingTool.calendars[idx] = {};
			BookingTool.calendars[idx]['input'] = this;
			
			// add the calendar container
			$(this).after('<div id="risk-calendar-box-' + idx + '"></div>');
			
			// add the calendar links
			$(this).after('<a href="#" id="risk-calendar-' + idx + '">' + 
							'<img src="/media/img/admin/icon_calendar.gif">' + 
						'</a>');
		});
		
		// apply change event listeners to all
		inputs.change(function(event) {
			// input element is piggy backed in event.target
			check_risk_for_field($(event.target));
		});
		
		// collect img anchors, use those for positioning, easier than
		// using the anchors themselves
		img_anchors = $('a[id^=risk-calendar] img');
		img_anchors.each(function(idx) {
			// the anchor is the parent
			anchor = $(this).parent();
			// and stores the id of the calendar
			calendar_id = parseInt(anchor.attr("id").split("risk-calendar-")[1], 10);
			
			BookingTool.calendars[calendar_id]["anchor"] = anchor;
			BookingTool.calendars[calendar_id]["img"] = this;
			
			$(this).click(function() {
				BookingTool.show_calendar(calendar_id, this);
			});
			// stop bubbling
			return false;
		});
	},
	
	calendars: [],
	
	show_calendar: function(calendar_id, img) {
		
		position = $(img).position();
		
		container = $('risk-calendar-box-' + calendar_id);
		container.html('<p><img src="/static/images/risk.loading.gif"> Loading ... </p>');
		container.css('position', 'absolute');
		container.load('/bookingtool/calendar/today.html', '', function(resp, status, req) {
			
		});
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