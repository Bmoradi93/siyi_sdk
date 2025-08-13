"""
Python implementation of ZR10 SDK by SIYI
ZR10 webpage: http://en.siyi.biz/en/Gimbal%20Camera/ZR10/overview/
Author : Mohamed Abdelkader
Email: mohamedashraf123@gmail.com
Copyright 2022

"""
from __future__ import annotations
from os import stat
from crc16_python import crc16_str_swap
import logging
from utils import toHex
from dataclasses import dataclass
from typing import Optional, List, Dict, Any


@dataclass
class FirmwareMsg:
    """Firmware version message"""
    seq: int = 0
    code_board_ver: str = ''
    gimbal_firmware_ver: str = ''
    zoom_firmware_ver: str = ''


@dataclass
class HardwareIDMsg:
    """Hardware ID message"""
    # x6B: ZR10
    # x73: A8 mini
    # x75: A2 mini
    # x78: ZR30
    # x83: ZT6
    # x7A: ZT30
    CAM_DICT: Dict[str, str] = None
    seq: int = 0
    id: str = ''
    cam_type_str: str = ''
    
    def __post_init__(self):
        if self.CAM_DICT is None:
            self.CAM_DICT = {'6B': 'ZR10', '73': 'A8 mini', '75': 'A2 mini', 
                            '78': 'ZR30', '83': 'ZT6', '7A': 'ZT30'}


@dataclass
class AutoFocusMsg:
    """Auto focus message"""
    seq: int = 0
    success: bool = False


@dataclass
class ManualZoomMsg:
    """Manual zoom message"""
    seq: int = 0
    level: int = -1


@dataclass
class ManualFocusMsg:
    """Manual focus message"""
    seq: int = 0
    success: bool = False


@dataclass
class GimbalSpeedMsg:
    """Gimbal speed message"""
    seq: int = 0
    success: bool = False


@dataclass
class CenterMsg:
    """Center gimbal message"""
    seq: int = 0
    success: bool = False


@dataclass
class RecordingMsg:
    """Recording message"""
    seq: int = 0
    state: int = -1
    OFF: int = 0
    ON: int = 1
    TF_EMPTY: int = 2
    TD_DATA_LOSS: int = 3


@dataclass
class MountDirMsg:
    """Mount direction message"""
    seq: int = 0
    dir: int = -1
    NORMAL: int = 0
    UPSIDE: int = 1


@dataclass
class MotionModeMsg:
    """Motion mode message"""
    seq: int = 0
    mode: int = -1
    LOCK: int = 0
    FOLLOW: int = 1
    FPV: int = 2


@dataclass
class FuncFeedbackInfoMsg:
    """Function feedback info message"""
    seq: int = 0
    info_type: Optional[int] = None
    SUCCESSFUL: int = 0
    PHOTO_FAIL: int = 1
    HDR_ON: int = 2
    HDR_OFF: int = 3
    RECROD_FAIL: int = 4


@dataclass
class AttitdueMsg:
    """Gimbal attitude message"""
    seq: int = 0
    stamp: float = 0.0  # seconds
    yaw: float = 0.0
    pitch: float = 0.0
    roll: float = 0.0
    yaw_speed: float = 0.0  # deg/s
    pitch_speed: float = 0.0
    roll_speed: float = 0.0


@dataclass
class SetGimbalAnglesMsg:
    """Set gimbal angles message"""
    seq: int = 0
    yaw: float = 0.0
    pitch: float = 0.0
    roll: float = 0.0


@dataclass
class RequestDataStreamMsg:
    """Request data stream message"""
    # data_type uint8_t
    ATTITUDE_DATA = '01'
    LASER_DATA = '02'

    # Frequency
    FREQ = {0: '00', 2: '01', 4: '02', 5: '03', 10: '04', 20: '05', 50: '06', 100: '07'}

    seq: int = 0 
    data_type: int = 0 # uint8_t
    freq: int = 0 # 0 means OFF (0, 2, 4, 5, 10, 20, 50, 100)


@dataclass
class RequestAbsoluteZoomMsg:
    """Request absolute zoom message"""
    seq: int = 0
    level: float = 0.0


@dataclass
class CurrentZoomValueMsg:
    """Current zoom value message"""
    seq: int = 0
    level: float = 0.0


class SIYIMESSAGE:
    """
    SIYI message protocol implementation
    """
    
    def __init__(self, debug: bool = False):
        """
        Initialize SIYI message handler
        
        Args:
            debug: Enable debug logging
        """
        self._debug = debug
        self._logger = logging.getLogger(self.__class__.__name__)
        
        # Message sequence counter
        self._seq = 0
        
        # Message constants
        self.STX = "5566"  # Start of text
        self.CTRL = "01"   # Control byte
        
    def _get_next_seq(self) -> int:
        """Get next sequence number"""
        self._seq = (self._seq + 1) % 65536
        return self._seq
    
    def _create_message(self, cmd_id: str, data: str = "") -> str:
        """
        Create a complete SIYI message
        
        Args:
            cmd_id: Command ID
            data: Optional data payload
            
        Returns:
            str: Complete hex message string
        """
        seq = self._get_next_seq()
        seq_hex = toHex(seq, 16)
        
        # Calculate data length (including sequence and command ID)
        data_len = len(seq_hex) + len(cmd_id) + len(data)
        data_len_hex = toHex(data_len, 16)
        
        # Build message without CRC
        message = self.STX + self.CTRL + data_len_hex + seq_hex + cmd_id + data
        
        # Calculate and append CRC
        crc = crc16_str_swap(message)
        message += crc
        
        if self._debug:
            self._logger.debug(f"Created message: {message}")
            
        return message
