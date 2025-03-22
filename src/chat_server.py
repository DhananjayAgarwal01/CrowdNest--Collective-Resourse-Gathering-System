import socket
import threading
import json
from datetime import datetime

class ChatServer:
    def __init__(self, host='localhost', port=5000):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = {}  # {client_id: (socket, username)}
        self.messages = []  # [(timestamp, sender, receiver, message)]
        
    def start(self):
        """Start the chat server"""
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Chat server started on {self.host}:{self.port}")
        
        # Accept client connections
        accept_thread = threading.Thread(target=self.accept_connections)
        accept_thread.daemon = True
        accept_thread.start()
        
    def accept_connections(self):
        """Accept incoming client connections"""
        while True:
            client_socket, address = self.server_socket.accept()
            print(f"New connection from {address}")
            
            # Start a new thread to handle this client
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_thread.daemon = True
            client_thread.start()
            
    def handle_client(self, client_socket):
        """Handle messages from a client"""
        try:
            # Get username from client
            data = client_socket.recv(1024).decode('utf-8')
            message = json.loads(data)
            
            if message['type'] == 'connect':
                username = message['username']
                user_id = message['user_id']
                self.clients[user_id] = (client_socket, username)
                
                # Send connection confirmation
                self.send_to_client(client_socket, {
                    'type': 'connect_response',
                    'status': 'success',
                    'message': f'Connected as {username}'
                })
                
                # Send any pending messages
                self.send_pending_messages(user_id)
                
            # Handle incoming messages
            while True:
                try:
                    data = client_socket.recv(1024).decode('utf-8')
                    if not data:
                        break
                        
                    message = json.loads(data)
                    
                    if message['type'] == 'chat':
                        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        self.messages.append((
                            timestamp,
                            message['sender_id'],
                            message['receiver_id'],
                            message['content']
                        ))
                        
                        # Try to send to receiver if online
                        if message['receiver_id'] in self.clients:
                            receiver_socket = self.clients[message['receiver_id']][0]
                            self.send_to_client(receiver_socket, {
                                'type': 'chat',
                                'sender_id': message['sender_id'],
                                'sender_name': self.clients[message['sender_id']][1],
                                'content': message['content'],
                                'timestamp': timestamp
                            })
                            
                except json.JSONDecodeError:
                    continue
                    
        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            # Remove client on disconnect
            for user_id, (socket, _) in list(self.clients.items()):
                if socket == client_socket:
                    del self.clients[user_id]
                    break
            client_socket.close()
            
    def send_to_client(self, client_socket, message):
        """Send a message to a client"""
        try:
            client_socket.send(json.dumps(message).encode('utf-8'))
        except:
            pass
            
    def send_pending_messages(self, user_id):
        """Send pending messages to a user who just connected"""
        if user_id not in self.clients:
            return
            
        client_socket = self.clients[user_id][0]
        
        # Send all messages where this user is the receiver
        for timestamp, sender_id, receiver_id, content in self.messages:
            if receiver_id == user_id:
                if sender_id in self.clients:
                    sender_name = self.clients[sender_id][1]
                    self.send_to_client(client_socket, {
                        'type': 'chat',
                        'sender_id': sender_id,
                        'sender_name': sender_name,
                        'content': content,
                        'timestamp': timestamp
                    })
                    
    def stop(self):
        """Stop the chat server"""
        for client_socket, _ in self.clients.values():
            try:
                client_socket.close()
            except:
                pass
        self.server_socket.close()

if __name__ == '__main__':
    server = ChatServer()
    server.start()
    
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("\nStopping chat server...")
        server.stop()
