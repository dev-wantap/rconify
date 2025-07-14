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
        """명령어 라인 아래의 응답 라인들 추출"""
        response_lines = []
        collected_lines = 0
        
        for line in lines[start_index + 1:]:
            if collected_lines >= max_lines:
                break
            
            line = line.strip()
            if not line:
                continue
            
            parsed_line = self._parse_log_line(line)
            if parsed_line:
                response_lines.append(parsed_line)
                collected_lines += 1
        
        return response_lines
    
    def _parse_log_line(self, line):
        """서버 로그 라인 파싱"""
        match = self.log_pattern.match(line)
        if match:
            timestamp, message = match.groups()
            return self._remove_color_codes(message)
        return None
    
    def _remove_color_codes(self, text):
        """ANSI 색상 코드와 게임 색상 코드 제거"""
        # ANSI 색상 코드 제거
        text = self.ansi_pattern.sub('', text)
        # 게임 색상 코드 제거 (§2, §a 등)
        text = self.game_color_pattern.sub('', text)
        return text