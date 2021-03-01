

if __name__ == '__main__':
    import pip, sys, os, subprocess
    from pip._internal.utils.misc import get_installed_distributions

    pkgs = ''.join(str(get_installed_distributions(local_only=True)))
    dep = ['cherrypy', 'more-itertools', 'jaraco.collections']
    for d in dep:
        if d not in pkgs:
            out = subprocess.run(f'pip install -q {d}', shell=True, capture_output=True, text=True)
            print(out.stdout)
            print(out.stderr)

    import cherrypy
    from cherrypy.lib import static

    localDir = os.path.dirname(__file__)
    absDir = os.path.join(os.getcwd(), localDir)

    class App(object):

        @cherrypy.expose
        def index(self):
            return """
                <html><body>
                    <h2>Upload a file</h2>
                    <form action="upload" method="post" enctype="multipart/form-data">
                    filename: <input type="file" name="users_file" /><br />
                    <input type="submit" />
                    </form>
                    <h2>Download a file</h2>
                    <a href='download'>Penguin image</a>
                </body></html>
                """

        @cherrypy.expose
        def upload(self, users_file):
            out = """<html>
                <body>
                    <h2> Result </h2>
                    file length: {}<br />
                    filename: {}<br />
                    mime-type: {}<br />
                    <hr />
                    <img src='static/1.jpg' width='300px'/> <br />
                    <br />
                    <h2> is similar to </h2>
                    <img src='{}' width='300px'/> <br />
                    <hr />
                    error: {}<br />
                </body>
                </html>"""

            size = 0
            image_bytes = bytearray()
            while True:
                data = users_file.file.read(1024*8)
                if not data:
                    break
                image_bytes += bytearray(data)
                size += len(data)

            image_file = 'image.jpg'
            err = 'None'

            try:
                with open('static/'+image_file, 'wb') as f:
                    f.write(image_bytes)
                    f.close()
            except IOError as e:
                err = e
            return out.format(size, users_file.filename,
                              users_file.content_type,
                              'static/' + image_file,
                              err)

        @cherrypy.expose
        def download(self):
            path = os.path.join(absDir, 'static/1.jpg')
            return static.serve_file(path, 'application/x-download',
                                     'attachment', os.path.basename(path))


    cherrypy.config.update({'server.socket_host': '0.0.0.0',
                            'server.socket_port': 8080})
    conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd())
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': 'static'
        }
    }
    cherrypy.quickstart(App(), '', conf)
