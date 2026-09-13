import os
import sqlite3
from flask import Flask, render_template_string, request, redirect, url_for, send_from_directory

app = Flask(__name__)
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

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
            --card-bg: #ffffff;
            --text-main: #1e293b;
            --text-sub: #64748b;
            --primary: #4f46e5;
            --shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.08);
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

        header { text-align: center; padding: 3rem 1.5rem 1.5rem; }
        header .badge { background: #e0e7ff; color: #4338ca; padding: 6px 16px; border-radius: 30px; font-size: 0.85rem; font-weight: 700; text-transform: uppercase; display: inline-block; margin-bottom: 0.75rem; }
        header h1 { font-size: 2.5rem; font-weight: 800; color: #0f172a; margin-bottom: 0.5rem; }

        .sticky-bar { position: sticky; top: 20px; z-index: 90; max-width: 1000px; margin: 0 auto 2rem; padding: 0 1.5rem; }
        .nav-container { background: rgba(255, 255, 255, 0.85); backdrop-filter: blur(12px); padding: 8px 16px; border-radius: 50px; border: 1px solid rgba(255, 255, 255, 0.6); box-shadow: 0 10px 25px -5px rgba(0,0,0,0.05); display: flex; justify-content: space-between; align-items: center; }
        
        .add-trigger-btn { background: linear-gradient(135deg, #4f46e5, #7c3aed); color: white; border: none; padding: 10px 24px; border-radius: 30px; font-weight: 700; cursor: pointer; }

        .cards-grid { max-width: 1000px; margin: 0 auto; display: grid; grid-template-columns: repeat(auto-fill, minmax(310px, 1fr)); gap: 28px; padding: 0 1.5rem; }
        .card { background: var(--card-bg); border-radius: 20px; overflow: hidden; box-shadow: var(--shadow); border: 1px solid #f1f5f9; display: flex; flex-direction: column; position: relative; }

        /* Multi-Image Gallery Grid */
        .img-gallery { display: grid; grid-template-columns: repeat(auto-fit, minmax(50%, 1fr)); gap: 2px; height: 230px; background: #e2e8f0; overflow: hidden; position: relative; }
        .gallery-img { width: 100%; height: 100%; object-fit: cover; }

        .q-badge { position: absolute; top: 12px; left: 12px; padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 800; z-index: 2; }
        .q1 { background: #ffe4e6; color: #e11d48; } .q2 { background: #dcfce7; color: #16a34a; }
        .q3 { background: #f3e8ff; color: #9333ea; } .q4 { background: #fef3c7; color: #d97706; }

        .actions { position: absolute; top: 12px; right: 12px; display: flex; gap: 6px; z-index: 2; }
        .action-btn { background: rgba(255, 255, 255, 0.9); border: none; width: 32px; height: 32px; border-radius: 50%; font-size: 0.9rem; cursor: pointer; display: flex; align-items: center; justify-content: center; text-decoration: none; color: #334155; }
        .action-btn:hover { background: #ffffff; }

        .card-content { padding: 1.5rem; display: flex; flex-direction: column; flex-grow: 1; }
        .card-title { font-size: 1.25rem; font-weight: 700; color: #0f172a; margin-bottom: 0.5rem; }
        .card-summary { font-size: 0.95rem; color: #475569; line-height: 1.6; flex-grow: 1; margin-bottom: 1rem; }

        /* Modal Overlay */
        .modal-overlay { display: none; position: fixed; inset: 0; background: rgba(15, 23, 42, 0.4); backdrop-filter: blur(8px); justify-content: center; align-items: center; z-index: 100; padding: 1rem; }
        .modal-card { background: white; border-radius: 24px; width: 100%; max-width: 540px; padding: 2rem; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25); }
        
        .input-group { margin-bottom: 1rem; }
        .input-group label { display: block; font-size: 0.85rem; font-weight: 700; color: #334155; margin-bottom: 4px; }
        .form-input { width: 100%; padding: 10px 14px; border-radius: 10px; border: 1.5px solid #e2e8f0; font-size: 0.95rem; }
        textarea.form-input { min-height: 110px; resize: vertical; }

        .save-btn { width: 100%; background: var(--primary); color: white; border: none; padding: 12px; border-radius: 10px; font-weight: 700; font-size: 1rem; cursor: pointer; }
    </style>
</head>
<body>

    <header>
        <span class="badge">English Project</span>
        <h1>My Bucket List Journal</h1>
    </header>

    <div class="sticky-bar">
        <div class="nav-container">
            <h3 style="font-size: 1rem; color: #334155;">Entries Gallery</h3>
            <button class="add-trigger-btn" onclick="openAddModal()">+ Add Entry</button>
        </div>
    </div>

    <div class="cards-grid">
        {% for item in items %}
        {% set photos = item[3].split(',') %}
        <div class="card">
            <span class="q-badge q{{ item[2] }}">Q{{ item[2] }}</span>
            <div class="actions">
                <button class="action-btn" onclick="openEditModal('{{ item[0] }}', '{{ item[1] }}', '{{ item[2] }}', '{{ item[4]|replace('\\n', ' ') }}')" title="Edit Post">✏️</button>
                <a href="/delete/{{ item[0] }}" class="action-btn" onclick="return confirm('Delete entry?')" title="Delete Post">🗑️</a>
            </div>
            
            <div class="img-gallery">
                {% for img in photos %}
                <img class="gallery-img" src="{{ url_for('uploaded_file', filename=img) }}" alt="Photo">
                {% endfor %}
            </div>

            <div class="card-content">
                <h3 class="card-title">{{ item[1] }}</h3>
                <p class="card-summary">{{ item[4] }}</p>
            </div>
        </div>
        {% endfor %}
    </div>

    <!-- Modal Form (Handles Add & Edit) -->
    <div class="modal-overlay" id="modalOverlay">
        <div class="modal-card">
            <h2 id="modalTitle" style="margin-bottom: 1rem;">New Bucket List Item</h2>
            <form id="entryForm" action="/add" method="POST" enctype="multipart/form-data">
                <div class="input-group">
                    <label>Title</label>
                    <input type="text" name="title" id="formTitle" class="form-input" required>
                </div>
                <div class="input-group">
                    <label>Quarter</label>
                    <select name="quarter" id="formQuarter" class="form-input" required>
                        <option value="1">Quarter 1</option>
                        <option value="2">Quarter 2</option>
                        <option value="3">Quarter 3</option>
                        <option value="4">Quarter 4</option>
                    </select>
                </div>
                <div class="input-group">
                    <label>Upload Photo(s) <span style="font-weight: 400; color: #64748b;">(Hold Ctrl/Cmd to choose multiple)</span></label>
                    <input type="file" name="photos" class="form-input" accept="image/*" multiple id="formPhotos">
                </div>
                <div class="input-group">
                    <label>Summary</label>
                    <textarea name="summary" id="formSummary" class="form-input" required></textarea>
                </div>
                <button type="submit" class="save-btn">Save Entry</button>
                <button type="button" onclick="closeModal()" style="width: 100%; background: none; border: none; margin-top: 8px; color: #64748b; cursor: pointer;">Cancel</button>
            </form>
        </div>
    </div>

    <script>
        function openAddModal() {
            document.getElementById('modalTitle').innerText = 'New Bucket List Item';
            document.getElementById('entryForm').action = '/add';
            document.getElementById('formTitle').value = '';
            document.getElementById('formQuarter').value = '1';
            document.getElementById('formSummary').value = '';
            document.getElementById('formPhotos').required = true;
            document.getElementById('modalOverlay').style.display = 'flex';
        }

        function openEditModal(id, title, quarter, summary) {
            document.getElementById('modalTitle').innerText = 'Edit Bucket List Item';
            document.getElementById('entryForm').action = '/edit/' + id;
            document.getElementById('formTitle').value = title;
            document.getElementById('formQuarter').value = quarter;
            document.getElementById('formSummary').value = summary;
            document.getElementById('formPhotos').required = false; // Optional to upload new photos when editing
            document.getElementById('modalOverlay').style.display = 'flex';
        }

        function closeModal() { document.getElementById('modalOverlay').style.display = 'none'; }
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
    photos = request.files.getlist('photos')

    saved_filenames = []
    for photo in photos:
        if photo and photo.filename != '':
            filename = photo.filename
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            saved_filenames.append(filename)

    filenames_str = ",".join(saved_filenames)
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO items (title, quarter, photo_filename, summary) VALUES (?, ?, ?, ?)',
        (title, quarter, filenames_str, summary)
    )
    conn.commit()
    conn.close()

    return redirect(url_for('home'))

@app.route('/edit/<int:item_id>', methods=['POST'])
def edit_entry(item_id):
    title = request.form.get('title')
    quarter = request.form.get('quarter')
    summary = request.form.get('summary')
    photos = request.files.getlist('photos')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # If new photos are uploaded during edit, save them and update filenames
    saved_filenames = []
    for photo in photos:
        if photo and photo.filename != '':
            filename = photo.filename
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            saved_filenames.append(filename)

    if saved_filenames:
        filenames_str = ",".join(saved_filenames)
        cursor.execute(
            'UPDATE items SET title = ?, quarter = ?, photo_filename = ?, summary = ? WHERE id = ?',
            (title, quarter, filenames_str, summary, item_id)
        )
    else:
        cursor.execute(
            'UPDATE items SET title = ?, quarter = ?, summary = ? WHERE id = ?',
            (title, quarter, summary, item_id)
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
    app.run(debug=True)
