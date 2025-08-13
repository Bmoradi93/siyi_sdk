"""
Configuration management for SIYI SDK
"""
import os
import yaml
import json
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class CameraConfig:
    """Configuration for camera settings"""
    server_ip: str = "192.168.144.25"
    port: int = 37260
    debug: bool = False
    connection_timeout: float = 5.0
    max_retries: int = 3
    heartbeat_interval: float = 1.0
    gimbal_info_interval: float = 1.0
    gimbal_attitude_interval: float = 0.02


@dataclass
class StreamingConfig:
    """Configuration for video streaming"""
    rtsp_url: str = "rtsp://192.168.144.25:8554/main.264"
    use_udp: bool = True
    width: int = 640
    height: int = 480
    frame_rate: int = 30
    buffer_size: int = 1
    connection_timeout: float = 2.0


@dataclass
class LoggingConfig:
    """Configuration for logging"""
    level: str = "INFO"
    format: str = "[%(levelname)s] %(asctime)s [%(name)s::%(funcName)s]: %(message)s"
    file: Optional[str] = None
    max_bytes: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5


@dataclass
class SDKConfig:
    """Main SDK configuration"""
    camera: CameraConfig = None
    streaming: StreamingConfig = None
    logging: LoggingConfig = None
    
    def __post_init__(self):
        if self.camera is None:
            self.camera = CameraConfig()
        if self.streaming is None:
            self.streaming = StreamingConfig()
        if self.logging is None:
            self.logging = LoggingConfig()


class ConfigManager:
    """Manages configuration loading and validation"""
    
    DEFAULT_CONFIG_PATHS = [
        "siyi_config.yaml",
        "siyi_config.json",
        "~/.siyi_sdk/config.yaml",
        "~/.siyi_sdk/config.json",
        "/etc/siyi_sdk/config.yaml",
        "/etc/siyi_sdk/config.json"
    ]
    
    def __init__(self, config_path: Optional[Union[str, Path]] = None):
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> SDKConfig:
        """Load configuration from file, environment variables, or defaults"""
        config = SDKConfig()
        
        # Try to load from file first
        if self.config_path:
            config = self._load_from_file(self.config_path, config)
        else:
            # Try default paths
            for path in self.DEFAULT_CONFIG_PATHS:
                expanded_path = Path(path).expanduser()
                if expanded_path.exists():
                    config = self._load_from_file(expanded_path, config)
                    break
        
        # Override with environment variables
        config = self._load_from_env(config)
        
        return config
    
    def _load_from_file(self, path: Union[str, Path], config: SDKConfig) -> SDKConfig:
        """Load configuration from YAML or JSON file"""
        path = Path(path)
        if not path.exists():
            return config
            
        try:
            with open(path, 'r') as f:
                if path.suffix.lower() == '.yaml':
                    file_config = yaml.safe_load(f)
                elif path.suffix.lower() == '.json':
                    file_config = json.load(f)
                else:
                    return config
                
                # Update camera config
                if 'camera' in file_config:
                    for key, value in file_config['camera'].items():
                        if hasattr(config.camera, key):
                            setattr(config.camera, key, value)
                
                # Update streaming config
                if 'streaming' in file_config:
                    for key, value in file_config['streaming'].items():
                        if hasattr(config.streaming, key):
                            setattr(config.streaming, key, value)
                
                # Update logging config
                if 'logging' in file_config:
                    for key, value in file_config['logging'].items():
                        if hasattr(config.logging, key):
                            setattr(config.logging, key, value)
                            
        except Exception as e:
            print(f"Warning: Could not load config from {path}: {e}")
            
        return config
    
    def _load_from_env(self, config: SDKConfig) -> SDKConfig:
        """Override configuration with environment variables"""
        # Camera settings
        config.camera.server_ip = os.getenv('SIYI_CAMERA_IP', config.camera.server_ip)
        config.camera.port = int(os.getenv('SIYI_CAMERA_PORT', str(config.camera.port)))
        config.camera.debug = os.getenv('SIYI_CAMERA_DEBUG', 'false').lower() == 'true'
        config.camera.connection_timeout = float(os.getenv('SIYI_CAMERA_TIMEOUT', str(config.camera.connection_timeout)))
        config.camera.max_retries = int(os.getenv('SIYI_CAMERA_RETRIES', str(config.camera.max_retries)))
        
        # Streaming settings
        config.streaming.rtsp_url = os.getenv('SIYI_RTSP_URL', config.streaming.rtsp_url)
        config.streaming.use_udp = os.getenv('SIYI_USE_UDP', 'true').lower() == 'true'
        config.streaming.width = int(os.getenv('SIYI_STREAM_WIDTH', str(config.streaming.width)))
        config.streaming.height = int(os.getenv('SIYI_STREAM_HEIGHT', str(config.streaming.height)))
        
        # Logging settings
        config.logging.level = os.getenv('SIYI_LOG_LEVEL', config.logging.level)
        config.logging.file = os.getenv('SIYI_LOG_FILE', config.logging.file)
        
        return config
    
    def save_config(self, path: Union[str, Path]) -> None:
        """Save current configuration to file"""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        config_dict = asdict(self.config)
        
        with open(path, 'w') as f:
            if path.suffix.lower() == '.yaml':
                yaml.dump(config_dict, f, default_flow_style=False, indent=2)
            elif path.suffix.lower() == '.json':
                json.dump(config_dict, f, indent=2)
    
    def get_camera_config(self) -> CameraConfig:
        """Get camera configuration"""
        return self.config.camera
    
    def get_streaming_config(self) -> StreamingConfig:
        """Get streaming configuration"""
        return self.config.streaming
    
    def get_logging_config(self) -> LoggingConfig:
        """Get logging configuration"""
        return self.config.logging
    
    def update_camera_config(self, **kwargs) -> None:
        """Update camera configuration"""
        for key, value in kwargs.items():
            if hasattr(self.config.camera, key):
                setattr(self.config.camera, key, value)
    
    def update_streaming_config(self, **kwargs) -> None:
        """Update streaming configuration"""
        for key, value in kwargs.items():
            if hasattr(self.config.streaming, key):
                setattr(self.config.streaming, key, value)


def create_default_config(path: Union[str, Path] = "siyi_config.yaml") -> None:
    """Create a default configuration file"""
    config = SDKConfig()
    config_manager = ConfigManager()
    config_manager.config = config
    config_manager.save_config(path)
    print(f"Default configuration saved to {path}")


if __name__ == "__main__":
    # Create default config if run directly
    create_default_config() 