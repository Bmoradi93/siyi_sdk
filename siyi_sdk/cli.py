#!/usr/bin/env python3
"""
Command-line interface for SIYI SDK
"""
import argparse
import sys
import logging
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from siyi_sdk import SIYISDK
from config import ConfigManager, create_default_config


def setup_logging(level: str = "INFO", log_file: Optional[str] = None) -> None:
    """Setup logging configuration"""
    log_level = getattr(logging, level.upper())
    
    # Create formatter
    formatter = logging.Formatter(
        '[%(levelname)s] %(asctime)s [%(name)s::%(funcName)s]: %(message)s'
    )
    
    # Setup console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)
    
    # Setup file handler if specified
    handlers = [console_handler]
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(log_level)
        handlers.append(file_handler)
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        handlers=handlers,
        format='[%(levelname)s] %(asctime)s [%(name)s::%(funcName)s]: %(message)s'
    )


def test_connection(args) -> int:
    """Test connection to camera"""
    print(f"Testing connection to {args.ip}:{args.port}...")
    
    try:
        with SIYISDK(server_ip=args.ip, port=args.port, debug=args.debug) as cam:
            print("✓ Successfully connected to camera")
            
            # Get camera info
            if cam.requestHardwareID():
                print(f"✓ Hardware ID request sent")
            
            if cam.requestFirmwareVersion():
                print(f"✓ Firmware version request sent")
            
            # Wait a bit for responses
            import time
            time.sleep(1)
            
            # Print connection info
            info = cam.get_connection_info()
            print(f"Connection info: {info}")
            
            return 0
            
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return 1


def get_camera_info(args) -> int:
    """Get camera information"""
    print(f"Getting camera info from {args.ip}:{args.port}...")
    
    try:
        with SIYISDK(server_ip=args.ip, port=args.port, debug=args.debug) as cam:
            print("✓ Connected to camera")
            
            # Request hardware ID
            if cam.requestHardwareID():
                print("✓ Hardware ID request sent")
                time.sleep(0.5)
                
                # Get hardware info from message object
                hw_msg = cam._hw_msg
                if hw_msg.id:
                    print(f"Hardware ID: {hw_msg.id}")
                    print(f"Camera Type: {hw_msg.cam_type_str}")
                else:
                    print("Hardware ID not yet received")
            
            # Request firmware version
            if cam.requestFirmwareVersion():
                print("✓ Firmware version request sent")
                time.sleep(0.5)
                
                # Get firmware info from message object
                fw_msg = cam._fw_msg
                if fw_msg.gimbal_firmware_ver:
                    print(f"Gimbal Firmware: {fw_msg.gimbal_firmware_ver}")
                    print(f"Zoom Firmware: {fw_msg.zoom_firmware_ver}")
                    print(f"Code Board Version: {fw_msg.code_board_ver}")
                else:
                    print("Firmware info not yet received")
            
            return 0
            
    except Exception as e:
        print(f"✗ Failed to get camera info: {e}")
        return 1


def control_gimbal(args) -> int:
    """Control gimbal movement"""
    print(f"Controlling gimbal on {args.ip}:{args.port}...")
    
    try:
        with SIYISDK(server_ip=args.ip, port=args.port, debug=args.debug) as cam:
            print("✓ Connected to camera")
            
            if args.command == "center":
                print("Centering gimbal...")
                if cam.requestCenterGimbal():
                    print("✓ Center command sent")
                else:
                    print("✗ Failed to send center command")
                    
            elif args.command == "angles":
                print(f"Setting gimbal angles: yaw={args.yaw}, pitch={args.pitch}")
                if cam.setGimbalRotation(args.yaw, args.pitch):
                    print("✓ Angle command sent")
                else:
                    print("✗ Failed to send angle command")
                    
            elif args.command == "speed":
                print(f"Setting gimbal speed: yaw={args.yaw_speed}, pitch={args.pitch_speed}")
                if cam.requestGimbalSpeed(args.yaw_speed, args.pitch_speed):
                    print("✓ Speed command sent")
                else:
                    print("✗ Failed to send speed command")
            
            return 0
            
    except Exception as e:
        print(f"✗ Failed to control gimbal: {e}")
        return 1


def control_camera(args) -> int:
    """Control camera functions"""
    print(f"Controlling camera on {args.ip}:{args.port}...")
    
    try:
        with SIYISDK(server_ip=args.ip, port=args.port, debug=args.debug) as cam:
            print("✓ Connected to camera")
            
            if args.command == "photo":
                print("Taking photo...")
                if cam.requestPhoto():
                    print("✓ Photo command sent")
                else:
                    print("✗ Failed to send photo command")
                    
            elif args.command == "record":
                if args.action == "start":
                    print("Starting recording...")
                    if cam.requestRecord():
                        print("✓ Record start command sent")
                    else:
                        print("✗ Failed to send record start command")
                elif args.action == "stop":
                    print("Stopping recording...")
                    if cam.requestRecord():
                        print("✓ Record stop command sent")
                    else:
                        print("✗ Failed to send record stop command")
                        
            elif args.command == "focus":
                if args.action == "auto":
                    print("Auto focusing...")
                    if cam.requestAutoFocus():
                        print("✓ Auto focus command sent")
                    else:
                        print("✗ Failed to send auto focus command")
                        
            elif args.command == "zoom":
                if args.action == "in":
                    print("Zooming in...")
                    if cam.requestZoomIn():
                        print("✓ Zoom in command sent")
                    else:
                        print("✗ Failed to send zoom in command")
                elif args.action == "out":
                    print("Zooming out...")
                    if cam.requestZoomOut():
                        print("✓ Zoom out command sent")
                    else:
                        print("✗ Failed to send zoom out command")
                elif args.action == "stop":
                    print("Stopping zoom...")
                    if cam.requestZoomHold():
                        print("✓ Zoom stop command sent")
                    else:
                        print("✗ Failed to send zoom stop command")
            
            return 0
            
    except Exception as e:
        print(f"✗ Failed to control camera: {e}")
        return 1


def set_mode(args) -> int:
    """Set camera mode"""
    print(f"Setting camera mode on {args.ip}:{args.port}...")
    
    try:
        with SIYISDK(server_ip=args.ip, port=args.port, debug=args.debug) as cam:
            print("✓ Connected to camera")
            
            if args.mode == "lock":
                print("Setting lock mode...")
                if cam.requestLockMode():
                    print("✓ Lock mode command sent")
                else:
                    print("✗ Failed to send lock mode command")
                    
            elif args.mode == "follow":
                print("Setting follow mode...")
                if cam.requestFollowMode():
                    print("✓ Follow mode command sent")
                else:
                    print("✗ Failed to send follow mode command")
                    
            elif args.mode == "fpv":
                print("Setting FPV mode...")
                if cam.requestFpvMode():
                    print("✓ FPV mode command sent")
                else:
                    print("✗ Failed to send FPV mode command")
            
            return 0
            
    except Exception as e:
        print(f"✗ Failed to set mode: {e}")
        return 1


def main() -> int:
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="SIYI SDK Command Line Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test connection
  siyi-sdk test --ip 192.168.144.25 --port 37260
  
  # Get camera info
  siyi-sdk info --ip 192.168.144.25
  
  # Center gimbal
  siyi-sdk gimbal center --ip 192.168.144.25
  
  # Set gimbal angles
  siyi-sdk gimbal angles --yaw 45 --pitch -30 --ip 192.168.144.25
  
  # Take photo
  siyi-sdk camera photo --ip 192.168.144.25
  
  # Set follow mode
  siyi-sdk mode follow --ip 192.168.144.25
        """
    )
    
    # Global arguments
    parser.add_argument(
        "--ip", 
        default="192.168.144.25",
        help="Camera IP address (default: 192.168.144.25)"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=37260,
        help="Camera port (default: 37260)"
    )
    parser.add_argument(
        "--debug", 
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--config", 
        help="Path to configuration file"
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Test command
    test_parser = subparsers.add_parser("test", help="Test camera connection")
    test_parser.set_defaults(func=test_connection)
    
    # Info command
    info_parser = subparsers.add_parser("info", help="Get camera information")
    info_parser.set_defaults(func=get_camera_info)
    
    # Gimbal control commands
    gimbal_parser = subparsers.add_parser("gimbal", help="Control gimbal")
    gimbal_subparsers = gimbal_parser.add_subparsers(dest="gimbal_command", help="Gimbal commands")
    
    center_parser = gimbal_subparsers.add_parser("center", help="Center gimbal")
    center_parser.set_defaults(func=control_gimbal, command="center")
    
    angles_parser = gimbal_subparsers.add_parser("angles", help="Set gimbal angles")
    angles_parser.add_argument("--yaw", type=float, required=True, help="Yaw angle in degrees")
    angles_parser.add_argument("--pitch", type=float, required=True, help="Pitch angle in degrees")
    angles_parser.set_defaults(func=control_gimbal, command="angles")
    
    speed_parser = gimbal_subparsers.add_parser("speed", help="Set gimbal speed")
    speed_parser.add_argument("--yaw-speed", type=int, required=True, help="Yaw speed (-100 to 100)")
    speed_parser.add_argument("--pitch-speed", type=int, required=True, help="Pitch speed (-100 to 100)")
    speed_parser.set_defaults(func=control_gimbal, command="speed")
    
    # Camera control commands
    camera_parser = subparsers.add_parser("camera", help="Control camera functions")
    camera_subparsers = camera_parser.add_subparsers(dest="camera_command", help="Camera commands")
    
    photo_parser = camera_subparsers.add_parser("photo", help="Take photo")
    photo_parser.set_defaults(func=control_camera, command="photo")
    
    record_parser = camera_subparsers.add_parser("record", help="Control recording")
    record_parser.add_argument("action", choices=["start", "stop"], help="Recording action")
    record_parser.set_defaults(func=control_camera, command="record")
    
    focus_parser = camera_subparsers.add_parser("focus", help="Control focus")
    focus_parser.add_argument("action", choices=["auto"], help="Focus action")
    focus_parser.set_defaults(func=control_camera, command="focus")
    
    zoom_parser = camera_subparsers.add_parser("zoom", help="Control zoom")
    zoom_parser.add_argument("action", choices=["in", "out", "stop"], help="Zoom action")
    zoom_parser.set_defaults(func=control_camera, command="zoom")
    
    # Mode commands
    mode_parser = subparsers.add_parser("mode", help="Set camera mode")
    mode_parser.add_argument("mode", choices=["lock", "follow", "fpv"], help="Camera mode")
    mode_parser.set_defaults(func=set_mode)
    
    # Config commands
    config_parser = subparsers.add_parser("config", help="Configuration management")
    config_subparsers = config_parser.add_subparsers(dest="config_command", help="Config commands")
    
    create_config_parser = config_subparsers.add_parser("create", help="Create default configuration file")
    create_config_parser.add_argument("--path", default="siyi_config.yaml", help="Path for config file")
    create_config_parser.set_defaults(func=lambda args: create_default_config(args.path) or 0)
    
    # Parse arguments
    args = parser.parse_args()
    
    # Load configuration if specified
    if args.config:
        config_manager = ConfigManager(args.config)
        # Override command line arguments with config
        camera_config = config_manager.get_camera_config()
        args.ip = camera_config.server_ip
        args.port = camera_config.port
        args.debug = camera_config.debug
    
    # Setup logging
    setup_logging("DEBUG" if args.debug else "INFO")
    
    # Handle no command
    if not hasattr(args, 'func'):
        parser.print_help()
        return 1
    
    # Execute command
    try:
        return args.func(args)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 130
    except Exception as e:
        print(f"Error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main()) 