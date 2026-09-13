import os
import sqlite3
from flask import Flask, render_template_string, request, redirect, url_for, send_from_directory

app = Flask(__name__)
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Database Setup
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            quarter INTEGER NOT NULL,
            photo_filename TEXT NOT NULL,
            summary TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Bucket List Journey</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-gradient: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%);
            --card-bg: #ffffff;
            --text-main: #1e293b;
            --text-sub: #64748b;
            --primary: #4f46e5;
            --shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.08);
            --shadow-hover: 0 20px 35px -5px rgba(79, 70, 229, 0.15);
        }

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Plus Jakarta Sans', sans-serif; }
        
        body {
            background: #f8fafc;
            background-image: 
                radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.12) 0px, transparent 50%),
                radial-gradient(at 100% 100%, rgba(236, 72, 153, 0.1) 0px, transparent 50%);
            background-attachment: fixed;
            color: var(--text-main);
            min-height: 100vh;
            padding-bottom: 80px;
        }

        /* Top Header */
        header {
            text-align: center;
            padding: 4rem 1.5rem 2rem;
        }
        header .badge {
            background: #e0e7ff;
            color: #4338ca;
            padding: 6px 16px;
            border-radius: 30px;
            font-size: 0.85rem;
            font-weight: 700;
            letter-spacing: 0.5px;
            text-transform: uppercase;
            display: inline-block;
            margin-bottom: 1rem;
        }
        header h1 {
            font-size: 2.75rem;
            font-weight: 800;
            color: #0f172a;
            letter-spacing: -1px;
            margin-bottom: 0.75rem;
        }
        header p {
            color: var(--text-sub);
            font-size: 1.15rem;
            max-width: 600px;
            margin: 0 auto;
        }

        /* Sticky Navigation Bar */
        .sticky-bar {
            position: sticky;
            top: 20px;
            z-index: 90;
            max-width: 1000px;
            margin: 0 auto 3rem;
            padding: 0 1.5rem;
        }
        .nav-container {
            background: rgba(255, 255, 255, 0.85);
            backdrop-filter: blur(12px);
            padding: 8px 12px;
            border-radius: 50px;
            border: 1px solid rgba(255, 255, 255, 0.6);
            box-shadow: 0 10px 25px -5px rgba(0,0,0,0.05);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .filter-tabs { display: flex; gap: 6px; }
        .tab-btn {
            background: transparent;
            border: none;
            padding: 10px 20px;
            border-radius: 30px;
            font-weight: 600;
            font-size: 0.9rem;
            color: var(--text-sub);
            cursor: pointer;
            transition: all 0.25s ease;
        }
        .tab-btn:hover { color: var(--text-main); }
        .tab-btn.active {
            background: var(--text-main);
            color: white;
            box-shadow: 0 4px 12px rgba(15, 23, 42, 0.15);
        }

        .add-trigger-btn {
            background: linear-gradient(135deg, #4f46e5, #7c3aed);
            color: white;
            border: none;
            padding: 10px 24px;
            border-radius: 30px;
            font-weight: 700;
            font-size: 0.9rem;
            cursor: pointer;
            box-shadow: 0 4px 14px rgba(79, 70, 229, 0.3);
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .add-trigger-btn:hover {
            transform: scale(1.03);
            box-shadow: 0 6px 20px rgba(79, 70, 229, 0.4);
        }

        /* Cards Layout */
        .cards-grid {
            max-width: 1000px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(310px, 1fr));
            gap: 28px;
            padding: 0 1.5rem;
        }

        .card {
            background: var(--card-bg);
            border-radius: 20px;
            overflow: hidden;
            box-shadow: var(--shadow);
            border: 1px solid #f1f5f9;
            transition: all 0.3s ease;
            display: flex;
            flex-direction: column;
            position: relative;
        }
        .card:hover {
            transform: translateY(-6px);
            box-shadow: var(--shadow-hover);
        }

        .img-wrapper {
            position: relative;
            width: 100%;
            height: 230px;
            overflow: hidden;
            background: #e2e8f0;
        }
        .card-img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.5s ease;
        }
        .card:hover .card-img { transform: scale(1.05); }

        /* Quarter Badges */
        .q-badge {
            position: absolute;
            top: 15px;
            left: 15px;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }
        .q1 { background: #ffe4e6; color: #e11d48; }
        .q2 { background: #dcfce7; color: #16a34a; }
        .q3 { background: #f3e8ff; color: #9333ea; }
        .q4 { background: #fef3c7; color: #d97706; }

        .delete-btn {
            position: absolute;
            top: 15px;
            right: 15px;
            background: rgba(255, 255, 255, 0.85);
            backdrop-filter: blur(4px);
            color: #ef4444;
            border: none;
            width: 32px;
            height: 32px;
            border-radius: 50%;
            font-size: 1.1rem;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: background 0.2s;
        }
        .delete-btn:hover { background: #fee2e2; color: #dc2626; }

        .card-content {
            padding: 1.5rem;
            display: flex;
            flex-direction: column;
            flex-grow: 1;
        }
        .card-title {
            font-size: 1.3rem;
            font-weight: 700;
            color: #0f172a;
            margin-bottom: 0.75rem;
        }
        .card-summary {
            font-size: 0.95rem;
            color: #475569;
            line-height: 1.65;
            flex-grow: 1;
            margin-bottom: 1.25rem;
            text-align: justify;
        }
        .card-footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-top: 1rem;
            border-top: 1px solid #f1f5f9;
            font-size: 0.8rem;
            font-weight: 600;
            color: #94a3b8;
        }

        /* Modal Overlay */
        .modal-overlay {
            display: none;
            position: fixed;
            inset: 0;
            background: rgba(15, 23, 42, 0.4);
            backdrop-filter: blur(8px);
            justify-content: center;
            align-items: center;
            z-index: 100;
            padding: 1rem;
        }
        .modal-card {
            background: white;
            border-radius: 24px;
            width: 100%;
            max-width: 540px;
            padding: 2rem;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
            animation: popIn 0.3s ease-out;
        }
        @keyframes popIn {
            from { transform: scale(0.95); opacity: 0; }
            to { transform: scale(1); opacity: 1; }
        }

        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.5rem;
        }
        .modal-header h2 { font-weight: 800; font-size: 1.5rem; color: #0f172a; }
        .close-icon { background: none; border: none; font-size: 1.5rem; cursor: pointer; color: #94a3b8; }

        .input-group { margin-bottom: 1.2rem; }
        .input-group label { display: block; font-size: 0.85rem; font-weight: 700; color: #334155; margin-bottom: 6px; }
        .form-input {
            width: 100%;
            padding: 12px 16px;
            border-radius: 12px;
            border: 1.5px solid #e2e8f0;
            font-size: 0.95rem;
            outline: none;
            transition: border-color 0.2s;
        }
        .form-input:focus { border-color: var(--primary); }
        textarea.form-input { min-height: 120px; resize: vertical; }

        .word-tracker {
            text-align: right;
            font-size: 0.8rem;
            font-weight: 700;
            color: var(--primary);
            margin-top: 4px;
        }

        .save-btn {
            width: 100%;
            background: var(--primary);
            color: white;
            border: none;
            padding: 14px;
            border-radius: 12px;
            font-weight: 700;
            font-size: 1rem;
            cursor: pointer;
            margin-top: 0.5rem;
        }
        .save-btn:hover { background: #4338ca; }
    </style>
</head>
<body>

    <header>
        <span class="badge">English Project</span>
        <h1>My Bucket List Journal</h1>
        <p>5 unforgettable moments per quarter, complete with personal photo evidence & 200-word reflections.</p>
    </header>

    <div class="sticky-bar">
        <div class="nav-container">
            <div class="filter-tabs">
                <button class="tab-btn active" onclick="filterQ('all', this)">All Items</button>
                <button class="tab-btn" onclick="filterQ('1', this)">Quarter 1</button>
                <button class="tab-btn" onclick="filterQ('2', this)">Quarter 2</button>
                <button class="tab-btn" onclick="filterQ('3', this)">Quarter 3</button>
                <button class="tab-btn" onclick="filterQ('4', this)">Quarter 4</button>
            </div>
            <button class="add-trigger-btn" onclick="showModal()">+ Add Entry</button>
        </div>
    </div>

    <div class="cards-grid">
        {% for item in items %}
        <div class="card item-card q-{{ item[2] }}">
            <div class="img-wrapper">
                <span class="q-badge q{{ item[2] }}">Quarter {{ item[2] }}</span>
                <a href="/delete/{{ item[0] }}" class="delete-btn" onclick="return confirm('Are you sure you want to delete this entry?')" title="Delete entry">&times;</a>
                <img class="card-img" src="{{ url_for('uploaded_file', filename=item[3]) }}" alt="{{ item[1] }}">
            </div>
            <div class="card-content">
                <h3 class="card-title">{{ item[1] }}</h3>
                <p class="card-summary">{{ item[4] }}</p>
                <div class="card-footer">
                    <span>Summary Length</span>
                    <span>{{ item[4].split()|length }} words</span>
                </div>
            </div>
        </div>
        {% else %}
        <div style="grid-column: 1/-1; text-align: center; padding: 4rem 1rem; color: var(--text-sub);">
            <h3>No entries created yet!</h3>
            <p>Click the purple "+ Add Entry" button above to upload your first photo and summary.</p>
        </div>
        {% endfor %}
    </div>

    <!-- Modal Form -->
    <div class="modal-overlay" id="modalOverlay">
        <div class="modal-card">
            <div class="modal-header">
                <h2>New Bucket List Item</h2>
                <button class="close-icon" onclick="hideModal()">&times;</button>
            </div>
            <form action="/add" method="POST" enctype="multipart/form-data">
                <div class="input-group">
                    <label>Incident / Activity Title</label>
                    <input type="text" name="title" class="form-input" placeholder="e.g. Scuba Diving in Key West" required>
                </div>
                <div class="input-group">
                    <label>Select Quarter</label>
                    <select name="quarter" class="form-input" required>
                        <option value="1">Quarter 1</option>
                        <option value="2">Quarter 2</option>
                        <option value="3">Quarter 3</option>
                        <option value="4">Quarter 4</option>
                    </select>
                </div>
                <div class="input-group">
                    <label>Upload Photo Evidence</label>
                    <input type="file" name="photo" class="form-input" accept="image/*" required>
                </div>
                <div class="input-group">
                    <label>200-Word Summary / Incident Story</label>
                    <textarea name="summary" id="summaryArea" class="form-input" placeholder="Write about what happened, how you felt..." oninput="countWords()" required></textarea>
                    <div class="word-tracker" id="wordTracker">0 / 200 words</div>
                </div>
                <button type="submit" class="save-btn">Publish to Journal</button>
            </form>
        </div>
    </div>

    <script>
        function showModal() { document.getElementById('modalOverlay').style.display = 'flex'; }
        function hideModal() { document.getElementById('modalOverlay').style.display = 'none'; }

        function countWords() {
            const text = document.getElementById('summaryArea').value.trim();
            const words = text ? text.split(/\\s+/).length : 0;
            const tracker = document.getElementById('wordTracker');
            tracker.innerText = `${words} / 200 words`;
        }

        function filterQ(quarter, btn) {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            document.querySelectorAll('.item-card').forEach(card => {
                if (quarter === 'all' || card.classList.contains('q-' + quarter)) {
                    card.style.display = 'flex';
                } else {
                    card.style.display = 'none';
                }
            });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM items ORDER BY quarter ASC, id DESC')
    items = cursor.fetchall()
    conn.close()
    return render_template_string(HTML_TEMPLATE, items=items)

@app.route('/add', methods=['POST'])
def add_entry():
    title = request.form.get('title')
    quarter = request.form.get('quarter')
    summary = request.form.get('summary')
    photo = request.files.get('photo')

    if photo and photo.filename != '':
        filename = photo.filename
        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO items (title, quarter, photo_filename, summary) VALUES (?, ?, ?, ?)',
            (title, quarter, filename, summary)
        )
        conn.commit()
        conn.close()

    return redirect(url_for('home'))

@app.route('/delete/<int:item_id>')
def delete_entry(item_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM items WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('home'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

import os
import sqlite3
from flask import Flask, render_template_string, request, redirect, url_for, send_from_directory

app = Flask(__name__)
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Database Setup
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            quarter INTEGER NOT NULL,
            photo_filename TEXT NOT NULL,
            summary TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Bucket List Journey</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-gradient: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%);
            --card-bg: #ffffff;
            --text-main: #1e293b;
            --text-sub: #64748b;
            --primary: #4f46e5;
            --shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.08);
            --shadow-hover: 0 20px 35px -5px rgba(79, 70, 229, 0.15);
        }

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Plus Jakarta Sans', sans-serif; }
        
        body {
            background: #f8fafc;
            background-image: 
                radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.12) 0px, transparent 50%),
                radial-gradient(at 100% 100%, rgba(236, 72, 153, 0.1) 0px, transparent 50%);
            background-attachment: fixed;
            color: var(--text-main);
            min-height: 100vh;
            padding-bottom: 80px;
        }

        /* Top Header */
        header {
            text-align: center;
            padding: 4rem 1.5rem 2rem;
        }
        header .badge {
            background: #e0e7ff;
            color: #4338ca;
            padding: 6px 16px;
            border-radius: 30px;
            font-size: 0.85rem;
            font-weight: 700;
            letter-spacing: 0.5px;
            text-transform: uppercase;
            display: inline-block;
            margin-bottom: 1rem;
        }
        header h1 {
            font-size: 2.75rem;
            font-weight: 800;
            color: #0f172a;
            letter-spacing: -1px;
            margin-bottom: 0.75rem;
        }
        header p {
            color: var(--text-sub);
            font-size: 1.15rem;
            max-width: 600px;
            margin: 0 auto;
        }

        /* Sticky Navigation Bar */
        .sticky-bar {
            position: sticky;
            top: 20px;
            z-index: 90;
            max-width: 1000px;
            margin: 0 auto 3rem;
            padding: 0 1.5rem;
        }
        .nav-container {
            background: rgba(255, 255, 255, 0.85);
            backdrop-filter: blur(12px);
            padding: 8px 12px;
            border-radius: 50px;
            border: 1px solid rgba(255, 255, 255, 0.6);
            box-shadow: 0 10px 25px -5px rgba(0,0,0,0.05);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .filter-tabs { display: flex; gap: 6px; }
        .tab-btn {
            background: transparent;
            border: none;
            padding: 10px 20px;
            border-radius: 30px;
            font-weight: 600;
            font-size: 0.9rem;
            color: var(--text-sub);
            cursor: pointer;
            transition: all 0.25s ease;
        }
        .tab-btn:hover { color: var(--text-main); }
        .tab-btn.active {
            background: var(--text-main);
            color: white;
            box-shadow: 0 4px 12px rgba(15, 23, 42, 0.15);
        }

        .add-trigger-btn {
            background: linear-gradient(135deg, #4f46e5, #7c3aed);
            color: white;
            border: none;
            padding: 10px 24px;
            border-radius: 30px;
            font-weight: 700;
            font-size: 0.9rem;
            cursor: pointer;
            box-shadow: 0 4px 14px rgba(79, 70, 229, 0.3);
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .add-trigger-btn:hover {
            transform: scale(1.03);
            box-shadow: 0 6px 20px rgba(79, 70, 229, 0.4);
        }

        /* Cards Layout */
        .cards-grid {
            max-width: 1000px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(310px, 1fr));
            gap: 28px;
            padding: 0 1.5rem;
        }

        .card {
            background: var(--card-bg);
            border-radius: 20px;
            overflow: hidden;
            box-shadow: var(--shadow);
            border: 1px solid #f1f5f9;
            transition: all 0.3s ease;
            display: flex;
            flex-direction: column;
            position: relative;
        }
        .card:hover {
            transform: translateY(-6px);
            box-shadow: var(--shadow-hover);
        }

        .img-wrapper {
            position: relative;
            width: 100%;
            height: 230px;
            overflow: hidden;
            background: #e2e8f0;
        }
        .card-img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.5s ease;
        }
        .card:hover .card-img { transform: scale(1.05); }

        /* Quarter Badges */
        .q-badge {
            position: absolute;
            top: 15px;
            left: 15px;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }
        .q1 { background: #ffe4e6; color: #e11d48; }
        .q2 { background: #dcfce7; color: #16a34a; }
        .q3 { background: #f3e8ff; color: #9333ea; }
        .q4 { background: #fef3c7; color: #d97706; }

        .delete-btn {
            position: absolute;
            top: 15px;
            right: 15px;
            background: rgba(255, 255, 255, 0.85);
            backdrop-filter: blur(4px);
            color: #ef4444;
            border: none;
            width: 32px;
            height: 32px;
            border-radius: 50%;
            font-size: 1.1rem;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: background 0.2s;
        }
        .delete-btn:hover { background: #fee2e2; color: #dc2626; }

        .card-content {
            padding: 1.5rem;
            display: flex;
            flex-direction: column;
            flex-grow: 1;
        }
        .card-title {
            font-size: 1.3rem;
            font-weight: 700;
            color: #0f172a;
            margin-bottom: 0.75rem;
        }
        .card-summary {
            font-size: 0.95rem;
            color: #475569;
            line-height: 1.65;
            flex-grow: 1;
            margin-bottom: 1.25rem;
            text-align: justify;
        }
        .card-footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-top: 1rem;
            border-top: 1px solid #f1f5f9;
            font-size: 0.8rem;
            font-weight: 600;
            color: #94a3b8;
        }

        /* Modal Overlay */
        .modal-overlay {
            display: none;
            position: fixed;
            inset: 0;
            background: rgba(15, 23, 42, 0.4);
            backdrop-filter: blur(8px);
            justify-content: center;
            align-items: center;
            z-index: 100;
            padding: 1rem;
        }
        .modal-card {
            background: white;
            border-radius: 24px;
            width: 100%;
            max-width: 540px;
            padding: 2rem;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
            animation: popIn 0.3s ease-out;
        }
        @keyframes popIn {
            from { transform: scale(0.95); opacity: 0; }
            to { transform: scale(1); opacity: 1; }
        }

        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.5rem;
        }
        .modal-header h2 { font-weight: 800; font-size: 1.5rem; color: #0f172a; }
        .close-icon { background: none; border: none; font-size: 1.5rem; cursor: pointer; color: #94a3b8; }

        .input-group { margin-bottom: 1.2rem; }
        .input-group label { display: block; font-size: 0.85rem; font-weight: 700; color: #334155; margin-bottom: 6px; }
        .form-input {
            width: 100%;
            padding: 12px 16px;
            border-radius: 12px;
            border: 1.5px solid #e2e8f0;
            font-size: 0.95rem;
            outline: none;
            transition: border-color 0.2s;
        }
        .form-input:focus { border-color: var(--primary); }
        textarea.form-input { min-height: 120px; resize: vertical; }

        .word-tracker {
            text-align: right;
            font-size: 0.8rem;
            font-weight: 700;
            color: var(--primary);
            margin-top: 4px;
        }

        .save-btn {
            width: 100%;
            background: var(--primary);
            color: white;
            border: none;
            padding: 14px;
            border-radius: 12px;
            font-weight: 700;
            font-size: 1rem;
            cursor: pointer;
            margin-top: 0.5rem;
        }
        .save-btn:hover { background: #4338ca; }
    </style>
</head>
<body>

    <header>
        <span class="badge">English Project</span>
        <h1>My Bucket List Journal</h1>
        <p>5 unforgettable moments per quarter, complete with personal photo evidence & 200-word reflections.</p>
    </header>

    <div class="sticky-bar">
        <div class="nav-container">
            <div class="filter-tabs">
                <button class="tab-btn active" onclick="filterQ('all', this)">All Items</button>
                <button class="tab-btn" onclick="filterQ('1', this)">Quarter 1</button>
                <button class="tab-btn" onclick="filterQ('2', this)">Quarter 2</button>
                <button class="tab-btn" onclick="filterQ('3', this)">Quarter 3</button>
                <button class="tab-btn" onclick="filterQ('4', this)">Quarter 4</button>
            </div>
            <button class="add-trigger-btn" onclick="showModal()">+ Add Entry</button>
        </div>
    </div>

    <div class="cards-grid">
        {% for item in items %}
        <div class="card item-card q-{{ item[2] }}">
            <div class="img-wrapper">
                <span class="q-badge q{{ item[2] }}">Quarter {{ item[2] }}</span>
                <a href="/delete/{{ item[0] }}" class="delete-btn" onclick="return confirm('Are you sure you want to delete this entry?')" title="Delete entry">&times;</a>
                <img class="card-img" src="{{ url_for('uploaded_file', filename=item[3]) }}" alt="{{ item[1] }}">
            </div>
            <div class="card-content">
                <h3 class="card-title">{{ item[1] }}</h3>
                <p class="card-summary">{{ item[4] }}</p>
                <div class="card-footer">
                    <span>Summary Length</span>
                    <span>{{ item[4].split()|length }} words</span>
                </div>
            </div>
        </div>
        {% else %}
        <div style="grid-column: 1/-1; text-align: center; padding: 4rem 1rem; color: var(--text-sub);">
            <h3>No entries created yet!</h3>
            <p>Click the purple "+ Add Entry" button above to upload your first photo and summary.</p>
        </div>
        {% endfor %}
    </div>

    <!-- Modal Form -->
    <div class="modal-overlay" id="modalOverlay">
        <div class="modal-card">
            <div class="modal-header">
                <h2>New Bucket List Item</h2>
                <button class="close-icon" onclick="hideModal()">&times;</button>
            </div>
            <form action="/add" method="POST" enctype="multipart/form-data">
                <div class="input-group">
                    <label>Incident / Activity Title</label>
                    <input type="text" name="title" class="form-input" placeholder="e.g. Scuba Diving in Key West" required>
                </div>
                <div class="input-group">
                    <label>Select Quarter</label>
                    <select name="quarter" class="form-input" required>
                        <option value="1">Quarter 1</option>
                        <option value="2">Quarter 2</option>
                        <option value="3">Quarter 3</option>
                        <option value="4">Quarter 4</option>
                    </select>
                </div>
                <div class="input-group">
                    <label>Upload Photo Evidence</label>
                    <input type="file" name="photo" class="form-input" accept="image/*" required>
                </div>
                <div class="input-group">
                    <label>200-Word Summary / Incident Story</label>
                    <textarea name="summary" id="summaryArea" class="form-input" placeholder="Write about what happened, how you felt..." oninput="countWords()" required></textarea>
                    <div class="word-tracker" id="wordTracker">0 / 200 words</div>
                </div>
                <button type="submit" class="save-btn">Publish to Journal</button>
            </form>
        </div>
    </div>

    <script>
        function showModal() { document.getElementById('modalOverlay').style.display = 'flex'; }
        function hideModal() { document.getElementById('modalOverlay').style.display = 'none'; }

        function countWords() {
            const text = document.getElementById('summaryArea').value.trim();
            const words = text ? text.split(/\\s+/).length : 0;
            const tracker = document.getElementById('wordTracker');
            tracker.innerText = `${words} / 200 words`;
        }

        function filterQ(quarter, btn) {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            document.querySelectorAll('.item-card').forEach(card => {
                if (quarter === 'all' || card.classList.contains('q-' + quarter)) {
                    card.style.display = 'flex';
                } else {
                    card.style.display = 'none';
                }
            });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM items ORDER BY quarter ASC, id DESC')
    items = cursor.fetchall()
    conn.close()
    return render_template_string(HTML_TEMPLATE, items=items)

@app.route('/add', methods=['POST'])
def add_entry():
    title = request.form.get('title')
    quarter = request.form.get('quarter')
    summary = request.form.get('summary')
    photo = request.files.get('photo')

    if photo and photo.filename != '':
        filename = photo.filename
        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO items (title, quarter, photo_filename, summary) VALUES (?, ?, ?, ?)',
            (title, quarter, filename, summary)
        )
        conn.commit()
        conn.close()

    return redirect(url_for('home'))

@app.route('/delete/<int:item_id>')
def delete_entry(item_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM items WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('home'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)