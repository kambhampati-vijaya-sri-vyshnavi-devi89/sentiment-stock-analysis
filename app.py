from flask import Flask, render_template, jsonify, request
from utils.data_generator import get_sector_data, get_correlation_data, get_granger_results, get_summary_stats
from utils.sentiment_analyzer import analyze_text_sentiment

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/sector/<sector>')
def sector_data(sector):
    data = get_sector_data(sector)
    return jsonify(data)

@app.route('/api/correlation')
def correlation():
    data = get_correlation_data()
    return jsonify(data)

@app.route('/api/granger')
def granger():
    data = get_granger_results()
    return jsonify(data)

@app.route('/api/summary')
def summary():
    data = get_summary_stats()
    return jsonify(data)

@app.route('/api/analyze_sentiment', methods=['POST'])
def analyze_sentiment():
    body = request.get_json()
    text = body.get('text', '')
    result = analyze_text_sentiment(text)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
