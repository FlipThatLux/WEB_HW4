from datetime import datetime
from time import sleep
from threading import Thread
from http import client
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import mimetypes
import logging
import pathlib
import socket
import json



HOST = '127.0.0.1'
PORT = 5000



def run_server(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server = ip, port
    sock.bind(server)
    try:
        while True:
            data, address = sock.recvfrom(1024)
            #print(f'Received data: {data.decode()} from: {address}')
            data_string = data.decode()
            cutoff, name, text = data_string.split("///")
            data_dict = {"username": name.strip("'"), "message": text.strip("'")}
            # data_string = data_string.translate(MAP)
            # name_part, text_part = data_string.split('", "')
            # data_dict = {"username": name_part.split(":")[1].strip().strip("'"), "message": text_part.split(":")[1].strip().strip("'")}

            with open('S:/Stuff/Homework_Python/WEB/HW4/front-init/storage/data.json', 'r') as file:
                file_data = json.load(file)
            with open('S:/Stuff/Homework_Python/WEB/HW4/front-init/storage/data.json', 'w') as file:
                file_data[str(datetime.now())] = data_dict
                json.dump(file_data, file)


            sock.sendto(data, address)
            logging.warning(f'Send data: {data.decode()} to: {address}')

    except KeyboardInterrupt:
        logging.warning(f'Destroy server')
    finally:
        sock.close()


def run_client(ip, port, comment):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server = ip, port
    # for line in MESSAGE.split(' '):
    #     data = line.encode()
    #     sock.sendto(data, server)
    #     print(f'Send data: {data.decode()} to server: {server}')
    #     response, address = sock.recvfrom(1024)
    #     print(f'Response data: {response.decode()} from address: {address}')
    
    data = str(comment).encode()
    sock.sendto(data, server)
    logging.warning(f'Send data: {data.decode()} to server: {server}')
    response, address = sock.recvfrom(1024)
    logging.warning(f'Response data: {response.decode()} from address: {address}')
    sock.close()


class HttpHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == '/':
            self.send_html_file('index.html')
        elif pr_url.path == '/message.html':
            self.send_html_file('message.html')
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file('error.html', 404)

    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        # print(data)
        data_parse = urllib.parse.unquote_plus(data.decode())
        # print(data_parse)
        data_dict = {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}
        shortened_data = ""
        for value in data_dict.values():
            shortened_data += "///" + value
        # logging.warning(f"From do_POST: sending {shortened_data}")

        # print(data_dict)
        # logging.warning(f'kkeekkekekekekekek {data_dict}')
        # with open('S:/Stuff/Homework_Python/WEB/HW4/front-init/storage/data.json', 'r') as file:
        #     file_data = json.load(file)
        # with open('S:/Stuff/Homework_Python/WEB/HW4/front-init/storage/data.json', 'w') as file:
        #     file_data[str(datetime.now())] = data_dict
        #     json.dump(file_data, file)

        client_with_socket = Thread(target=run_client, args=(HOST, PORT, shortened_data))
        client_with_socket.start()
        # sleep(3)
        client_with_socket.join()

        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", 'text/plain')
        self.end_headers()
        with open(f'.{self.path}', 'rb') as file:
            self.wfile.write(file.read())



def run(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ('', 3000)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()



if __name__ == '__main__':
    server_with_socket = Thread(target=run_server, args=(HOST, PORT))
    server_with_socket.start()
    run()
    server_with_socket.join()