from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import sys
import ssl

class RequestHandler(BaseHTTPRequestHandler):
    Page = '''\
<html>
<body>
<table>
<tr>  <td>Header: </td>         <td>Value</td>          </tr>
<tr>  <td>Date and time: </td>  <td>{date_time}</td>    </tr>
<tr>  <td>Client host: </td>    <td>{client_host}</td>  </tr>
<tr>  <td>Client port: </td>    <td>{client_port}s</td> </tr>
<tr>  <td>Command: </td>        <td>{command}</td>      </tr>
<tr>  <td>Path: </td>           <td>{path}</td>         </tr>
</table>
--------------------------------------------------------------
'''
    Error_Page = '''\
<p>Error accessing {path}</p>
<p>{msg}</p>
</body>
</html>
'''
    Listing_Page = '''\
<p>Directory Listing:</p>
<ul>
{0}
</ul>
</body>
</html>
'''
    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
    def do_GET(self):
        page = self.create_page()
        a = open("Page.html",'w')
        a.write(page)
        a.close()
        try:
            fullpath = os.getcwd()
            fullpath += self.path.replace("%20"," ")
            if not os.path.exists(fullpath):
                raise Exception("'{0}' not found".format(self.path))
            elif os.path.exists(fullpath):
                if os.path.isfile(fullpath):
                    self.handle_file(fullpath)
                elif os.path.isdir(fullpath):
                    self.list_dir(fullpath)
            else:
                raise Exception("Unknown Object '{0}'".format(self.path))
        except Exception as msg:
            self.handle_error(msg)
    def handle_file(self, full_path):
        try:
            with open(full_path,'rb') as reader:
                content = reader.read()
                reader.close()
            self.send_content(content)
        except IOError or PermissionError as msg:
            msg = "'{0}' cannot be read: {1}".format(self.path, msg)
            self.handle_error(msg)
    def handle_error(self, msg):
        content = self.Error_Page.format(path=self.path, msg=msg)
        a = open("Page.html",'a')
        a.write(content)
        a.close()
        with open("Page.html",'rb') as reader:
            content = reader.read()
        self.send_content(content, 404)
    def send_content(self, content, status=200):
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)
        os.remove("Page.html")
    def list_dir(self, full_path):
        try:
            entries = os.listdir(full_path)
            bullets = ['<li>{0}</li>'.format(e) for e in entries]
            page = self.Listing_Page.format('\n'.join(bullets))
            a = open("Page.html",'a')
            a.write(page)
            a.close()
            with open("Page.html",'rb') as reader:
                page = reader.read()
            self.send_content(page)
        except Exception as msg:
            msg = "'{0}' cannot be listed: {1}".format(self.path, msg)
            self.handle_error(msg)
    def create_page(self):
        values = {
            'date_time'   : self.date_time_string(),
            'client_host' : self.client_address[0],
            'client_port' : self.client_address[1],
            'command'     : self.command,
            'path'        : self.path
        }
        page = self.Page.format(**values)
        return page
    
def usage():
    print("Usage:\n[+] BasicHTTPSServer.py [port]\n[+] Port value must be between 0 and 65535")
    print("[+] Make sure the port is available and open")
    print("Quitting...")
    exit()
    
def run():
    if(len(sys.argv)!=2):
        usage()
    if(int(sys.argv[1]) >= 0 and int(sys.argv[1]) <= 65535):
        prt = int(sys.argv[1])
    else:
        usage()
    try:
        print("[+] Starting the web server")
        print("[+] Serving HTTPS on port {0}".format(prt))
        serverAddress = ('', prt)
        server = HTTPServer(serverAddress, RequestHandler)
        server.socket = ssl.wrap_socket(server.socket,certfile='./server.pem',server_side='True')
        print("[+] Web server ready\n[+] Press Ctrl+C to shutdown the web server")
        server.serve_forever()
    except KeyboardInterrupt:
        print ('[+] ^C received, shutting down the web server')
        exit()
    except Exception as msg:
        print("Error: {0}".format(msg))
        print("Quitting...")
        exit()

if __name__=='__main__':
    run()
