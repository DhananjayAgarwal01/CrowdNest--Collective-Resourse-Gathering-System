import socket
import threading
import json
from datetime import datetime

class ChatClient:
    def __init__(self, host='localhost', port=5000):
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
        self.message_callback = None
        self.error_callback = None
        
    def connect(self, user_id, username):
        """Connect to the chat server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            
            # Send connect message
            self.send_message({
                'type': 'connect',
                'user_id': user_id,
                'username': username
            })
            
            # Start listening for messages
            self.connected = True
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()
            
            return True
            
        except Exception as e:
            if self.error_callback:
                self.error_callback(f"Failed to connect: {str(e)}")
            return False
            
    def send_chat_message(self, sender_id, receiver_id, content):
        """Send a chat message to another user"""
        if not self.connected:
            if self.error_callback:
                self.error_callback("Not connected to chat server")
            return False
            
        try:
            self.send_message({
                'type': 'chat',
                'sender_id': sender_id,
                'receiver_id': receiver_id,
                'content': content
            })
            return True
        except Exception as e:
            if self.error_callback:
                self.error_callback(f"Failed to send message: {str(e)}")
            return False
            
    def send_message(self, message):
        """Send a message to the server"""
        try:
            self.socket.send(json.dumps(message).encode('utf-8'))
        except Exception as e:
            if self.error_callback:
                self.error_callback(f"Failed to send message: {str(e)}")
            self.disconnect()
            
    def receive_messages(self):
        """Receive messages from the server"""
        while self.connected:
            try:
                data = self.socket.recv(1024).decode('utf-8')
                if not data:
                    break
                    
                message = json.loads(data)
                
                if message['type'] == 'chat' and self.message_callback:
                    self.message_callback(message)
                    
            except json.JSONDecodeError:
                continue
            except Exception as e:
                if self.error_callback:
                    self.error_callback(f"Connection error: {str(e)}")
                break
                
        self.disconnect()
        
    def set_message_callback(self, callback):
        """Set callback for receiving messages"""
        self.message_callback = callback
        
    def set_error_callback(self, callback):
        """Set callback for errors"""
        self.error_callback = callback
        
    def disconnect(self):
        """Disconnect from the chat server"""
        self.connected = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
