// poormans namespacing
if(!window.BookingTool) {
	BookingTool = {};
};

BookingTool.Verification = {
	
	NAME: '',
	
	init: function() {
		
		button = $('input.sms-verification')[0];
		if(button) {
			name = button.id.split('send_sms-')[1];
			BookingTool.Verification.NAME = name;
			
			// set for first time after page load
			BookingTool.Verification.update_active_msisdn();
			
			// re-set for every change in the active_msisdn
			$('#id_active_msisdn').change(function() {
				BookingTool.Verification.update_active_msisdn();
			});
			
			// every time the button is clicked, send and sms
			$('input#send_sms-'+name).click(function(event) {
				BookingTool.Verification.send_sms();
				return false;
			});
		}
	},
	
	update_active_msisdn: function() {
		selected_index = $('#id_active_msisdn').val();
		selected_child = $('#id_active_msisdn').children()[selected_index];
		new_msisdn = $(selected_child).text();
		$('#id_' + BookingTool.Verification.NAME).attr('value',new_msisdn);
	},
	
	send_sms: function() {
		result_container = $('#send_sms_result-'+BookingTool.Verification.NAME);
		result_container.html('<img src="/static/images/verification.loading.gif">');
		msisdn = $('#id_' + BookingTool.Verification.NAME).attr('value');
		if(msisdn) {
			result_container.load('/bookingtool/verification.html', {
				'msisdn': msisdn
			});
		}
	}
};

$(BookingTool.Verification.init);

