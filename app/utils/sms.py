import random
from models.verification import VerificationCode
from app import db
from app import client
from config import TWILIO_PHONE_NUMBER

def generate_verification_code():
    return ''.join(random.choices('0123456789', k=6))


def send_verification_sms(phone_number):
    code = generate_verification_code()
    verification = VerificationCode(phone_number=phone_number, code=code)
    db.session.add(verification)
    db.session.commit()
    
    message = client.messages.create(
        body=f'Your Do2Done verification code is: {code}',
        from_=TWILIO_PHONE_NUMBER,
        to=phone_number
    )
    return message
