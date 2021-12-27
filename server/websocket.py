from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from concurrent.futures import ThreadPoolExecutor

import worker

w = worker.Worker()

app = Flask(__name__, static_folder='build/static', template_folder='build')
sio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def serve_ui():
    '''serve ui 

    '''
    return render_template('index.html')

@sio.on('connect')
def handle_connect():

    print('connected')

@sio.on('get_datasets')
def handel_get_datasets():
    data_names = w.handle_get_datasets()

    emit('r_get_datasets', data_names)
    return

@sio.on('get_preview_ir')
def handle_get_preview_ir(dataset):  
    outs = w.handle_get_preview_ir(dataset)

    emit('r_get_preview_ir', outs)
    return

@sio.on('get_preview_isw')
def handle_get_preview_iws(dataset):  
    out = w.handle_get_preview_isw(dataset)

    emit('r_get_preview_isw', out)
    return

@sio.on('register')
def handle_ir(in_args):
    print('received')

    d = in_args['dataset']
    algorithm = in_args['algorithm']

    emit('r_register', 'processing')
    with ThreadPoolExecutor() as executor:
        if algorithm == 'farneback':
            t = executor.submit(w.run_farneback, d)
        elif algorithm == 'horn-schunck':
            alpha = in_args['alpha']
            t = executor.submit(w.run_horn_schunck, d, alpha)
        else:
            t = executor.submit(w.run_farneback, d)

        out = t.result()

    emit('r_register', out)
    return

@sio.on('restore')
def handle_restore(in_args):
    ''' distortion restoration
    args:
        {
            'dataset': str
        }

    returns:
        {
            'restored': image file,
            'ssim': float,
            'psnr': float,
            'mse': float
        }

    '''
    print('received isw')

    emit('r_restore', 'processing')

    d = in_args['dataset']
    with ThreadPoolExecutor() as executor:
        t = executor.submit(w.run_restore, d)
        out = t.result()

    emit('r_restore', out)
    return

if __name__ == '__main__':
    sio.run(app, host='0.0.0.0', port=8888, debug=True)
