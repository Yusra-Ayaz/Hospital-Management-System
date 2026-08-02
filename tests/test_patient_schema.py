from datetime import date
from presentation.schemas.hospital import PatientIn
def test_patient_schema_accepts_valid_patient():
    patient=PatientIn(medical_record_number="MRN-1",first_name="Ada",last_name="Lovelace",date_of_birth=date(1990,1,1),gender="female",phone="555-0100")
    assert patient.medical_record_number == "MRN-1"
