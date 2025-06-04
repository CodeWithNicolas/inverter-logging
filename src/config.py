"""
Configuration module for SunSpec Gateway.
Handles loading and validation of configuration from YAML files.
"""

import os
import yaml
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, validator
from pathlib import Path


class ServerConfig(BaseModel):
    """Server configuration settings."""
    host: str = "0.0.0.0"
    port: int = 8080
    log_level: str = "INFO"


class TCPConfig(BaseModel):
    """TCP connection configuration."""
    host: str
    port: int = 502
    slave_id: int = 1
    timeout: int = 10


class RTUConfig(BaseModel):
    """RTU connection configuration."""
    port: str
    baudrate: int = 19200
    bytesize: int = 8
    parity: str = "N"
    stopbits: int = 1
    slave_id: int = 1
    timeout: int = 10


class InverterConfig(BaseModel):
    """Inverter connection configuration."""
    connection_type: str = Field(..., description="Connection type: 'tcp' or 'rtu'")
    tcp: Optional[TCPConfig] = None
    rtu: Optional[RTUConfig] = None
    
    @validator('connection_type')
    def validate_connection_type(cls, v):
        if v not in ['tcp', 'rtu']:
            raise ValueError("connection_type must be 'tcp' or 'rtu'")
        return v


class DataCollectionConfig(BaseModel):
    """Data collection configuration."""
    poll_interval: int = 30
    models_to_read: List[int] = Field(default=[1, 103, 160, 113])
    max_retries: int = 3
    retry_delay: int = 5


class LoggingConfig(BaseModel):
    """Logging configuration."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file: str = "gateway.log"
    max_file_size: str = "10MB"
    backup_count: int = 5


class GatewayInfo(BaseModel):
    """Gateway information."""
    name: str = "SunSpec Gateway"
    version: str = "1.0.0"
    description: str = "Production-grade brand-agnostic SunSpec inverter gateway"


class Config(BaseModel):
    """Main configuration class."""
    gateway: GatewayInfo
    server: ServerConfig
    inverter: InverterConfig
    data_collection: DataCollectionConfig
    logging: LoggingConfig


def load_config(config_path: str = "config.yaml") -> Config:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        Parsed and validated configuration
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If config file is invalid YAML
        ValueError: If configuration is invalid
    """
    config_file = Path(config_path)
    
    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Invalid YAML in config file: {e}")
    
    try:
        return Config(**config_data)
    except Exception as e:
        raise ValueError(f"Configuration validation failed: {e}")


def get_default_config() -> Config:
    """Get default configuration for development/testing."""
    return Config(
        gateway=GatewayInfo(),
        server=ServerConfig(),
        inverter=InverterConfig(
            connection_type="tcp",
            tcp=TCPConfig(host="192.168.1.100")
        ),
        data_collection=DataCollectionConfig(),
        logging=LoggingConfig()
    ) 