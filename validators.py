import re
from datetime import datetime

def validate_fullname(fullname: str) -> str:
    if not fullname:
        return "ФИО обязательно для заполнения"
    parts = fullname.split()
    if len(parts) < 2:
        return "Введите имя и фамилию"
    if not all(part.isalpha() for part in parts):
        return "ФИО должно содержать только буквы"
    return None

def validate_phone(phone: str) -> str:
    if not phone:
        return "Телефон обязателен для заполнения"
    if not re.match(r'^\+?[0-9\s\-\(\)]{10,15}$', phone):
        return "Неверный формат телефона"
    return None

def validate_email(email: str) -> str:
    if not email:
        return "Email обязателен для заполнения"
    if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
        return "Некорректный email"
    return None

def validate_birthdate(birthdate: str) -> str:
    if not birthdate:
        return "Дата рождения обязательна"
    try:
        date = datetime.strptime(birthdate, '%Y-%m-%d')
        if date > datetime.now():
            return "Дата рождения не может быть в будущем"
    except ValueError:
        return "Неверный формат даты"
    return None

def validate_gender(gender: str) -> str:
    if gender not in ['male', 'female']:
        return "Выберите пол"
    return None

def validate_languages(languages: list) -> str:
    valid_langs = {'Pascal', 'C', 'C++', 'JavaScript', 'PHP', 
                  'Python', 'Java', 'Haskel', 'Clojure', 'Prolog', 'Scala', 'Go'}
    if not languages:
        return "Выберите хотя бы один язык"
    if not all(lang in valid_langs for lang in languages):
        return "Выбраны недопустимые языки"
    return None

def validate_biography(bio: str) -> str:
    if not bio or len(bio.strip()) < 10:
        return "Биография должна содержать минимум 10 символов"
    return None

def validate_contract(contract: str) -> str:
    if contract != 'on':
        return "Необходимо подтвердить контракт"
    return None

def validate_form_data(data: dict) -> dict:
    errors = {}
    
    if error := validate_fullname(data.get('fullname', [''])[0]):
        errors['fullname'] = error
    
    if error := validate_phone(data.get('phone', [''])[0]):
        errors['phone'] = error
    
    if error := validate_email(data.get('email', [''])[0]):
        errors['email'] = error
    
    if error := validate_birthdate(data.get('birthdate', [''])[0]):
        errors['birthdate'] = error
    
    if error := validate_gender(data.get('gender', [''])[0]):
        errors['gender'] = error
    
    if error := validate_languages(data.get('language', [])):
        errors['language'] = error
    
    if error := validate_biography(data.get('bio', [''])[0]):
        errors['bio'] = error
    
    if error := validate_contract(data.get('contract', [''])[0]):
        errors['contract'] = error
    
    return errors

def validate_login_form(data: dict) -> dict:
    errors = {}
    
    if not data.get('username', [''])[0]:
        errors['username'] = "Логин обязателен"
    
    if not data.get('password', [''])[0]:
        errors['password'] = "Пароль обязателен"
    
    return errors
