import asyncio
import struct


class RCONClient:
    def __init__(self, host: str, port: int, password: str):
        self.host = host
        self.port = port
        self.password = password

        self.reader = None
        self.writer = None

        self.request_id = 0

    async def connect(self):
        """서버 연결 및 인증"""
        self.reader, self.writer = await asyncio.open_connection(self.host, self.port)

        # 인증 패킷 전송
        auth_packet = self._pack_data(self._get_request_id(), 3, self.password)
        self.writer.write(auth_packet)
        await self.writer.drain()

        # 인증 응답 확인
        response = await self._read_packet()
        req_id, req_type, payload = self._unpack_data(response)

        if req_id == -1:
            raise Exception("인증 실패")

    async def send_command(self, command: str) -> str:
        """명령어 전송"""
        cmd_packet = self._pack_data(self._get_request_id(), 2, command)
        self.writer.write(cmd_packet)
        await self.writer.drain()

        # 응답 받기
        response = await self._read_packet()
        req_id, req_type, payload = self._unpack_data(response)

        return payload

    async def close(self):
        """연결 종료"""
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()

    async def _read_packet(self) -> bytes:
        """패킷 읽기"""
        length_data = await self.reader.readexactly(4)
        length = struct.unpack('<I', length_data)[0]
        packet_data = await self.reader.readexactly(length)
        return length_data + packet_data

    def _pack_data(self, req_id: int, req_type: int, payload: str) -> bytes:
        """패킷 생성"""
        payload_bytes = payload.encode('utf-8') + b'\x00'
        packet_size = 4 + 4 + len(payload_bytes) + 1

        packet = struct.pack('<I', packet_size)
        packet += struct.pack('<I', req_id)
        packet += struct.pack('<I', req_type)
        packet += payload_bytes
        packet += b'\x00'

        return packet

    def _unpack_data(self, data: bytes) -> tuple:
        """패킷 파싱"""
        req_id = struct.unpack('<I', data[4:8])[0]
        req_type = struct.unpack('<I', data[8:12])[0]

        payload_end = data.find(b'\x00', 12)
        if payload_end == -1:
            payload_end = len(data) - 1

        payload = data[12:payload_end].decode('utf-8', errors='ignore')
        return req_id, req_type, payload

    def _get_request_id(self) -> int:
        """요청 ID 생성"""
        self.request_id += 1
        return self.request_id


# 간단한 서비스 함수들
async def execute_command(host: str, port: int, password: str, command: str) -> str:
    """명령어 실행"""
    client = RCONClient(host, port, password)
    try:
        await client.connect()
        result = await client.send_command(command)
        return result
    finally:
        await client.close()


async def test_connection(host: str, port: int, password: str) -> bool:
    """연결 테스트"""
    try:
        result = await execute_command(host, port, password, "list")
        return True
    except:
        return False


if __name__ == "__main__":
    host = "localhost"
    port = 25575
    password = "password"
    print(asyncio.run(execute_command(host, port, password, "help")))
