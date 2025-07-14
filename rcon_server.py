# rcon_server.py
import socket
import struct
import threading
import time

import screen_handler


class RCONServer:
    def __init__(self, screen_handler, host='0.0.0.0', port=25575, password='password'):
        self.screen_handler = screen_handler
        self.host = host
        self.port = port
        self.password = password
        self.running = False

    def start(self):
        self.running = True
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)

        print(f"RCON server running on {self.host}:{self.port}")

        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                thread = threading.Thread(target=self.handle_client, args=(client_socket,))
                thread.daemon = True
                thread.start()
            except Exception as e:
                if self.running:
                    print(f"❌ Error: {e}")

    def stop(self):
        self.running = False
        if hasattr(self, 'server_socket'):
            self.server_socket.close()

    def handle_client(self, client_socket):
        """클라이언트 연결 처리"""
        try:
            # 인증 패킷 수신
            auth_packet = self._read_packet(client_socket)
            req_id, req_type, payload = self._unpack_data(auth_packet)
            
            # 인증 확인
            if req_type == 3 and payload == self.password:  # AUTH_REQUEST
                # 인증 성공 응답
                response = self._pack_data(req_id, 2, "")  # AUTH_RESPONSE
                client_socket.send(response)
                
                # 클라이언트 명령 처리 루프
                while True:
                    try:
                        cmd_packet = self._read_packet(client_socket)
                        req_id, req_type, command = self._unpack_data(cmd_packet)
                        
                        if req_type == 2:  # EXEC_COMMAND
                            # 명령어 실행
                            result = self.screen_handler.execute_command(command)
                            response = self._pack_data(req_id, 0, result)  # RESPONSE_VALUE
                            client_socket.send(response)
                            
                    except Exception as e:
                        print(f"Command error: {e}")
                        break
                        
            else:
                # 인증 실패 응답
                response = self._pack_data(-1, 2, "")
                client_socket.send(response)
                
        except Exception as e:
            print(f"Client error: {e}")
        finally:
            client_socket.close()
    
    def _read_packet(self, socket):
        """패킷 읽기"""
        length_data = socket.recv(4)
        if not length_data:
            raise Exception("Connection closed")
        
        length = struct.unpack('<I', length_data)[0]
        packet_data = socket.recv(length)
        return length_data + packet_data
    
    def _pack_data(self, req_id, req_type, payload):
        """패킷 생성"""
        payload_bytes = payload.encode('utf-8') + b'\x00'
        packet_size = 4 + 4 + len(payload_bytes) + 1
        
        packet = struct.pack('<I', packet_size)
        packet += struct.pack('<I', req_id)
        packet += struct.pack('<I', req_type)
        packet += payload_bytes
        packet += b'\x00'
        
        return packet
    
    def _unpack_data(self, data):
        """패킷 파싱"""
        req_id = struct.unpack('<I', data[4:8])[0]
        req_type = struct.unpack('<I', data[8:12])[0]
        
        payload_end = data.find(b'\x00', 12)
        if payload_end == -1:
            payload_end = len(data) - 1
            
        payload = data[12:payload_end].decode('utf-8', errors='ignore')
        return req_id, req_type, payload
