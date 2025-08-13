# SIYI SDK Documentation

Welcome to the SIYI SDK documentation! This SDK provides Python interfaces for controlling SIYI camera-gimbal systems.

## Table of Contents

1. [Installation](installation.md)
2. [Quick Start](quickstart.md)
3. [User Guide](userguide.md)
4. [API Reference](api.md)
5. [Examples](examples.md)
6. [Configuration](configuration.md)
7. [Troubleshooting](troubleshooting.md)
8. [Contributing](contributing.md)

## Overview

The SIYI SDK is a comprehensive Python library for controlling SIYI camera-gimbal systems. It provides:

- **Gimbal Control**: 3-axis control (yaw, pitch, roll)
- **Camera Operations**: Focus, zoom, recording, photo capture
- **Motion Modes**: Lock, Follow, and FPV modes
- **Video Streaming**: RTSP and RTMP support
- **Real-time Control**: Low-latency UDP communication
- **Cross-platform**: Works on Linux, Windows, and macOS

## Supported Cameras

- **ZR10**: Professional gimbal camera
- **A8 mini**: Compact gimbal camera
- **A2 mini**: Ultra-compact gimbal camera
- **ZR30**: High-end gimbal camera
- **ZT6**: Thermal imaging camera
- **ZT30**: Advanced thermal imaging camera

## Key Features

### 🎯 **Precise Control**
- Sub-degree accuracy for gimbal positioning
- Configurable speed control for smooth movements
- Automatic boundary checking and safety limits

### 📹 **Video Excellence**
- Real-time RTSP streaming
- RTMP output for broadcasting
- Hardware-accelerated video processing
- Low-latency video transmission

### 🔧 **Developer Friendly**
- Modern Python API with type hints
- Comprehensive error handling
- Extensive logging and debugging
- Context manager support
- Async/await ready

### 🚀 **Performance Optimized**
- Multi-threaded architecture
- Efficient message protocol
- Memory-optimized frame handling
- Connection pooling and resilience

## Quick Example

```python
from siyi_sdk import SIYISDK

# Connect to camera
with SIYISDK(server_ip="192.168.144.25", port=37260) as cam:
    # Center the gimbal
    cam.requestCenterGimbal()
    
    # Set gimbal to specific angles
    cam.setGimbalRotation(yaw=45.0, pitch=-30.0)
    
    # Take a photo
    cam.requestPhoto()
    
    # Start recording
    cam.requestRecord()
```

## Installation

```bash
# Install from PyPI
pip install siyi-sdk

# Install with optional dependencies
pip install siyi-sdk[streaming,gui,dev]

# Install from source
git clone https://github.com/mzahana/siyi_sdk.git
cd siyi_sdk
pip install -e .
```

## Requirements

- **Python**: 3.8 or higher
- **OpenCV**: For video processing
- **GStreamer**: For video streaming (optional)
- **FFmpeg**: For RTMP streaming (optional)

## Getting Help

- **Documentation**: [https://siyi-sdk.readthedocs.io/](https://siyi-sdk.readthedocs.io/)
- **GitHub Issues**: [https://github.com/mzahana/siyi_sdk/issues](https://github.com/mzahana/siyi_sdk/issues)
- **Discussions**: [https://github.com/mzahana/siyi_sdk/discussions](https://github.com/mzahana/siyi_sdk/discussions)

## License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

## Acknowledgments

- **SIYI Technology**: For providing the camera hardware and protocol specifications
- **Open Source Community**: For the excellent libraries that make this SDK possible
- **Contributors**: All the developers who have contributed to this project

---

*Last updated: December 2024* 