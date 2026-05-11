from django.core.validators import RegexValidator

class PhoneNumberValidator(RegexValidator):
    regex = r"^09\d{9}$"
    code = "phone invalid"
    message = "phone invalid"



class UserNameValidator(RegexValidator):
        regex = "^@[a-zA-Z][a-zA-Z0-9_]{4,31}$"
        code = "invalid username"
        message = "invalid username"


    
validate_phone_number = PhoneNumberValidator()
validate_user_name = UserNameValidator()