from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime

app = Flask(__name__)

# Replace 'your_api_key_here' with your actual NewsAPI key
NEWS_API_KEY = 'c4ad9764f9dd421287adc66e88323a3b'
NEWS_API_URL = 'https://newsapi.org/v2/everything'

# Route for the main page
@app.route('/', methods=['GET'])
def index():
    """Render the main page with the search form."""
    return render_template('index.html')

# Route for handling search requests
@app.route('/search', methods=['POST'])
def search():
    """Handle search requests, fetch news from NewsAPI, and return rendered articles."""
    keyword = request.form.get('keyword')
    from_date = request.form.get('from_date')
    to_date = request.form.get('to_date')
    source = request.form.get('source')
    
    if not keyword:
        return jsonify({'status': 'error', 'message': 'Keyword is required'})
    
    params = {
        'q': keyword,
        'apiKey': NEWS_API_KEY,
        'sortBy': 'publishedAt',
        'language': 'en',
        'page_size': 20
    }
    
    if from_date:
        params['from'] = from_date
    if to_date:
        params['to'] = to_date
    if source:
        params['sources'] = source
    
    response = requests.get(NEWS_API_URL, params=params)
    
    if response.status_code == 200:
        data = response.json()
        if data.get('status') == 'ok':
            articles = data.get('articles', [])
            for article in articles:
                published_at = article['publishedAt']
                dt = datetime.strptime(published_at, '%Y-%m-%dT%H:%M:%SZ')
                article['publishedAtFormatted'] = dt.strftime('%B %d, %Y, %H:%M UTC')
            from_date_formatted = None
            to_date_formatted = None
            if from_date:
                from_date_formatted = datetime.strptime(from_date, '%Y-%m-%d').strftime('%B %d, %Y')
            if to_date:
                to_date_formatted = datetime.strptime(to_date, '%Y-%m-%d').strftime('%B %d, %Y')
            html = render_template('articles.html', articles=articles, keyword=keyword, from_date=from_date_formatted, to_date=to_date_formatted)
            return jsonify({'status': 'success', 'html': html})
        else:
            return jsonify({'status': 'error', 'message': data.get('message', 'Error fetching news')})
    else:
        return jsonify({'status': 'error', 'message': 'Error fetching news'})

if __name__ == '__main__':
    app.run(debug=True)