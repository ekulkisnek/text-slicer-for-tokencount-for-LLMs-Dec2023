from flask import Flask, request, render_template_string
import os
import re

# ------------------------
# Flask Application Setup
# ------------------------
app = Flask(__name__)
app.secret_key = os.urandom(24)  # Set a secret key for session management

# In-memory cache for storing chunked texts
chunked_text_cache = {}

# ------------------------
# Text Chunking Functions
# ------------------------
def clean_text(text):
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"\S+@\S+", "", text)
    text = re.sub(r"[^a-zA-Z\s]", "", text)
    return " ".join(text.split())

def remove_stopwords(text):
    stopwords = set(["a", "an", "and", "at", "but", "how", "in", "is", "on", "or", "the", "to", "what", "will"])
    return " ".join(word for word in text.split() if word.lower() not in stopwords)

def chunk_text(text, max_length=30000):
    return [text[i:i + max_length] for i in range(0, len(text), max_length)]

# ------------------------
# Route: Display Chunked Text
# ------------------------
# Route: Display Chunked Text
@app.route('/text/<text_id>')
def show_text(text_id):
    text = chunked_text_cache.get(text_id, 'No text available.')
    return render_template_string('''
        <style>
            #chunkedText {
                white-space: pre-wrap;
            }
        </style>
        <button onclick="copyToClipboard()">Copy to Clipboard</button>
        <script>
        function copyToClipboard() {
            var text = document.getElementById("chunkedText").innerText;
            navigator.clipboard.writeText(text);
        }
        </script>
        <pre id="chunkedText">{{ text }}</pre>
        <a href="/">Back to form</a>
        ''', text=text)

# Route: Main Index
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        input_text = request.form.get('input_text')
        cleaned_text = clean_text(input_text)
        final_text = remove_stopwords(cleaned_text)
        chunks = chunk_text(final_text, max_length=30000)

        chunk_ids = []
        for chunk in chunks:
            chunk_id = os.urandom(8).hex()
            chunked_text_cache[chunk_id] = chunk
            chunk_ids.append(chunk_id)

        return render_template_string('''
            <h2>Text Chunks</h2>
            <p>To provide the context for the above prompt, I will send you text in parts. When I am finished, I will tell you 'ALL PARTS SENT'. Do not answer until you have received all the parts.</p>
            <ul>
                {% for chunk_id in chunk_ids %}
                    <li>
                        <a href="{{ url_for('show_text', text_id=chunk_id) }}">Chunk {{ loop.index }}</a>
                        <button onclick="copyToClipboard('{{ chunked_text_cache[chunk_id] }}')">Copy Chunk</button>
                    </li>
                {% endfor %}
            </ul>
            <a href="/">Back to form</a>

            <script>
            function copyToClipboard(text) {
                navigator.clipboard.writeText(text);
            }
            </script>
            ''', chunk_ids=chunk_ids, chunked_text_cache=chunked_text_cache)

    return render_template_string('''
        <form method="post">
            Long Text: <br><textarea name="input_text" rows="10" cols="50"></textarea><br>
            <input type="submit" value="Submit">
        </form>
        ''')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
