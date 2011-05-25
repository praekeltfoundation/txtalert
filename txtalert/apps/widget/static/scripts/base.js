// mock Opera mini's widget API while we're developing in
// a desktop browser
var widget = {
    storage: {},
    
    setPreferenceForKey: function(key, value) {
        this.storage[key] = value;
        return value;
    },
    
    preferenceForKey: function(key) {
        return this.storage[key];
    }
};

// Mock the txtalert patient Api
var Patient = {
    find: function(msisdn, patient_id, callback) {
        $.getJSON('/api/v1/patient.json', {
            msisdn: msisdn,
            patient_id: patient_id
        }, callback);
    }
};

$(document).ready(function() {
    var form = $('#signin_form');
    var msisdn = widget.preferenceForKey('msisdn');
    var patient_id = widget.preferenceForKey('patient_id');
    if(msisdn) {
        form.value = msisdn;
    }
    
    if(patient_id) {
        form.value = patient_id;
    }
    
    form.submit(function(evt) {
        form = evt.target;
        msisdn = form.msisdn.value;
        patient_id = form.patient_id.value;
        widget.setPreferenceForKey('msisdn', msisdn);
        widget.setPreferenceForKey('patient_id', msisdn);
        
        Patient.find(msisdn, patient_id, function(patient) {
            if(patient.msisdn && patient.patient_id) {
                show_next_appointment_for(patient);
            } else {
                login_failed();
            }
        });
        return false;
    });
});

var Format = {
    months: [
        'January', 'February', 'March', 'April', 'May', 'June', 
        'July', 'August', 'September', 'October', 'November', 'December'
    ],
    
    date: function(triplet) {
        abbr_month = this.months[triplet[1]];
        return [triplet[2], abbr_month, triplet[0]].join(" ");
    }
};

var login_failed = function() {
    $('#signin .error').css('display', 'block');
    $('#signin .error').html('Wrong Phone Number and Patient ID.<br/>' + 
                                '<strong>Please try again.</strong>');
};

var show_next_appointment_for = function(patient) {
    if(patient.next_appointment.length == 0) {
        $('#signin .error').css('display', 'block');
        $('#signin .error').html("You don't have a next appointment.<br/>" + 
                                    "<strong>Please contact your clinic.</strong>");
    } else {
        $('#signin').hide();
        $('#appointment .info h1').html(Format.date(patient.next_appointment));
        $('#appointment .info h2').html(patient.clinic);
        $('#appointment').show();
    }
};