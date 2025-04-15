from basicocr import gettext, saveindifferentfile
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import pytesseract
from pytesseract import Output
import cv2
from PIL import Image
import paddleocr
from actualocr import getgoodtext, translate_text
from chat import chatbot
from imgtoexcel import main
from imgtodocx import texttodoc
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
UPLOAD_FOLDER=os.getenv("UPLOAD_FOLDER")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024 # 100 MB

@app.route('/', methods=["GET", "POST"])
def index():
    return render_template('home.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'image' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    try:
        file.save(file_path)
    except Exception as e:
        print(f"Error saving file: {e}")
        return jsonify({'error': 'File not saved'}), 500
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not saved'}), 500
    print(f"File saved at: {file_path}")
    print(f"Files in upload directory: {os.listdir(app.config['UPLOAD_FOLDER'])}")
    mode = request.args.get('mode', 'basic')
    try:
        if mode == 'advanced':
            result_text = getgoodtext(file_path)
        else:
            result_text = gettext(file_path)
    except Exception as e:
        print(f"Error processing file with {mode} mode: {e}")
        return jsonify({'error': f"Error processing image with {mode} mode"}), 500
    print(f"Extracted text ({mode} mode): {result_text}")
    return jsonify({'result': result_text})

@app.route('/translate', methods=['POST'])
def translate_text_route():
    data = request.get_json()
    text = data.get('text')
    lang = data.get('lang')
    if not text or not lang:
        return jsonify({'error': 'Missing text or language'}), 400
    try:
        translated_text = translate_text(text, lang)
    except Exception as e:
        print(f"Error translating text: {e}")
        return jsonify({'error': 'Error translating text'}), 500
    return jsonify({'translated_text': translated_text})

@app.route('/export', methods=['POST'])
def export_to_excel():
    data = request.get_json()
    text = data.get('text')
    
    if not text:
        return jsonify({'error': 'No text to export'}), 400
    
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'exported_text.csv')
    with open(output_path, 'w') as f:
        f.write(text)
    
    return jsonify({'file_url': '/download/exported_text.csv'})

@app.route('/exportToExcel', methods=['POST'])
def img_to_excel():
    if 'image' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    try:
        file.save(file_path)
    except Exception as e:
        print(f"Error saving file: {e}")
        return jsonify({'error': 'File not saved'}), 500
    
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not saved'}), 500
    
    print(f"File saved at: {file_path}")
    print(f"Files in upload directory: {os.listdir(app.config['UPLOAD_FOLDER'])}")
    
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'table_data.csv')
    
    try:
        df = main(file_path, output_path=output_path)
        
        if not os.path.exists(output_path):
            return jsonify({'error': 'Excel conversion failed - output file not created'}), 500
        
        return jsonify({'file_url': '/download/table_data.csv'})
        
    except Exception as e:
        print(f"Error processing file: {e}")
        return jsonify({'error': f"Error processing image: {str(e)}"}), 500

@app.route('/chatbot', methods=['POST'])
def chatbot_route():
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    context = data.get('context', '')
    query = data.get('query', '')
    
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    
    try:
        response = chatbot(context, query)
        
        if not response:
            response = "I couldn't generate a response based on the provided context."
        
        return jsonify({'response': response})
    
    except Exception as e:
        print(f"Error using chatbot: {e}")
        return jsonify({'error': f"Error processing query: {str(e)}"}), 500

@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
    
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)