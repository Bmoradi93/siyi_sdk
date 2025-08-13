"""
Comprehensive test suite for SIYI SDK
"""
import pytest
import unittest.mock as mock
from unittest.mock import Mock, patch, MagicMock
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from siyi_sdk import SIYISDK, CameraConfig
from siyi_message import SIYIMESSAGE, FirmwareMsg, HardwareIDMsg
from config import ConfigManager, SDKConfig


class TestCameraConfig:
    """Test CameraConfig dataclass"""
    
    def test_default_values(self):
        """Test default configuration values"""
        config = CameraConfig()
        assert config.server_ip == "192.168.144.25"
        assert config.port == 37260
        assert config.debug is False
        assert config.connection_timeout == 5.0
        assert config.max_retries == 3
    
    def test_custom_values(self):
        """Test custom configuration values"""
        config = CameraConfig(
            server_ip="192.168.1.100",
            port=8080,
            debug=True,
            connection_timeout=10.0
        )
        assert config.server_ip == "192.168.1.100"
        assert config.port == 8080
        assert config.debug is True
        assert config.connection_timeout == 10.0


class TestSIYISDK:
    """Test SIYI SDK class"""
    
    @pytest.fixture
    def mock_socket(self):
        """Mock socket for testing"""
        with mock.patch('socket.socket') as mock_sock:
            mock_sock.return_value.recvfrom.return_value = (b'test_data', ('192.168.144.25', 37260))
            yield mock_sock
    
    @pytest.fixture
    def mock_siyi_message(self):
        """Mock SIYI message handler"""
        with mock.patch('siyi_sdk.SIYIMESSAGE') as mock_msg:
            mock_msg.return_value.getFirmwareVersion.return_value = "test_message"
            yield mock_msg
    
    @pytest.fixture
    def sdk_instance(self, mock_socket, mock_siyi_message):
        """Create SDK instance for testing"""
        return SIYISDK(debug=True)
    
    def test_init_default_config(self):
        """Test SDK initialization with default config"""
        sdk = SIYISDK()
        assert sdk._server_ip == "192.168.144.25"
        assert sdk._port == 37260
        assert sdk._debug is False
    
    def test_init_custom_config(self):
        """Test SDK initialization with custom config"""
        config = CameraConfig(
            server_ip="192.168.1.100",
            port=8080,
            debug=True
        )
        sdk = SIYISDK(config=config)
        assert sdk._server_ip == "192.168.1.100"
        assert sdk._port == 8080
        assert sdk._debug is True
    
    def test_init_kwargs_override(self):
        """Test that kwargs override config values"""
        sdk = SIYISDK(server_ip="192.168.1.200", port=9000)
        assert sdk._server_ip == "192.168.1.200"
        assert sdk._port == 9000
    
    def test_context_manager(self, mock_socket, mock_siyi_message):
        """Test context manager functionality"""
        with mock.patch.object(SIYISDK, 'connect', return_value=True):
            with mock.patch.object(SIYISDK, 'disconnect'):
                with SIYISDK() as sdk:
                    assert isinstance(sdk, SIYISDK)
    
    def test_context_manager_connection_failure(self, mock_socket, mock_siyi_message):
        """Test context manager with connection failure"""
        with mock.patch.object(SIYISDK, 'connect', return_value=False):
            with pytest.raises(ConnectionError):
                with SIYISDK():
                    pass
    
    def test_safe_operation(self, sdk_instance):
        """Test safe operation context manager"""
        with sdk_instance.safe_operation("test_op"):
            pass  # Should not raise any exception
    
    def test_safe_operation_with_error(self, sdk_instance):
        """Test safe operation context manager with error"""
        with pytest.raises(Exception):
            with sdk_instance.safe_operation("test_op"):
                raise Exception("Test error")
    
    def test_connect_success(self, sdk_instance, mock_socket):
        """Test successful connection"""
        with mock.patch.object(sdk_instance, '_test_connection', return_value=True):
            with mock.patch.object(sdk_instance, '_start_threads'):
                result = sdk_instance.connect()
                assert result is True
    
    def test_connect_failure(self, sdk_instance, mock_socket):
        """Test connection failure"""
        with mock.patch.object(sdk_instance, '_test_connection', return_value=False):
            result = sdk_instance.connect()
            assert result is False
    
    def test_connect_with_retries(self, sdk_instance, mock_socket):
        """Test connection with retries"""
        with mock.patch.object(sdk_instance, '_test_connection', side_effect=[False, False, True]):
            with mock.patch.object(sdk_instance, '_start_threads'):
                with mock.patch('time.sleep'):
                    result = sdk_instance.connect(maxRetries=3)
                    assert result is True
    
    def test_disconnect(self, sdk_instance):
        """Test disconnection"""
        sdk_instance._stop = False
        sdk_instance._recv_thread = Mock()
        sdk_instance._conn_thread = Mock()
        sdk_instance._g_info_thread = Mock()
        sdk_instance._g_att_thread = Mock()
        sdk_instance._socket = Mock()
        
        # Mock threads as alive
        for thread in [sdk_instance._recv_thread, sdk_instance._conn_thread, 
                      sdk_instance._g_info_thread, sdk_instance._g_att_thread]:
            thread.is_alive.return_value = True
            thread.join.return_value = None
        
        sdk_instance.disconnect()
        
        assert sdk_instance._stop is True
        assert sdk_instance._connected is False
        assert sdk_instance._socket is None
    
    def test_send_message_success(self, sdk_instance, mock_socket):
        """Test successful message sending"""
        sdk_instance._socket = mock_socket.return_value
        sdk_instance._connected = True
        
        sdk_instance._send_message(b"test_message")
        mock_socket.return_value.sendto.assert_called_once()
    
    def test_send_message_no_socket(self, sdk_instance):
        """Test message sending without socket"""
        sdk_instance._socket = None
        
        with pytest.raises(ConnectionError, match="Socket not initialized"):
            sdk_instance._send_message(b"test_message")
    
    def test_send_message_not_connected(self, sdk_instance):
        """Test message sending when not connected"""
        sdk_instance._socket = Mock()
        sdk_instance._connected = False
        
        with pytest.raises(ConnectionError):
            sdk_instance._send_message(b"test_message")
    
    def test_is_connected(self, sdk_instance):
        """Test connection status check"""
        sdk_instance._connected = True
        sdk_instance._socket = Mock()
        assert sdk_instance.is_connected() is True
        
        sdk_instance._connected = False
        assert sdk_instance.is_connected() is False
        
        sdk_instance._connected = True
        sdk_instance._socket = None
        assert sdk_instance.is_connected() is False
    
    def test_get_connection_info(self, sdk_instance):
        """Test connection info retrieval"""
        sdk_instance._connected = True
        sdk_instance._socket = Mock()
        sdk_instance._last_fw_seq = 42
        
        info = sdk_instance.get_connection_info()
        assert info['connected'] is True
        assert info['server_ip'] == "192.168.144.25"
        assert info['port'] == 37260
        assert info['socket_active'] is True
        assert info['last_fw_seq'] == 42
    
    def test_send_msg_success(self, sdk_instance):
        """Test successful message sending via sendMsg"""
        with mock.patch.object(sdk_instance, 'is_connected', return_value=True):
            with mock.patch.object(sdk_instance, '_send_message'):
                result = sdk_instance.sendMsg("test_hex_message")
                assert result is True
    
    def test_send_msg_not_connected(self, sdk_instance):
        """Test message sending when not connected"""
        with mock.patch.object(sdk_instance, 'is_connected', return_value=False):
            result = sdk_instance.sendMsg("test_hex_message")
            assert result is False
    
    def test_rcv_msg_success(self, sdk_instance, mock_socket):
        """Test successful message receiving"""
        sdk_instance._socket = mock_socket.return_value
        sdk_instance._connected = True
        
        result = sdk_instance.rcvMsg()
        assert result == b'test_data'
    
    def test_rcv_msg_not_connected(self, sdk_instance):
        """Test message receiving when not connected"""
        sdk_instance._connected = False
        
        result = sdk_instance.rcvMsg()
        assert result is None
    
    def test_rcv_msg_timeout(self, sdk_instance, mock_socket):
        """Test message receiving with timeout"""
        sdk_instance._socket = mock_socket.return_value
        sdk_instance._connected = True
        mock_socket.return_value.recvfrom.side_effect = TimeoutError("timeout")
        
        result = sdk_instance.rcvMsg()
        assert result is None


class TestSIYIMESSAGE:
    """Test SIYI message handling"""
    
    def test_init(self):
        """Test message handler initialization"""
        msg_handler = SIYIMESSAGE(debug=True)
        assert msg_handler._debug is True
        assert msg_handler._seq == 0
        assert msg_handler.STX == "5566"
        assert msg_handler.CTRL == "01"
    
    def test_get_next_seq(self):
        """Test sequence number generation"""
        msg_handler = SIYIMESSAGE()
        
        seq1 = msg_handler._get_next_seq()
        assert seq1 == 1
        
        seq2 = msg_handler._get_next_seq()
        assert seq2 == 2
        
        # Test wrap-around
        msg_handler._seq = 65535
        seq3 = msg_handler._get_next_seq()
        assert seq3 == 0
    
    def test_create_message(self):
        """Test message creation"""
        msg_handler = SIYIMESSAGE(debug=True)
        
        with mock.patch('siyi_message.crc16_str_swap', return_value="abcd"):
            message = msg_handler._create_message("01", "test_data")
            
            assert message.startswith("5566")
            assert message.endswith("abcd")
            assert "01" in message
            assert "test_data" in message


class TestConfigManager:
    """Test configuration management"""
    
    def test_init_default(self):
        """Test default configuration initialization"""
        config_manager = ConfigManager()
        config = config_manager.config
        
        assert isinstance(config, SDKConfig)
        assert isinstance(config.camera, CameraConfig)
        assert isinstance(config.streaming, StreamingConfig)
        assert isinstance(config.logging, LoggingConfig)
    
    def test_load_from_env(self):
        """Test environment variable loading"""
        with mock.patch.dict(os.environ, {
            'SIYI_CAMERA_IP': '192.168.1.100',
            'SIYI_CAMERA_PORT': '8080',
            'SIYI_CAMERA_DEBUG': 'true'
        }):
            config_manager = ConfigManager()
            camera_config = config_manager.get_camera_config()
            
            assert camera_config.server_ip == '192.168.1.100'
            assert camera_config.port == 8080
            assert camera_config.debug is True
    
    def test_update_camera_config(self):
        """Test camera configuration updates"""
        config_manager = ConfigManager()
        
        config_manager.update_camera_config(
            server_ip='192.168.1.200',
            port=9000
        )
        
        camera_config = config_manager.get_camera_config()
        assert camera_config.server_ip == '192.168.1.200'
        assert camera_config.port == 9000


class TestIntegration:
    """Integration tests (require mock camera)"""
    
    @pytest.mark.integration
    def test_full_workflow(self):
        """Test complete SDK workflow with mocked camera"""
        # This would test the full workflow with a mock camera
        # Implementation depends on having a mock camera or simulator
        pass
    
    @pytest.mark.slow
    def test_performance(self):
        """Test SDK performance characteristics"""
        # This would test performance with various loads
        pass


# Mock tests for when hardware is not available
class TestMockCamera:
    """Tests using mock camera responses"""
    
    def test_mock_firmware_response(self):
        """Test handling of mock firmware response"""
        # Mock firmware response data
        mock_response = b'\x55\x66\x01\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00\x00\x00\x00'
        
        # This would test parsing of the mock response
        # Implementation depends on the specific message format
        pass
    
    def test_mock_hardware_id_response(self):
        """Test handling of mock hardware ID response"""
        # Mock hardware ID response data
        mock_response = b'\x55\x66\x01\x00\x00\x00\x02\x00\x6B\x00\x00\x00\x00\x00\x00\x00'
        
        # This would test parsing of the mock response
        pass


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"]) 