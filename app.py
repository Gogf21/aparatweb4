from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse
import html
from db import save_user
from validators import validate_form_data
import os
import json
from http import cookies
import time
from datetime import datetime, timedelta

class RequestHandler(BaseHTTPRequestHandler):
    def _set_cookies(self, cookie_data, max_age=None, expires=None):
        cookie = cookies.SimpleCookie()
        for key, value in cookie_data.items():
            cookie[key] = value
            cookie[key]['path'] = '/'
            if max_age:
                cookie[key]['max-age'] = max_age
            if expires:
                cookie[key]['expires'] = expires
            cookie[key]['httponly'] = True
            cookie[key]['samesite'] = 'Lax'
        self.send_header('Set-Cookie', cookie.output(header=''))

    def _get_cookies(self):
        if 'Cookie' in self.headers:
            cookie = cookies.SimpleCookie()
            cookie.load(self.headers['Cookie'])
            return {k: v.value for k, v in cookie.items()}
        return {}

    def _clear_error_cookies(self):
        cookies_to_clear = ['fullname', 'phone', 'email', 'birthdate', 
                          'gender', 'language', 'bio', 'contract', 'errors']
        cookie_data = {name: '' for name in cookies_to_clear}
        self._set_cookies(cookie_data, max_age=0)

    def _prepare_form_data_from_cookies(self, cookie_data):
        form_data = {
            'fullname': [cookie_data.get('fullname', '')],
            'phone': [cookie_data.get('phone', '')],
            'email': [cookie_data.get('email', '')],
            'birthdate': [cookie_data.get('birthdate', '')],
            'gender': [cookie_data.get('gender', '')],
            'bio': [cookie_data.get('bio', '')],
            'contract': [cookie_data.get('contract', '')]
        }
        
        if 'language' in cookie_data:
            form_data['language'] = cookie_data['language'].split(',')
        
        return form_data

    def do_GET(self):
        if self.path == '/':
            self.serve_form()
        elif self.path == '/static/styles.css':
            self.serve_static_file('static/styles.css', 'text/css')
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'404 Not Found')

    def do_POST(self):
        if self.path == '/submit':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            data = parse_qs(post_data)
            
            errors = validate_form_data(data)
            
            if errors:
                cookie_data = {}
                for field in ['fullname', 'phone', 'email', 'birthdate', 'gender', 'bio']:
                    if field in data:
                        cookie_data[field] = data[field][0]
                
                if 'language' in data:
                    cookie_data['language'] = ','.join(data['language'])
                
                if 'contract' in data:
                    cookie_data['contract'] = 'on'
                
                cookie_data['errors'] = json.dumps(errors)
                
                self.send_response(303)
                self._set_cookies(cookie_data, max_age=300)
                self.send_header('Location', '/')
                self.end_headers()
            else:
                try:
                    user_data = self.prepare_user_data(data)
                    user_id = save_user(user_data)
                    
                    cookie_data = {
                        'fullname': data['fullname'][0],
                        'phone': data['phone'][0],
                        'email': data['email'][0],
                        'birthdate': data['birthdate'][0],
                        'gender': data['gender'][0],
                        'bio': data['bio'][0]
                    }
                    if 'language' in data:
                        cookie_data['language'] = ','.join(data['language'])
                    
                    expires = (datetime.now() + timedelta(days=365)).strftime('%a, %d %b %Y %H:%M:%S GMT')
                    self._clear_error_cookies()
                    self._set_cookies(cookie_data, expires=expires)
                    
                    # Показываем страницу успеха
                    self.serve_success_page(user_id)
                except Exception as e:
                    self.serve_form_with_errors({'server_error': str(e)}, data)

    def serve_form(self):
        try:
            with open('templates/form.html', 'r', encoding='utf-8') as file:
                html_content = file.read()
            
            cookie_data = self._get_cookies()
            errors = None
            form_data = None
            
            if 'errors' in cookie_data:
                errors = json.loads(cookie_data['errors'])
                form_data = self._prepare_form_data_from_cookies(cookie_data)
                # Очищаем cookies с ошибками
                self._clear_error_cookies()
            else:
                form_data = self._prepare_form_data_from_cookies(cookie_data)
            
            if form_data:
                for field in ['fullname', 'phone', 'email', 'birthdate', 'bio']:
                    if field in form_data:
                        value = html.escape(form_data[field][0])
                        html_content = html_content.replace(
                            f'name="{field}"',
                            f'name="{field}" value="{value}"'
                        )
                
                if 'gender' in form_data and form_data['gender'][0]:
                    gender = form_data['gender'][0]
                    html_content = html_content.replace(
                        f'value="{gender}"',
                        f'value="{gender}" checked'
                    )
                
                if 'contract' in form_data and form_data['contract'][0] == 'on':
                    html_content = html_content.replace(
                        'name="contract"',
                        'name="contract" checked'
                    )
                
                if 'language' in form_data:
                    for lang in form_data['language']:
                        if lang:  
                            html_content = html_content.replace(
                                f'value="{lang}"',
                                f'value="{lang}" selected'
                            )
            
            if errors:
                if 'server_error' in errors:
                    html_content = html_content.replace(
                        '<h2>Форма регистрации</h2>',
                        f'<h2>Форма регистрации</h2>\n<div class="server-error">{html.escape(errors["server_error"])}</div>'
                    )
                
                for field, error in errors.items():
                    if field != 'server_error':
                        html_content = html_content.replace(
                            f'name="{field}"',
                            f'name="{field}" class="error-field"'
                        )
                        error_div = f'<div class="error-message">{html.escape(error)}</div>'
                        html_content = html_content.replace(
                            f'<label for="{field}">',
                            f'{error_div}<label for="{field}">'
                        )
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html_content.encode('utf-8'))
        except FileNotFoundError:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b'Template file not found')
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f'Server error: {str(e)}'.encode('utf-8'))

    def serve_success_page(self, user_id):
        success_html = f"""
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <title>Успешная регистрация</title>
            <link rel="stylesheet" href="/static/styles.css">
        </head>
        <body>
            <div class="success-container">
                <h2>Регистрация завершена успешно!</h2>
                <p>Ваш ID: {html.escape(str(user_id))}</p>
                <a href="/">Вернуться к форме</a>
            </div>
        </body>
        </html>
        """
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(success_html.encode('utf-8'))

    def serve_static_file(self, filepath, content_type):
        try:
            with open(filepath, 'rb') as file:
                self.send_response(200)
                self.send_header('Content-type', content_type)
                self.end_headers()
                self.wfile.write(file.read())
        except FileNotFoundError:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'404 Not Found')

    def prepare_user_data(self, data):
        fullname_parts = data['fullname'][0].strip().split()
        return {
            'first_name': fullname_parts[0] if len(fullname_parts) > 0 else '',
            'last_name': fullname_parts[1] if len(fullname_parts) > 1 else '',
            'middle_name': fullname_parts[2] if len(fullname_parts) > 2 else None,
            'phone': data['phone'][0].strip(),
            'email': data['email'][0].strip(),
            'birthdate': data['birthdate'][0],
            'gender': data['gender'][0],
            'biography': data['bio'][0].strip(),
            'languages': data.get('language', [])
        }

def run_server():
    server_address = ('', 800)
    httpd = HTTPServer(server_address, RequestHandler)
    print('Сервер запущен на порту 8000...')
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()
