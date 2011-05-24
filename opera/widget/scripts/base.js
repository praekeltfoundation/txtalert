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
    
    patients: [{
        msisdn: '0761234567',
        patient_id: '123',
        next_appointment: new Date(2012,1,1),
        clinic: 'Temba Lethu Clinic'
    }],
    
    find: function(msisdn, patient_id) {
        console.log(this.patients);
        for(idx in this.patients) {
            patient = this.patients[idx];
            console.log(patient);
            if(patient.msisdn == msisdn && patient.patient_id == patient_id) {
                return patient;
            }
        }
        return false;
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
        
        patient = Patient.find(msisdn, patient_id);
        if(patient) {
            show_next_appointment_for(patient);
        } else {
            login_failed();
        }
        
        return false;
    });
});

var Format = {
    months: [
        'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
    ],
    
    date: function(date) {
        abbr_month = this.months[date.getMonth()];
        return [date.getDate(), abbr_month, date.getFullYear()].join(" ");
    }
};

var login_failed = function() {
    $('#signin .error').css('display', 'block');
    $('#signin .error').html('Wrong Phone Number and Patient ID.<br/>' + 
                                '<strong>Please try again.</strong>');
};

var show_next_appointment_for = function(patient) {
    $('#signin').hide();
    $('#appointment .info h1').html(Format.date(patient.next_appointment));
    $('#appointment .info h2').html(patient.clinic);
    $('#appointment').show();
};