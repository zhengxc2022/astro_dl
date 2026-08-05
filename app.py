from flask import Flask, render_template, request, jsonify
import sys
import os
import io
from contextlib import redirect_stdout, redirect_stderr

# 动态获取脚本所在目录，使其可移植
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(SCRIPT_DIR, 'lib'))
from DLtools import img_download
from config import config

app = Flask(__name__)

# Survey configurations with their specific parameters
SURVEY_CONFIG = {
    'lotss': {
        'name': 'LoTSS (LOFAR Two-metre Sky Survey)',
        'method': 'lotss_img',
        'params': {
            'out': {'type': 'text', 'default': 'lotss.fits', 'label': 'Output Filename'},
            'low': {'type': 'checkbox', 'default': False, 'label': 'Low Resolution'},
            'dr': {'type': 'select', 'default': 2, 'options': [1, 2, 3], 'label': 'Data Release'}
        }
    },
    'ls': {
        'name': 'Legacy Survey',
        'method': 'LS_img',
        'params': {
            'out': {'type': 'text', 'default': 'LS.fits', 'label': 'Output Filename'},
            'pixscale': {'type': 'number', 'default': 0.3, 'label': 'Pixel Scale (arcsec/pixel)'},
            'bands': {'type': 'text', 'default': 'grz', 'label': 'Bands'},
            'release': {'type': 'select', 'default': 10, 'options': [8, 9, 10], 'label': 'Data Release'}
        }
    },
    'vlass': {
        'name': 'VLASS (VLA Sky Survey)',
        'method': 'VLASS_img',
        'params': {
            'epoch': {'type': 'select', 'default': 1, 'options': [1, 2, 3], 'label': 'Epoch'},
            'image_type': {'type': 'select', 'default': 'ql', 'options': ['ql', 'se'], 'label': 'Image Type'},
            'out': {'type': 'text', 'default': 'vlass.fits', 'label': 'Output Filename'},
            'overwrite_existing': {'type': 'checkbox', 'default': True, 'label': 'Overwrite Existing'}
        }
    },
    'nvss': {
        'name': 'NVSS (NRAO VLA Sky Survey)',
        'method': 'NVSS_img',
        'params': {
            'out': {'type': 'text', 'default': 'NVSS.fits', 'label': 'Output Filename'}
        }
    },
    'first': {
        'name': 'FIRST Survey',
        'method': 'FIRST_img',
        'params': {
            'out': {'type': 'text', 'default': 'FIRST.fits', 'label': 'Output Filename'}
        }
    },
    'sdss': {
        'name': 'SDSS (Sloan Digital Sky Survey)',
        'method': 'SDSS_img',
        'params': {
            'out': {'type': 'text', 'default': 'SDSS.fits', 'label': 'Output Filename'},
            'pixscale': {'type': 'number', 'default': 0.3, 'label': 'Pixel Scale (arcsec/pixel)'},
            'bands': {'type': 'text', 'default': 'grz', 'label': 'Bands'}
        }
    },
    'smss': {
        'name': 'SMSS (SkyMapper Survey)',
        'method': 'SMSS_img',
        'params': {
            'out': {'type': 'text', 'default': 'SMSS.fits', 'label': 'Output Filename'},
            'band': {'type': 'text', 'default': 'g', 'label': 'Band'}
        }
    },
    'vlbi': {
        'name': 'VLBI (Astrogeo)',
        'method': 'VLBI_img',
        'params': {
            'jname': {'type': 'text', 'default': 'J000000+000000', 'label': 'Source J2000 Name'},
            'band': {'type': 'select', 'default': 'L', 'options': ['L', 'C', 'X', 'K'], 'label': 'Band'},
            'out': {'type': 'text', 'default': 'VLBI.fits', 'label': 'Output Filename'}
        }
    },
    'racs': {
        'name': 'RACS (Rapid ASKAP Continuum)',
        'method': 'RACS_img',
        'params': {
            'band': {'type': 'select', 'default': 'Low', 'options': ['Low', 'Mid', 'High'], 'label': 'Band'},
            'poltype': {'type': 'select', 'default': 'i', 'options': ['i', 'q', 'u', 'v'], 'label': 'Polarization Type'},
            'out_dir': {'type': 'text', 'default': 'RACS', 'label': 'Output Directory'},
            'out': {'type': 'text', 'default': '', 'label': 'Output Filename (blank = keep original)'},
            'username': {'type': 'text', 'default': config.CASDA_USERNAME, 'label': 'CASDA Username'},
            'password': {'type': 'password', 'default': config.CASDA_PASSWORD, 'label': 'CASDA Password'}
        }
    },
    'emu': {
        'name': 'EMU (Evolutionary Map of Universe)',
        'method': 'EMU_img',
        'params': {
            'poltype': {'type': 'select', 'default': 'i', 'options': ['i', 'q', 'u', 'v'], 'label': 'Polarization Type'},
            'out_dir': {'type': 'text', 'default': 'EMU', 'label': 'Output Directory'},
            'out': {'type': 'text', 'default': '', 'label': 'Output Filename (blank = keep original)'},
            'username': {'type': 'text', 'default': config.CASDA_USERNAME, 'label': 'CASDA Username'},
            'password': {'type': 'password', 'default': config.CASDA_PASSWORD, 'label': 'CASDA Password'}
        }
    },
    'tgss': {
        'name': 'TGSS (TIFR GMRT Sky Survey)',
        'method': 'TGSS_img',
        'params': {
            'out': {'type': 'text', 'default': 'TGSS.fits', 'label': 'Output Filename'}
        }
    }
}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/surveys')
def get_all_surveys():
    """Get all available surveys"""
    return jsonify(SURVEY_CONFIG)


@app.route('/api/survey/<survey_key>')
def get_survey_params(survey_key):
    """Get parameters for a specific survey"""
    if survey_key in SURVEY_CONFIG:
        return jsonify(SURVEY_CONFIG[survey_key])
    return jsonify({'error': 'Survey not found'}), 404


@app.route('/api/browse', methods=['POST'])
def browse_directory():
    """Browse file system directories"""
    data = request.json
    current_path = data.get('path', os.path.expanduser('~'))
    
    try:
        # Normalize path
        current_path = os.path.abspath(current_path)
        
        # Check if path exists
        if not os.path.exists(current_path):
            return jsonify({
                'success': False,
                'error': 'Path does not exist'
            })
        
        # Check if it's a directory
        if not os.path.isdir(current_path):
            return jsonify({
                'success': False,
                'error': 'Not a directory'
            })
        
        # List directories
        items = []
        try:
            for item in sorted(os.listdir(current_path)):
                item_path = os.path.join(current_path, item)
                if os.path.isdir(item_path):
                    items.append({
                        'name': item,
                        'path': item_path,
                        'type': 'directory'
                    })
        except PermissionError:
            return jsonify({
                'success': False,
                'error': 'Permission denied'
            })
        
        # Get parent directory
        parent = os.path.dirname(current_path) if current_path != '/' else None
        
        return jsonify({
            'success': True,
            'current_path': current_path,
            'parent': parent,
            'directories': items
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


@app.route('/api/common-paths')
def get_common_paths():
    """Get common directory paths"""
    home = os.path.expanduser('~')
    cwd = os.getcwd()
    
    paths = [
        {'name': 'Home', 'path': home, 'icon': '🏠'},
        {'name': 'Current Directory', 'path': cwd, 'icon': '📁'},
        {'name': 'Downloads', 'path': os.path.join(home, 'Downloads'), 'icon': '📥'},
        {'name': 'Desktop', 'path': os.path.join(home, 'Desktop'), 'icon': '🖥️'},
    ]
    
    # Check for WSL Windows paths
    if os.path.exists('/mnt/c/'):
        win_user = None
        try:
            # Try to find Windows user directory
            for item in os.listdir('/mnt/c/Users/'):
                if item not in ['Public', 'Default', 'All Users', 'desktop.ini']:
                    win_user = item
                    break
        except:
            pass
        
        if win_user:
            win_home = f'/mnt/c/Users/{win_user}'
            paths.extend([
                {'name': 'Windows Home', 'path': win_home, 'icon': '🪟'},
                {'name': 'Windows Downloads', 'path': f'{win_home}/Downloads', 'icon': '📥'},
                {'name': 'Windows Desktop', 'path': f'{win_home}/Desktop', 'icon': '🖥️'},
            ])
    
    # Filter existing paths
    valid_paths = [p for p in paths if os.path.exists(p['path'])]
    
    return jsonify(valid_paths)


@app.route('/api/download', methods=['POST'])
def download():
    """Execute image download"""
    data = request.json
    
    ra = float(data.get('ra'))
    dec = float(data.get('dec'))
    size = float(data.get('size'))
    survey_key = data.get('survey')
    params = data.get('params', {})
    output_dir = data.get('output_dir', './downloads/')
    
    if survey_key not in SURVEY_CONFIG:
        return jsonify({'error': 'Invalid survey'}), 400
    
    survey_config = SURVEY_CONFIG[survey_key]
    method_name = survey_config['method']
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # 只处理当前 survey 定义的参数，忽略其他参数
    # 首先设置默认值
    converted_params = {}
    for key, param_config in survey_config['params'].items():
        converted_params[key] = param_config['default']
    
    # 然后用用户提供的值覆盖（只接受当前 survey 定义的参数）
    for key, value in params.items():
        if key in survey_config['params']:
            param_config = survey_config['params'][key]
            if param_config['type'] == 'number':
                converted_params[key] = float(value)
            elif param_config['type'] == 'checkbox':
                converted_params[key] = value == True or value == 'true'
            elif param_config['type'] == 'select':
                try:
                    converted_params[key] = int(value)
                except:
                    converted_params[key] = value
            else:
                converted_params[key] = value
    
    # Update output paths with the output directory
    # For 'out' parameter (filename), prepend output directory
    if 'out' in converted_params:
        if converted_params['out'] == '':
            converted_params['out'] = None
        elif converted_params['out'] is not None:
            converted_params['out'] = os.path.join(output_dir, os.path.basename(converted_params['out']))
    
    # For 'outdir' or 'out_dir' parameters, use the output directory
    if 'outdir' in converted_params:
        converted_params['outdir'] = output_dir
    if 'out_dir' in converted_params:
        converted_params['out_dir'] = output_dir
    
    # Treat empty credential strings as None (falls back to environment variables)
    for cred_key in ('username', 'password'):
        if cred_key in converted_params and converted_params[cred_key] == '':
            converted_params[cred_key] = None
    
    # In the web app, a CASDA password is required when a username is provided
    # (interactive keyring login is not available through the web form)
    if converted_params.get('username') and not converted_params.get('password'):
        return jsonify({
            'success': False,
            'error': 'CASDA password is required when username is provided. '
                     'Set CASDA_PASSWORD environment variable or enter it in the form.'
        }), 400
    
    # Capture stdout and stderr
    output_buffer = io.StringIO()
    
    try:
        def run_download():
            downloader = img_download(ra, dec, size)
            method = getattr(downloader, method_name)
            print(f"Starting download for {survey_config['name']}...")
            print(f"Position: RA={ra}, Dec={dec}, Size={size} arcsec")
            print(f"Output directory: {output_dir}")
            # Don't print passwords in logs
            safe_params = {k: v for k, v in converted_params.items() if k != 'password'}
            print(f"Parameters: {safe_params}")
            method(**converted_params)
            print(f"\nDownload completed!")
            print(f"Output files: {downloader.outfiles}")
            return downloader
        
        with redirect_stdout(output_buffer), redirect_stderr(output_buffer):
            downloader = run_download()
        
        output = output_buffer.getvalue()
        
        return jsonify({
            'success': True,
            'output': output,
            'outfiles': downloader.outfiles
        })
        
    except Exception as e:
        import traceback
        error_output = output_buffer.getvalue()
        error_output += f"\nError: {str(e)}\n"
        error_output += traceback.format_exc()
        return jsonify({
            'success': False,
            'output': error_output,
            'error': str(e)
        })


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
