window.addEventListener('load', function() {
    var preferences = get_credentials();
    var form = document.getElementById('signin_form');
    if(preferences.msisdn && preferences.patient_id) {
        form.msisdn.value = preferences.msisdn;
        form.patient_id.value = preferences.patient_id;
    } else {
        init_signin_form(form);
    }
  // var main = document.getElementById('main');
  // var about = document.getElementById('about');
  // var btn_header = document.getElementById('btn_header');
  //    
  // function showMain() {
  //   about.style.display = 'none';
  //   main.style.display = 'block';
  //   btn_header.textContent = 'About';
  // }
  //    
  // function showAbout() {
  //   about.style.display = 'block';
  //   main.style.display = 'none';
  //   btn_header.textContent = 'Back';
  // }
  //    
  // function flip() {
  //   if (main.currentStyle.display === 'block') {
  //     showAbout();
  //   } else {
  //     showMain();
  //   }
  // }
  //    
  // btn_header.addEventListener('click', flip, false);
}, false);

var get_credentials = function() {
    return {
        msisdn: widget.preferenceForKey('msisdn'),
        patient_id: widget.preferenceForKey('patient_id')
    };
};

var init_signin_form = function(form) {
    form.addEventListener('submit', function() {
       widget.setPreferenceForKey('msisdn', form.msisdn.value);
       widget.setPreferenceForKey('patient_id', form.patient_id.value);
    });
};

var display_preferences = function(form) {
    form.msisdn.value = widget.preferenceForKey('msisdn');
    form.patient_id.value = widget.preferenceForKey('patient_id');
};