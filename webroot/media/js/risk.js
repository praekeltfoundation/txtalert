BookingTool = {
	init: function() {
		// get all risk inputs
		inputs = $('input.risk-field');
		inputs.each(function(idx) {
			BookingTool.calendars[idx] = {};
			BookingTool.calendars[idx].input = this;
			
			// add the calendar container
			$(this).after('<div class="risk-calendar module" ' + 
							'id="risk-calendar-box-' + idx + '" ' + 
							'style="display: none;"></div>');
			
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
		
		// collect the containers
		containers = $('div[id^=risk-calendar-box]');
		containers.each(function(idx) {
			BookingTool.calendars[idx].container = $(this);
		});
		
		// collect img anchors, use those for positioning, easier than
		// using the anchors themselves
		img_anchors = $('a[id^=risk-calendar] img');
		img_anchors.each(function(idx) {
			// the anchor is the parent
			anchor = $(this).parent();
			// and stores the id of the calendar
			calendar_id = parseInt(anchor.attr("id").split("risk-calendar-")[1], 10);
			
			BookingTool.calendars[calendar_id].anchor = anchor;
			BookingTool.calendars[calendar_id].img = this;
			
			$(this).click(function() {
				BookingTool.hide_all_calendars();
				BookingTool.show_calendar($(this));
				// stop bubbling
				return false;
			});
		});
		
		// hide all calendars when clicking anything outside
		$(window).click(BookingTool.hide_all_calendars);
	},
	
	calendars: [],
	
	position_container: function(container, img) {
		position = $(img).position();
		container.css('position', 'absolute');
		container.css('top', position.top - container.height() + 10);
		container.css('left', position.left + 17);
	},
	
	show_calendar: function(img) {
		// get the calendar id from the DOM id, icky I know
		id = $(img).parent().attr('id');
		calendar_id = parseInt(id.split("risk-calendar-")[1], 10);
		
		container = BookingTool.calendars[calendar_id].container;
		container.html('<p><img src="/static/images/risk.loading.gif"> Loading calendar </p>');
		// position loading message
		BookingTool.position_container(container, img);
		container.show();
		
		// get input value
		input = BookingTool.calendars[calendar_id].input;
		match = input.value.match(/(\d{4})-(\d{1,2})-(\d{1,2})/);
		if(match) {
			path = '/bookingtool/calendar/' + match[1] + '/' + match[2] + '.html';
		} else {
			path = '';
		}
		
		// load the calendar over ajax
		BookingTool.load_calendar(calendar_id, container, path);
	},
	
	load_calendar: function(calendar_id, container, path) {
		
		// if a path is given use it, otherwise go to today
		if(!path) {
			path = '/bookingtool/calendar/today.html';
		}
		
		container.load(path, '', function(resp, status, req) {
			if(status != "success") {
				container.html("<p><strong>Oops!</strong> Something went wrong loading the calendar.</p>");
			} else {
				BookingTool.add_date_handlers(calendar_id, container);
				BookingTool.add_month_pagination_handlers(calendar_id, container);
			}
			// reposition with calendar or err msg loaded
			img = BookingTool.calendars[calendar_id].img;
			BookingTool.position_container(container, img);
		});
	},
	
	add_date_handlers: function(calendar_id, container) {
		$('td a', container).each(function() {
			$(this).click(function() {
				BookingTool.pick_date(calendar_id, $(this).attr('rel'));
				return false;
			});
		});
	},
	
	add_month_pagination_handlers: function(calendar_id, container) {
		$('p a', container).each(function() {
			$(this).click(function() {
				BookingTool.load_calendar(calendar_id, container, $(this).attr('href'));
				return false;
			});
		});
	},
	
	pick_date: function(calendar_id, date) {
		BookingTool.hide_calendar(calendar_id);
		input = BookingTool.calendars[calendar_id].input;
		$(input).attr('value', date);
		BookingTool.check_risk_for_field(input);
	},
	
	hide_calendar: function(calendar_id) {
		BookingTool.calendars[calendar_id].container.hide();
	},
	
	hide_all_calendars: function() {
		$(BookingTool.calendars).each(function(idx) {
			BookingTool.hide_calendar(idx);
		});
	},
	
	check_risk_for_field: function(input) {
		// make user aware something is happening
		input = $(input);
		input.addClass('loading');
		// for each event, get the json for the given date value
		$.getJSON('/bookingtool/calendar/risk.js', {"date": input.attr('value')}, function(data) {
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