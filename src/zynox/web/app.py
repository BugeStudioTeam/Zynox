"""Flask web application for ZynoxAI - Static files version"""

import os
import sys
import json
import subprocess
import io
import zipfile
import time
import threading
import requests
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file, Response, stream_with_context, send_from_directory
from contextlib import redirect_stdout

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from zynox.cli import ZynoxAI
from zynox.config import Config
from zynox.memory.session import SessionManager
from zynox.core.file.manager import FileManager

# Get directories
WEB_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(WEB_DIR, 'static')

# Create directories if not exist
os.makedirs(STATIC_DIR, exist_ok=True)

# Download icons from GitHub
ICON_URLS = {
    'folder': 'https://raw.githubusercontent.com/BugeStudioTeam/Zynox/refs/heads/main/images/icons/folder.png',
    'zip': 'https://raw.githubusercontent.com/BugeStudioTeam/Zynox/refs/heads/main/images/icons/zip.png',
    'file': 'https://raw.githubusercontent.com/BugeStudioTeam/Zynox/refs/heads/main/images/icons/file.png'
}

def download_icon(name, url):
    """Download icon from URL to static directory"""
    icon_path = os.path.join(STATIC_DIR, f'{name}.png')
    if not os.path.exists(icon_path):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                with open(icon_path, 'wb') as f:
                    f.write(response.content)
                print(f"[Downloaded icon: {name}.png]")
            else:
                print(f"[Failed to download {name}.png: HTTP {response.status_code}]")
        except Exception as e:
            print(f"[Error downloading {name}.png: {e}]")

# Download icons on startup
for name, url in ICON_URLS.items():
    download_icon(name, url)

# Global ZynoxAI instance
zynox = None
config = None
session_manager = None
file_manager = None

# Global current directory for terminal
global_cwd = os.path.expanduser("~")

# Global stop flag for current task
stop_task_flag = False


def create_app():
    """Create Flask app with static files"""
    global zynox, config, session_manager, file_manager, global_cwd, stop_task_flag
    
    # Initialize ZynoxAI components
    zynox = ZynoxAI()
    config = Config()
    session_manager = SessionManager()
    file_manager = FileManager()
    global_cwd = os.path.expanduser("~")
    stop_task_flag = False
    
    app = Flask(__name__, static_folder=None)
    app.config['SECRET_KEY'] = 'zynoxai-secret'
    
    # Serve static files
    @app.route('/static/<path:filename>')
    def serve_static(filename):
        return send_from_directory(STATIC_DIR, filename)
    
    @app.route('/styles/<path:filename>')
    def serve_styles(filename):
        return send_from_directory(os.path.join(WEB_DIR, 'styles'), filename)
    
    @app.route('/js/<path:filename>')
    def serve_js(filename):
        return send_from_directory(os.path.join(WEB_DIR, 'js'), filename)
    
    @app.route('/icon.png')
    def serve_icon():
        return send_from_directory(WEB_DIR, 'icon.png')
    
    @app.route('/')
    def index():
        return send_from_directory(WEB_DIR, 'index.html')
    
    @app.route('/dashboard')
    def dashboard():
        return send_from_directory(WEB_DIR, 'index.html')
    
    @app.route('/chat')
    def chat():
        return send_from_directory(WEB_DIR, 'index.html')
    
    @app.route('/settings')
    def settings():
        return send_from_directory(WEB_DIR, 'index.html')
    
    @app.route('/api/pwd')
    def api_pwd():
        global global_cwd
        return jsonify({'cwd': global_cwd})
    
    @app.route('/api/cd', methods=['POST'])
    def api_cd():
        global global_cwd
        data = request.json
        path = data.get('path', '')
        
        try:
            if path == '~' or path == '':
                new_path = os.path.expanduser("~")
            elif path.startswith('/'):
                new_path = path
            else:
                new_path = os.path.normpath(os.path.join(global_cwd, path))
            
            if os.path.exists(new_path) and os.path.isdir(new_path):
                global_cwd = new_path
                return jsonify({'success': True, 'cwd': global_cwd})
            else:
                return jsonify({'success': False, 'error': 'Directory not found'})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    
    @app.route('/api/status')
    def api_status():
        return jsonify({
            'status': 'running',
            'provider': zynox.current_provider,
            'environment': zynox.environment,
            'package_manager': zynox.package_manager,
            'version': '3.6.8'
        })
    
    @app.route('/api/stop', methods=['POST'])
    def api_stop():
        global stop_task_flag
        stop_task_flag = True
        return jsonify({'success': True})
    
    @app.route('/api/files/list')
    def api_files_list():
        create_dir = Config.get_create_dir()
        files = []
        
        def scan_directory(path, relative_path=""):
            try:
                for item in os.listdir(path):
                    item_path = os.path.join(path, item)
                    rel_path = os.path.join(relative_path, item) if relative_path else item
                    if os.path.isdir(item_path):
                        files.append({'name': item, 'path': rel_path, 'is_dir': True, 'size': 0})
                        scan_directory(item_path, rel_path)
                    else:
                        files.append({'name': item, 'path': rel_path, 'is_dir': False, 'size': os.path.getsize(item_path)})
            except Exception as e:
                print(f"Error scanning: {e}")
        
        if os.path.exists(create_dir):
            scan_directory(create_dir)
        
        return jsonify({'files': files})
    
    @app.route('/api/files/download')
    def api_file_download():
        filepath = request.args.get('path', '')
        create_dir = Config.get_create_dir()
        full_path = os.path.join(create_dir, filepath)
        
        if not os.path.exists(full_path) or os.path.isdir(full_path):
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(full_path, as_attachment=True, download_name=os.path.basename(full_path))
    
    @app.route('/api/folder/download')
    def api_folder_download():
        folderpath = request.args.get('path', '')
        create_dir = Config.get_create_dir()
        full_path = os.path.join(create_dir, folderpath)
        
        if not os.path.exists(full_path) or not os.path.isdir(full_path):
            return jsonify({'error': 'Folder not found'}), 404
        
        zip_buffer = io.BytesIO()
        folder_name = os.path.basename(full_path)
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for root, dirs, files in os.walk(full_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, os.path.dirname(full_path))
                    zip_file.write(file_path, arcname)
        
        zip_buffer.seek(0)
        return send_file(zip_buffer, as_attachment=True, download_name=f'{folder_name}.zip', mimetype='application/zip')
    
    @app.route('/api/files/download-all')
    def api_files_download_all():
        create_dir = Config.get_create_dir()
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            if os.path.exists(create_dir):
                for root, dirs, files in os.walk(create_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, create_dir)
                        zip_file.write(file_path, arcname)
        
        zip_buffer.seek(0)
        return send_file(zip_buffer, as_attachment=True, download_name='zynoxai_created_files.zip', mimetype='application/zip')
    
    @app.route('/api/sessions')
    def api_sessions():
        sessions = session_manager.list_sessions()
        return jsonify({'sessions': sessions})
    
    @app.route('/api/created')
    def api_created():
        files = file_manager.list_created_files()
        return jsonify({'files': files})
    
    @app.route('/api/config', methods=['GET', 'POST'])
    def api_config():
        if request.method == 'POST':
            data = request.json
            if 'default_provider' in data:
                config.set_default_provider(data['default_provider'])
                zynox.current_provider = data['default_provider']
            if 'default_model' in data:
                config.set_default_model(data['default_model'])
            if 'api_keys' in data:
                for provider, key in data['api_keys'].items():
                    if key:
                        config.set_api_key(provider, key)
            return jsonify({'success': True})
        return jsonify({
            'default_provider': config.get_default_provider(),
            'default_model': config.get_default_model(),
            'api_keys': list(config.data.get('api_keys', {}).keys())
        })
    
    @app.route('/api/sessions/new', methods=['POST'])
    def api_new_session():
        session_manager.new_session()
        return jsonify({'success': True})
    
    @app.route('/api/sessions/clear', methods=['POST'])
    def api_clear_memory():
        session_manager.clear_memory()
        return jsonify({'success': True})
    
    @app.route('/api/sessions/load', methods=['POST'])
    def api_load_session():
        data = request.json
        session_id = data.get('session_id')
        if session_manager.load_session(session_id):
            return jsonify({'success': True})
        return jsonify({'success': False, 'error': 'Session not found'})
    
    @app.route('/api/sessions/delete', methods=['POST'])
    def api_delete_session():
        data = request.json
        session_id = data.get('session_id')
        if session_manager.delete_session(session_id):
            return jsonify({'success': True})
        return jsonify({'success': False})
    
    @app.route('/api/clear-created', methods=['POST'])
    def api_clear_created():
        file_manager.clear_created_files()
        return jsonify({'success': True})
    
    @app.route('/api/command', methods=['POST'])
    def api_command():
        global global_cwd
        data = request.json
        command = data.get('command', '')
        cwd = data.get('cwd', global_cwd)
        
        if command.strip().startswith('zynox'):
            return jsonify({'stdout': 'Use standard Linux commands.', 'stderr': '', 'returncode': 0})
        
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30, executable='/bin/bash', cwd=cwd)
            return jsonify({'stdout': result.stdout, 'stderr': result.stderr, 'returncode': result.returncode})
        except subprocess.TimeoutExpired:
            return jsonify({'stderr': 'Timeout', 'returncode': -1})
        except Exception as e:
            return jsonify({'stderr': str(e), 'returncode': -1})
    
    @app.route('/api/chat/stream', methods=['POST'])
    def api_chat_stream():
        global stop_task_flag
        stop_task_flag = False

        # Handle both FormData (with files) and JSON (no files)
        user_msg = ''
        uploaded_files_info = []

        if request.content_type and 'multipart/form-data' in request.content_type:
            user_msg = request.form.get('message', '')
            uploaded_files = request.files.getlist('files')
        else:
            data = request.json or {}
            user_msg = data.get('message', '')
            uploaded_files = []

        # Save uploaded files to workspace
        create_dir = Config.get_create_dir()
        os.makedirs(create_dir, exist_ok=True)

        for uploaded_file in uploaded_files:
            if uploaded_file and uploaded_file.filename:
                safe_name = os.path.basename(uploaded_file.filename)
                save_path = os.path.join(create_dir, safe_name)
                uploaded_file.save(save_path)
                file_size = os.path.getsize(save_path)
                uploaded_files_info.append({
                    'name': safe_name,
                    'path': safe_name,
                    'size': file_size,
                    'is_dir': False
                })
                print(f"[Uploaded: {safe_name} ({file_size} bytes)]")

        # If files were uploaded and no message, auto-generate a task message
        if not user_msg and uploaded_files_info:
            file_names = ', '.join(f['name'] for f in uploaded_files_info)
            user_msg = f"Files uploaded: {file_names}. Please analyze these files."

        def generate():
            from ..core.executor.step_executor import StepExecutor

            files_before = set()
            if os.path.exists(create_dir):
                for root, dirs, files in os.walk(create_dir):
                    for file in files:
                        rel_path = os.path.relpath(os.path.join(root, file), create_dir)
                        files_before.add(rel_path)

            output_queue = []
            created_files = []

            def callback(text, color="white"):
                output_queue.append(text)

            executor = StepExecutor(zynox, callback)

            success = False
            exception = None

            def run_task():
                nonlocal success, exception
                try:
                    if not stop_task_flag:
                        success = executor.run(user_msg, ".")
                except Exception as e:
                    if "stopped" not in str(e):
                        exception = str(e)

            thread = threading.Thread(target=run_task)
            thread.start()

            while thread.is_alive():
                if stop_task_flag:
                    yield f"data: {json.dumps({'text': '\\n⚠️ Task stopped by user\\n', 'complete': True})}\n\n"
                    return
                if output_queue:
                    for line in output_queue:
                        yield f"data: {json.dumps({'text': line})}\n\n"
                    output_queue.clear()
                time.sleep(0.05)

            if output_queue:
                for line in output_queue:
                    yield f"data: {json.dumps({'text': line})}\n\n"

            if not stop_task_flag:
                if os.path.exists(create_dir):
                    for root, dirs, files in os.walk(create_dir):
                        for file in files:
                            rel_path = os.path.relpath(os.path.join(root, file), create_dir)
                            if rel_path not in files_before:
                                full_path = os.path.join(root, file)
                                created_files.append({
                                    'name': file,
                                    'path': rel_path,
                                    'size': os.path.getsize(full_path),
                                    'is_dir': False
                                })
                        for dir_name in dirs:
                            rel_path = os.path.relpath(os.path.join(root, dir_name), create_dir)
                            if rel_path not in files_before:
                                created_files.append({
                                    'name': dir_name,
                                    'path': rel_path,
                                    'size': 0,
                                    'is_dir': True
                                })

                if created_files:
                    yield f"data: {json.dumps({'created_files': created_files})}\n\n"

            if exception:
                yield f"data: {json.dumps({'error': exception, 'complete': True})}\n\n"
            elif stop_task_flag:
                yield f"data: {json.dumps({'complete': True, 'success': False, 'stopped': True})}\n\n"
            else:
                yield f"data: {json.dumps({'complete': True, 'success': success})}\n\n"

        return Response(stream_with_context(generate()), mimetype='text/event-stream')
    
    @app.route('/api/chat', methods=['POST'])
    def api_chat():
        global stop_task_flag
        stop_task_flag = False
        
        # Handle both FormData and JSON
        if request.content_type and 'multipart/form-data' in request.content_type:
            user_msg = request.form.get('message', '')
            uploaded_files = request.files.getlist('files')
        else:
            data = request.json or {}
            user_msg = data.get('message', '')
            uploaded_files = []
        
        # Save uploaded files
        create_dir = Config.get_create_dir()
        os.makedirs(create_dir, exist_ok=True)
        for uploaded_file in uploaded_files:
            if uploaded_file and uploaded_file.filename:
                safe_name = os.path.basename(uploaded_file.filename)
                save_path = os.path.join(create_dir, safe_name)
                uploaded_file.save(save_path)
        
        files_before = set()
        folders_before = set()
        if os.path.exists(create_dir):
            for root, dirs, files in os.walk(create_dir):
                for file in files:
                    rel_path = os.path.relpath(os.path.join(root, file), create_dir)
                    files_before.add(rel_path)
                for dir_name in dirs:
                    rel_path = os.path.relpath(os.path.join(root, dir_name), create_dir)
                    folders_before.add(rel_path)
        
        output_buffer = io.StringIO()
        
        with redirect_stdout(output_buffer):
            zynox.memory.add_message("user", user_msg)
            zynox.task_complete = False
            
            file_list = zynox.file_manager.list_files(".")
            prompt = zynox.create_prompt(user_msg, "", file_list)
            response = zynox.call_api(zynox.current_provider, prompt)
            
            if response:
                zynox.memory.add_message("assistant", response[:300])
                zynox.parse_and_execute(response, ".")
        
        result = output_buffer.getvalue()
        if not result or len(result.strip()) == 0:
            result = "Task completed"
        
        created_items = []
        if os.path.exists(create_dir):
            for root, dirs, files in os.walk(create_dir):
                for file in files:
                    rel_path = os.path.relpath(os.path.join(root, file), create_dir)
                    if rel_path not in files_before:
                        full_path = os.path.join(root, file)
                        created_items.append({
                            'name': file,
                            'path': rel_path,
                            'size': os.path.getsize(full_path),
                            'is_dir': False
                        })
                for dir_name in dirs:
                    rel_path = os.path.relpath(os.path.join(root, dir_name), create_dir)
                    if rel_path not in folders_before:
                        created_items.append({
                            'name': dir_name,
                            'path': rel_path,
                            'size': 0,
                            'is_dir': True
                        })
        
        return jsonify({
            'response': result,
            'created_files': created_items
        })
    
    return app


def run_web_server(host='127.0.0.1', port=5000, debug=False):
    """Run web server"""
    app = create_app()
    print(f"\n[Web Server Started]")
    print(f"[Access at: http://{host}:{port}]")
    print(f"[Press Ctrl+C to stop]\n")
    app.run(host=host, port=port, debug=debug, threaded=True)


if __name__ == '__main__':
    run_web_server()