# screen_handler.py
import subprocess
import tempfile
import time
from bedrock_parser import BedrockParser


class BedrockScreenHandler:
    def __init__(self, session_name):
        self.session_name = session_name
        self.output_file = tempfile.mktemp()
        self.parser = BedrockParser()

    def send_command(self, command):
        cmd = ['screen', '-S', self.session_name, '-X', 'stuff', f'{command}\n']
        subprocess.run(cmd, check=True)

    def capture_output(self):
        subprocess.run(['screen', '-S', self.session_name, '-X', 'hardcopy', self.output_file])
        with open(self.output_file, 'r', encoding='latin-1') as f:
            return f.read()

    def execute_command(self, command):
        self.send_command(command)
        time.sleep(0.3)
        raw_output = self.capture_output()
        return self.parser.get_command_response(raw_output, command)