from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

messages = []

@app.route('/')
def index():
    return render_template('index.html', messages=messages)

@app.route('/submit', methods=['POST'])
def submit():
    user_input = request.form.get('user_input')
    if user_input:
        messages.append({"sender": "user", "text": user_input})
        messages.append({"sender": "bot", "text": "Resposta automática."})
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
    
