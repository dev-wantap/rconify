# RCONify - RCON Bridge for Minecraft Bedrock Dedicated Server

RCONify is a Python-based bridge server that provides RCON (Remote Console) functionality to Minecraft Bedrock Edition servers, which do not natively support the RCON protocol.

This project allows you to remotely execute commands on a Bedrock server running in a `screen` session and retrieve the output.

## Key Features

-   **RCON Support**: Enables the use of standard RCON clients (e.g., `mcrcon`) to connect to and execute commands on a Bedrock server.
-   **Screen Integration**: Interacts with the server console running within a `screen` session.
-   **Intelligent Response Parsing**: Intelligently parses the actual command response from the full screen output.
-   **Pure Python**: Works with only the Python standard library, requiring no external dependencies.

## How It Works

1.  The RCONify server listens for connections from RCON clients on a specified port (default: 25575).
2.  When a client sends a command after authentication, RCONify injects the command into the Bedrock server's console using `screen -X stuff`.
3.  After a short delay, it captures the entire screen content to a text file using `screen -X hardcopy`.
4.  It then parses this text file—which contains a mix of server logs, the command, and its output—to extract only the relevant response lines.
5.  The extracted result is formatted according to the RCON protocol and sent back to the client.

## Requirements

-   Python 3.x
-   `screen` utility
-   A Minecraft Bedrock server running within a `screen` session

## Installation and Usage

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/dev-wantap/rconify.git
    cd rconify
    ```

2.  **Start the RCONify server:**
    Run `main.py` and pass the name of the `screen` session where your Bedrock server is running as an argument.

    ```bash
    python3 main.py <screen_session_name>
    ```
    *   Example: If your `screen` session is named `bedrock`:
        ```bash
        python3 main.py bedrock
        ```

3.  **Connect with an RCON client:**
    You can now use an RCON client like `mcrcon` to connect to the server.

    ```bash
    mcrcon -H 127.0.0.1 -P 25575 -p password "list"
    ```
    *   The default password is `password`. You can change it in the `rcon_server.py` source file.

## Configuration

The RCON server's host, port, and password can be modified directly at the top of the `rcon_server.py` file.

```python
# rcon_server.py

class RCONServer:
    def __init__(self, screen_handler, host='0.0.0.0', port=25575, password='password'):
        # ...
```
