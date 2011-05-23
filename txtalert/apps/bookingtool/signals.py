def pre_save_booking_patient_handler(**kwargs):
    """Must be a pre_save handler"""
    pre_save_booking_patient(kwargs['instance'])

def pre_save_booking_patient(booking_patient):
    """If the date_of_birth isn't set, we automatically pin the date of 
    birth based on the year, assuming the 1st of january."""
    if not booking_patient.date_of_birth:
        booking_patient.date_of_birth = booking_patient.determine_year_of_birth()
    
    """If the patient was opted in and our opt_status hasn't been set yet
    automatically set it to 'opt-in' based on the patient record"""
    if booking_patient.opted_in and not booking_patient.opt_status:
        booking_patient.opt_status = 'opt-in'
    
    """and the other way around as well"""
    if booking_patient.opt_status == 'opt-in' and not booking_patient.opted_in:
        booking_patient.opted_in = True
