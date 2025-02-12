import socket
import threading
import json

class ChatServer:
    def __init__(self, host='localhost', port=5000):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen()
        
        self.clients = {}
        print(f"Chat server running on {host}:{port}")
        
        self.accept_connections()
    
    def accept_connections(self):
        while True:
            try:
                client_socket, address = self.server.accept()
                thread = threading.Thread(target=self.handle_client, args=(client_socket,))
                thread.start()
            except Exception as e:
                print(f"Error accepting connection: {e}")
    
    def handle_client(self, client_socket):
        try:
            auth = json.loads(client_socket.recv(1024).decode())
            user_id = auth['user_id']
            self.clients[client_socket] = user_id
            
            while True:
                message = client_socket.recv(1024).decode()
                if message:
                    data = json.loads(message)
                    self.forward_message(user_id, data)
        except:
            pass
        finally:
            self.remove_client(client_socket)
    
    def forward_message(self, sender_id, data):
        receiver_id = data['receiver_id']
        for sock, uid in self.clients.items():
            if uid == receiver_id:
                try:
                    sock.send(json.dumps({
                        'sender_id': sender_id,
                        'content': data['content']
                    }).encode())
                except:
                    self.remove_client(sock)
    
    def remove_client(self, client_socket):
        if client_socket in self.clients:
            del self.clients[client_socket]
        client_socket.close()

if __name__ == "__main__":
    server = ChatServer()
