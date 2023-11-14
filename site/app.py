from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    # app.run(debug=True, host='0.0.0.0', ssl_context=('cert.pem', 'key.pem'))
    # app.run(debug=True, host='0.0.0.0')
    # at port 80
    app.run(host='0.0.0.0', port=80)
