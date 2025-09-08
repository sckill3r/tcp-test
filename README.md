# TCP Test Server

A Python-based TCP server for testing ESP32 CBRS connectivity and custom hex command transmission.

## Features

- **TCP Server**: Listens for incoming connections on configurable host/port
- **GUI Interface**: Tkinter-based control panel for monitoring connections
- **Custom Commands**: Send arbitrary hex byte commands to connected clients
- **Real-time Logging**: Monitor connection status and data transmission
- **Railway Ready**: Pre-configured for deployment on Railway platform

## Quick Start

### Local Testing
```bash
python server.py 0.0.0.0 9309
```

### Railway Deployment
1. Connect this repository to Railway
2. Railway will automatically detect Python and deploy
3. Get your public URL and port from Railway dashboard

## Usage

1. **Start the server** - The GUI will show connection status
2. **Connect your ESP32** - Configure ESP32 to connect to server IP/port
3. **Send commands** - Use the GUI to send custom hex commands
4. **Monitor logs** - Watch real-time connection and data logs

## ESP32 Configuration

Update your ESP32 code:
```c
#define YOUR_ACTACCESS24_IP "your-railway-url.railway.app"
// Update port to match Railway's assigned port
```

## Files

- `server.py` - Main TCP server with GUI
- `commands.py` - Command handling and packet construction
- `globals.py` - Global variables
- `requirements.txt` - Python dependencies (none required)
- `Procfile` - Railway deployment configuration
- `railway.json` - Railway platform configuration

## Protocol

The server expects packets in the format:
```
[Length (2 bytes)] [Host Key (1 byte)] [Command (1 byte)] [Reply Code (1 byte)] [Payload (variable)] [CRC (2 bytes)]
```

## License

MIT License