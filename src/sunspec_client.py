"""
SunSpec Client module for communicating with SunSpec-compliant inverters.
Uses the official pySunSpec2 library for robust, standardized communication.
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

import sunspec2.modbus.client as sunspec_client
from sunspec2.modbus.client import SunSpecModbusClientDeviceTCP, SunSpecModbusClientDeviceRTU

from .config import Config, TCPConfig, RTUConfig


logger = logging.getLogger(__name__)


class SunSpecDeviceError(Exception):
    """Custom exception for SunSpec device errors."""
    pass


class SunSpecClient:
    """
    SunSpec client for communicating with brand-agnostic SunSpec-compliant inverters.
    
    Supports:
    - Sungrow, Fronius, SMA, Huawei, ABB and other SunSpec-compliant inverters
    - Both TCP and RTU connections
    - Automatic model discovery
    - Robust error handling and retries
    """
    
    def __init__(self, config: Config):
        """
        Initialize SunSpec client.
        
        Args:
            config: Gateway configuration
        """
        self.config = config
        self.device: Optional[Union[SunSpecModbusClientDeviceTCP, SunSpecModbusClientDeviceRTU]] = None
        self.is_connected = False
        self.last_read_time: Optional[datetime] = None
        self.cached_data: Dict[str, Any] = {}
        self.available_models: Dict[int, str] = {}
        
    async def connect(self) -> bool:
        """
        Connect to the SunSpec device.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            logger.info(f"Connecting to SunSpec device via {self.config.inverter.connection_type.upper()}")
            
            if self.config.inverter.connection_type == "tcp":
                await self._connect_tcp()
            elif self.config.inverter.connection_type == "rtu":
                await self._connect_rtu()
            else:
                raise SunSpecDeviceError(f"Unsupported connection type: {self.config.inverter.connection_type}")
                
            # Perform device discovery
            await self._discover_models()
            
            self.is_connected = True
            logger.info("Successfully connected to SunSpec device")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to SunSpec device: {e}")
            self.is_connected = False
            return False
    
    async def _connect_tcp(self):
        """Connect via TCP/IP."""
        tcp_config = self.config.inverter.tcp
        if not tcp_config:
            raise SunSpecDeviceError("TCP configuration not provided")
            
        logger.info(f"Connecting to {tcp_config.host}:{tcp_config.port} (slave_id={tcp_config.slave_id})")
        
        self.device = SunSpecModbusClientDeviceTCP(
            slave_id=tcp_config.slave_id,
            ipaddr=tcp_config.host,
            ipport=tcp_config.port,
            timeout=tcp_config.timeout
        )
    
    async def _connect_rtu(self):
        """Connect via RTU (serial)."""
        rtu_config = self.config.inverter.rtu
        if not rtu_config:
            raise SunSpecDeviceError("RTU configuration not provided")
            
        logger.info(f"Connecting to {rtu_config.port} (slave_id={rtu_config.slave_id})")
        
        self.device = SunSpecModbusClientDeviceRTU(
            slave_id=rtu_config.slave_id,
            name=rtu_config.port,
            baudrate=rtu_config.baudrate,
            bytesize=rtu_config.bytesize,
            parity=rtu_config.parity,
            stopbits=rtu_config.stopbits,
            timeout=rtu_config.timeout
        )
    
    async def _discover_models(self):
        """Discover available SunSpec models on the device."""
        if not self.device:
            raise SunSpecDeviceError("Device not initialized")
            
        try:
            logger.info("Starting SunSpec model discovery...")
            # Run device scan to discover models
            await asyncio.get_event_loop().run_in_executor(None, self.device.scan)
            
            # Store available models
            self.available_models = {}
            for model_id, model_list in self.device.models.items():
                if isinstance(model_id, int):
                    # Get model name from first model in list
                    if model_list and hasattr(model_list[0], 'model_name'):
                        model_name = model_list[0].model_name
                    else:
                        model_name = f"Model_{model_id}"
                    self.available_models[model_id] = model_name
                    
            logger.info(f"Discovered {len(self.available_models)} models: {self.available_models}")
            
        except Exception as e:
            raise SunSpecDeviceError(f"Model discovery failed: {e}")
    
    async def read_data(self, model_ids: Optional[List[int]] = None) -> Dict[str, Any]:
        """
        Read data from specified SunSpec models.
        
        Args:
            model_ids: List of model IDs to read. If None, uses configured models.
            
        Returns:
            Dictionary containing read data
        """
        if not self.is_connected or not self.device:
            raise SunSpecDeviceError("Device not connected")
            
        if model_ids is None:
            model_ids = self.config.data_collection.models_to_read
            
        data = {}
        
        for model_id in model_ids:
            try:
                if model_id not in self.available_models:
                    logger.warning(f"Model {model_id} not available on device")
                    continue
                    
                # Read model data
                model_data = await self.read_model(model_id)
                if model_data:
                    data[f"model_{model_id}"] = model_data
                    
            except Exception as e:
                logger.error(f"Failed to read model {model_id}: {e}")
                continue
        
        self.cached_data = data
        self.last_read_time = datetime.now()
        return data
    
    async def read_model(self, model_id: int) -> Dict[str, Any]:
        """Read data from a specific model."""
        if not self.device or model_id not in self.device.models:
            return {}
            
        model_list = self.device.models[model_id]
        if not model_list:
            return {}
            
        # Read from the first instance of the model
        model = model_list[0]
        
        try:
            # Perform read operation
            await asyncio.get_event_loop().run_in_executor(None, model.read)
            
            # Extract point data
            points_data = {}
            if hasattr(model, 'points'):
                for point_name, point in model.points.items():
                    if hasattr(point, 'value') and point.value is not None:
                        # Use computed value if available (includes scale factors)
                        if hasattr(point, 'cvalue') and point.cvalue is not None:
                            points_data[point_name] = point.cvalue
                        else:
                            points_data[point_name] = point.value
            
            # Extract group data (for repeating groups)
            if hasattr(model, 'groups'):
                for group_name, group_list in model.groups.items():
                    if isinstance(group_list, list):
                        group_data = []
                        for i, group in enumerate(group_list):
                            group_points = {}
                            if hasattr(group, 'points'):
                                for point_name, point in group.points.items():
                                    if hasattr(point, 'value') and point.value is not None:
                                        if hasattr(point, 'cvalue') and point.cvalue is not None:
                                            group_points[point_name] = point.cvalue
                                        else:
                                            group_points[point_name] = point.value
                            group_data.append(group_points)
                        points_data[group_name] = group_data
            
            return {
                'model_id': model_id,
                'model_name': self.available_models.get(model_id, f'Model_{model_id}'),
                'points': points_data,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error reading model {model_id}: {e}")
            return {}
    
    async def write_point(self, model_id: int, point_name: str, value: Any) -> bool:
        """
        Write value to a specific point in a model.
        
        Args:
            model_id: Model ID
            point_name: Point name
            value: Value to write
            
        Returns:
            True if write successful, False otherwise
        """
        if not self.is_connected or not self.device:
            raise SunSpecDeviceError("Device not connected")
            
        try:
            if model_id not in self.device.models:
                raise SunSpecDeviceError(f"Model {model_id} not available")
                
            model_list = self.device.models[model_id]
            if not model_list:
                raise SunSpecDeviceError(f"No instances of model {model_id}")
                
            model = model_list[0]
            
            # Check if point exists
            if not hasattr(model, 'points') or point_name not in model.points:
                raise SunSpecDeviceError(f"Point {point_name} not found in model {model_id}")
                
            point = model.points[point_name]
            
            # Set the value
            if hasattr(point, 'cvalue'):
                point.cvalue = value
            else:
                point.value = value
                
            # Write to device
            await asyncio.get_event_loop().run_in_executor(None, model.write)
            
            logger.info(f"Successfully wrote {value} to {point_name} in model {model_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to write to {point_name} in model {model_id}: {e}")
            return False
    
    async def get_available_models(self) -> Dict[int, str]:
        """Get available SunSpec models on the device."""
        return self.available_models
    
    async def get_device_info(self) -> Dict[str, Any]:
        """Get basic device information from the common model."""
        if not self.is_connected:
            return {}
            
        try:
            # Model 1 is the common model with device info
            common_data = await self.read_model(1)
            if common_data and 'points' in common_data:
                return {
                    'manufacturer': common_data['points'].get('Mn', 'Unknown'),
                    'model': common_data['points'].get('Md', 'Unknown'),
                    'version': common_data['points'].get('Vr', 'Unknown'),
                    'serial_number': common_data['points'].get('SN', 'Unknown'),
                    'device_address': common_data['points'].get('DA', 1)
                }
        except Exception as e:
            logger.error(f"Failed to get device info: {e}")
            
        return {}
    
    async def disconnect(self):
        """Disconnect from the device."""
        if self.device:
            try:
                await asyncio.get_event_loop().run_in_executor(None, self.device.close)
                logger.info("Disconnected from SunSpec device")
            except Exception as e:
                logger.error(f"Error during disconnect: {e}")
            finally:
                self.device = None
                self.is_connected = False
    
    def get_cached_data(self) -> Dict[str, Any]:
        """Get the last cached data."""
        return {
            'data': self.cached_data,
            'last_read_time': self.last_read_time.isoformat() if self.last_read_time else None,
            'available_models': self.available_models
        } 