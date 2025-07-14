# bedrock_parser.py
import re


class BedrockParser:
    def __init__(self):
        # Bedrock 서버 로그 패턴 (실제 형식: [2025-07-14 17:44:34:423 INFO])
        self.log_pattern = re.compile(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}:\d{3} \w+)\]\s*(.*)')
        # ANSI 색상 코드 제거 패턴
        self.ansi_pattern = re.compile(r'\x1b\[[0-9;]*m')
        # 게임 색상 코드 제거 패턴 (§2, §a 등)
        self.game_color_pattern = re.compile(r'§[0-9a-fk-or]')
    
    def get_command_response(self, raw_output, sent_command, max_response_lines=10):
        """입력한 명령어 아래 라인들을 제한된 개수만 추출"""
        lines = raw_output.split('\n')
        
        command_line_index = self._find_command_line(lines, sent_command)
        if command_line_index is None:
            return "Command executed (command not found in output)"
        
        response_lines = self._extract_response_lines(
            lines, command_line_index, max_response_lines
        )
        
        return '\n'.join(response_lines) if response_lines else "Command executed"
    
    def _find_command_line(self, lines, sent_command):
        """명령어가 있는 라인을 뒤에서부터 찾기"""
        for i in range(len(lines) - 1, -1, -1):
            if lines[i].strip() == sent_command:
                return i
        return None
    
    def _extract_response_lines(self, lines, start_index, max_lines):
        """명령어 라인 아래의 응답 라인들 추출 (개선된 로직)"""
        response_lines = []
        
        # 명령어 바로 다음 라인부터 시작
        for line in lines[start_index + 1:]:
            # 최대 라인 수에 도달하면 중단
            if len(response_lines) >= max_lines:
                break
                
            line = line.strip()
            if not line:
                continue

            # 휴리스틱: 새로운 타임스탬프 로그는 이전 명령어 응답의 끝을 의미.
            # (단, 첫 번째 응답 라인은 타임스탬프를 가질 수 있으므로, 이미 응답을 수집하기 시작했을 때만 적용)
            if response_lines and self.log_pattern.match(line):
                break
                
            # 라인 파싱: 로그 형식이면 메시지만 추출, 아니면 전체 라인 사용
            match = self.log_pattern.match(line)
            if match:
                _, message = match.groups()
                parsed_line = self._remove_color_codes(message)
            else:
                parsed_line = self._remove_color_codes(line)
            
            if parsed_line:
                response_lines.append(parsed_line)
                
        return response_lines
    
    def _remove_color_codes(self, text):
        """ANSI 색상 코드와 게임 색상 코드 제거"""
        # ANSI 색상 코드 제거
        text = self.ansi_pattern.sub('', text)
        # 게임 색상 코드 제거 (§2, §a 등)
        text = self.game_color_pattern.sub('', text)
        return text