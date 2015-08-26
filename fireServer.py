import os
import re
from flask import Flask, request, redirect, url_for
from flask import send_from_directory
from werkzeug import secure_filename
from werkzeug.serving import run_simple
import mimetypes
from flask import request, send_file, Response
from werkzeug.datastructures import Headers
UPLOAD_FOLDER = 'data/'
ALLOWED_EXTENSIONS = set(['pdf'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#@app.after_request
#def after_request(response):
#    response.headers.add('Accept-Ranges', 'bytes')
#    return response

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def send_file_partial(path):
    """ 
        Simple wrapper around send_file which handles HTTP 206 Partial Content
        (byte ranges)
        TODO: handle all send_file args, mirror send_file's error handling
        (if it has any)
    """
    range_header = request.headers.get('Range', None)
    if not range_header: return send_file(path)
    
    size = os.path.getsize(path)    
    byte1, byte2 = 0, None
    
    m = re.search('(\d+)-(\d*)', range_header)
    g = m.groups()
    
    if g[0]: byte1 = int(g[0])
    if g[1]: byte2 = int(g[1])

    length = size - byte1
    if byte2 is not None:
        length = byte2 - byte1
    
    data = None
    with open(path, 'rb') as f:
        f.seek(byte1)
        data = f.read(length)

    rv = Response(data, 
        206,
        mimetype=mimetypes.guess_type(path)[0], 
        direct_passthrough=True)
    rv.headers.add('Content-Range', 'bytes {0}-{1}/{2}'.format(byte1, byte1 + length - 1, size))

    return rv


def __send_file( musicFile , cachetimout, stream=True):
    headers = Headers()
    headers.add('Content-Disposition', 
'attachment',filename=musicFile.filename)
    headers.add('Content-Transfer-Encoding','binary')

    status = 200
    size = getsize(musicFile.path)
    begin=0;
    end=size-1;

    if request.headers.has_key("Range") and rangerequest:
        status = 206
        headers.add('Accept-Ranges','bytes')
        ranges=findall(r"\d+", request.headers["Range"])
        begin = int( ranges[0] )
        if len(ranges)>1:
            end=int( ranges[1] )
        headers.add('Content-Range','bytes %s-%s/%s' % 
(str(begin),str(end),str(end-begin)) )
    
    headers.add('Content-Length',str((end-begin)+1))
    
    #Add mimetype    
    mimetypes = {u"mp3":"audio/mpeg",u"ogg":"audio/ogg"}
    if stream==True:
        mimetype = mimetypes[musicFile.filetype]
    else:
        mimetype = "application/octet-stream"
    
    response = Response( file(musicFile.path), status=status, 
mimetype=mimetype, headers=headers, direct_passthrough=True)
    
    #enable browser file caching with etags
    response.cache_control.public = True
    response.cache_control.max_age = int(cachetimout)
    response.last_modified = int(musicFile.changetime)
    response.expires=int( time() + int(cachetimout) )
    response.set_etag('%s%s' % ( musicFile.id,musicFile.changetime ))
    response.make_conditional(request)
    
    return response

@app.route('/file/<path:filepath>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def upload_file(filepath):
    #savepath = os.path.join(app.config['UPLOAD_FOLDER'], filepath)
    savepath = app.config['UPLOAD_FOLDER'] + filepath
    directory, filename = os.path.split(savepath)
    if request.method == 'GET':
        #return send_from_directory(directory, filename, add_etags=False)
        return send_file_partial(savepath)
        #return send_file(savepath, 1000000)
    if request.method == 'POST' or request.method == 'PUT':        
        file = request.files['file']
        if not os.path.exists(directory):
            os.makedirs(directory)
        file.save(savepath)
        return filepath
    if request.method == 'DELETE':
        if not os.path.exists(savepath):
            return 'NotExists'
        os.remove(savepath)
        #os.removedirs(directory)
        return 'OK'
    return

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, threaded=True)
    #run_simple('0.0.0.0', 5000, app,
    #           use_reloader=True, use_debugger=False, use_evalex=True)

