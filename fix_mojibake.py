import re

def clean_file(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read()
            
        cleaned = re.sub(r'[^\x00-\x7F]+', ' ', text)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(cleaned)
        print('Cleaned', path)
    except Exception as e:
        print('Error on', path, e)

clean_file('app.py')
clean_file('auth_ui.py')
