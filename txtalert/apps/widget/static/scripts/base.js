// Access to txtalert patient json API
var Patient = {
    URL: 'http://qa.txtalert.praekeltfoundation.org/api/v1/patient.json',
    find: function(msisdn, patient_id, callback) {
        var req = new XMLHttpRequest();
        req.onreadystatechange = function () {
            if (req.readyState != 4) return;
            if (req.status == 200 ) {
                eval("this.json = " + req.responseText);
                callback(this.json);
            } else {
                var err = 'Error retrieving patient info: ' + req.status + ' (' + req.statusText + ')';
                console.log(err);
            }
        };
        req.open('GET', this.URL + '?patient_id='+encodeURIComponent(patient_id)+'&msisdn='+encodeURIComponent(msisdn), true );
        req.send(null);
    }
};

window.addEventListener('load', function() {
    var form = document.getElementById('signin_form');
    var msisdn = widget.preferenceForKey('msisdn');
    var patient_id = widget.preferenceForKey('patient_id');
    
    if(msisdn) {
        form.msisdn.value = msisdn;
    }
    
    if(patient_id) {
        form.patient_id.value = patient_id;
    }
    form.msisdn.addEventListener('change', function(evt) {
        form.patient_id.value = '1';
    });
    
    form.addEventListener('submit', function(evt) {
        evt.preventDefault();
        
        msisdn = form.msisdn.value;
        patient_id = form.patient_id.value;
        widget.setPreferenceForKey('msisdn', msisdn);
        widget.setPreferenceForKey('patient_id', patient_id);
        Patient.find(msisdn, patient_id, function(patient) {
            if(patient.msisdn && patient.patient_id) {
                show_next_appointment_for(patient);
            } else {
                login_failed();
            }
        });
    }, true);
    
}, false);

// Allow the widget to run outside the widget environment
if(typeof window.widget == "undefined") {
    console.log('Mocking widget, not running in the Widget environment');
    window.widget = {
        storage: {},

        setPreferenceForKey: function(key, value) {
            console.log('setting '+key+': '+value);
            this.storage[key] = value;
            return value;
        },

        preferenceForKey: function(key) {
            console.log('reading '+key+' as '+this.storage[key]);
            return this.storage[key];
        }
    };
    
    console.log('Mocking URL to use relative Ajax URL');
    Patient.URL = '/api/v1/patient.json';
}

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

var show_error = function(message) {
    var signin = document.getElementById('signin');
    var error = signin.getElementsByClassName('error')[0];
    error.innerHTML = message;
    show_element(error);
};

var login_failed = function() {
    show_error('Wrong Phone Number and Patient ID.<br/>' + 
                '<strong>Please try again.</strong>');
};

var hide_element = function(element) {
    element.style.display = 'none';
};

var show_element = function(element) {
    element.style.display = 'block';    
};

var show_next_appointment_for = function(patient) {
    
    var signin = document.getElementById('signin');
    var appointment = document.getElementById('appointment');
    
    if(patient.next_appointment.length == 0) {
        show_error("You don't have a next appointment.<br/>" + 
                     "<strong>Please contact your clinic.</strong>");
    } else {
        hide_element(signin);
        var span = appointment.getElementsByTagName('span')[0];
        span.innerHTML = 'Hello '+patient.name+' '+patient.surname;
        
        var info = appointment.getElementsByClassName('info')[0];
        var h1 = info.getElementsByTagName('h1')[0];
        var h2 = info.getElementsByTagName('h2')[0];
        
        h1.innerHTML = Format.date(patient.next_appointment);
        h2.innerHTML = patient.clinic;
        
        show_element(appointment);
    }
};