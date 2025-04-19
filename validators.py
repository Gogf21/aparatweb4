import re
from datetime import datetime

def validate_fullname(fullname: str) -> str:
    if not fullname:
        return "ФИО обязательно для заполнения"
    
    parts = fullname.split()
    if len(parts) < 2:
        return "Введите имя и фамилию"
    
    if not re.match(r'^[а-яА-ЯёЁa-zA-Z\- ]+$', fullname):
        return "ФИО должно содержать только буквы, пробелы и дефисы"
    
    if len(parts) > 3:
        return "ФИО должно содержать не более 3 частей (фамилия, имя, отчество)"
    
    return None

def validate_phone(phone: str) -> str:
    if not phone:
        return "Телефон обязателен для заполнения"
    
    if not re.match(r'^(\+7|8)[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}$', phone):
        return "Неверный формат телефона. Допустимые форматы: +7 999 123-45-67, 89991234567"
    
    return None

def validate_email(email: str) -> str:
    if not email:
        return "Email обязателен для заполнения"
    
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        return "Некорректный email. Допустимы только латинские буквы, цифры и символы ._%+-"
    
    return None

def validate_birthdate(birthdate: str) -> str:
    if not birthdate:
        return "Дата рождения обязательна"
    
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', birthdate):
        return "Неверный формат даты. Используйте формат ГГГГ-ММ-ДД"
    
    try:
        date = datetime.strptime(birthdate, '%Y-%m-%d')
        if date > datetime.now():
            return "Дата рождения не может быть в будущем"
    except ValueError:
        return "Некорректная дата"
    
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
    
    if len(bio) > 500:
        return "Биография не должна превышать 500 символов"
    
    if re.search(r'[<>{}[\]]', bio):
        return "Биография содержит недопустимые символы (<, >, {, }, [, ])"
    
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
