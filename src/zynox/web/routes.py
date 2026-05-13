"""API routes for web interface"""

import json
import os
import subprocess
from flask import render_template, request, jsonify, session
from flask_socketio import emit
from ..config import Config
from ..core.file.manager import FileManager
from ..core.file.search import FileSearcher

file_manager = FileManager()
file_searcher = FileSearcher()

def init_routes(app, zynox_instance, socketio):
    """Initialize all routes"""
    
    @app.route('/')
    def index():
        """Main page"""
        return render_template('index.html')
    
    @app.route('/dashboard')
    def dashboard():
        """Dashboard page"""
        return render_template('dashboard.html')
    
    @app.route('/chat')
    def chat():
        """Chat page"""
        return render_template('chat.html')
    
    @app.route('/settings')
    def settings():
        """Settings page"""
        return render_template('settings.html')
    
    @app.route('/api/status')
    def api_status():
        """Get system status"""
        return jsonify({
            'status': 'running',
            'provider': zynox_instance.current_provider,
            'environment': zynox_instance.environment,
            'package_manager': zynox_instance.package_manager,
            'session_id': zynox_instance.memory.current_session['session_id'],
            'message_count': len(zynox_instance.memory.current_session['messages'])
        })
    
    @app.route('/api/config', methods=['GET', 'POST'])
    def api_config():
        """Get or update configuration"""
        config = Config()
        
        if request.method == 'POST':
            data = request.json
            if 'default_provider' in data:
                config.set_default_provider(data['default_provider'])
                zynox_instance.current_provider = data['default_provider']
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
    
    @app.route('/api/files')
    def api_files():
        """List files in current directory"""
        path = request.args.get('path', '.')
        files = file_manager.list_files(path)
        return jsonify({'files': files})
    
    @app.route('/api/created')
    def api_created():
        """List created files"""
        files = file_manager.list_created_files()
        return jsonify({'files': files})
    
    @app.route('/api/sessions')
    def api_sessions():
        """List all sessions"""
        sessions = zynox_instance.memory.list_sessions()
        return jsonify({'sessions': sessions})
    
    @app.route('/api/sessions/load', methods=['POST'])
    def api_load_session():
        """Load a session"""
        data = request.json
        session_id = data.get('session_id')
        if zynox_instance.memory.load_session(session_id):
            return jsonify({'success': True})
        return jsonify({'success': False, 'error': 'Session not found'})
    
    @app.route('/api/sessions/delete', methods=['POST'])
    def api_delete_session():
        """Delete a session"""
        data = request.json
        session_id = data.get('session_id')
        if zynox_instance.memory.delete_session(session_id):
            return jsonify({'success': True})
        return jsonify({'success': False})
    
    @app.route('/api/sessions/clear', methods=['POST'])
    def api_clear_memory():
        """Clear current memory"""
        zynox_instance.memory.clear_memory()
        return jsonify({'success': True})
    
    @app.route('/api/sessions/new', methods=['POST'])
    def api_new_session():
        """Start new session"""
        zynox_instance.memory.new_session()
        return jsonify({'success': True})
    
    @app.route('/api/clear-created', methods=['POST'])
    def api_clear_created():
        """Clear all created files"""
        file_manager.clear_created_files()
        return jsonify({'success': True})
    
    @app.route('/static/<path:filename>')
    def serve_static(filename):
        """Serve static files"""
        return send_from_directory(app.static_folder, filename)
    
    # SocketIO events
    @socketio.on('connect')
    def handle_connect():
        emit('connected', {'status': 'connected'})
    
    @socketio.on('send_message')
    def handle_message(data):
        """Handle chat message via WebSocket"""
        user_input = data.get('message', '')
        
        # Send thinking status
        emit('thinking', {'status': True})
        
        # Capture output
        import io
        from contextlib import redirect_stdout
        
        output_buffer = io.StringIO()
        with redirect_stdout(output_buffer):
            zynox_instance.memory.add_message("user", user_input)
            zynox_instance.task_complete = False
            
            file_list = file_manager.list_files(".")
            prompt = zynox_instance.create_prompt(user_input, "", file_list)
            response = zynox_instance.call_api(zynox_instance.current_provider, prompt)
            
            if response:
                zynox_instance.memory.add_message("assistant", response[:300])
                zynox_instance.parse_and_execute(response, ".")
        
        result = output_buffer.getvalue()
        if not result or len(result.strip()) == 0:
            result = "✅ Task completed"
        
        emit('message_response', {
            'output': result,
            'session_id': zynox_instance.memory.current_session['session_id']
        })
    
    @socketio.on('execute_command')
    def handle_execute(data):
        """Execute shell command"""
        command = data.get('command', '')
        
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
            emit('command_result', {
                'command': command,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            })
        except subprocess.TimeoutExpired:
            emit('command_result', {
                'command': command,
                'error': 'Command timeout after 30 seconds'
            })
        except Exception as e:
            emit('command_result', {
                'command': command,
                'error': str(e)
            })