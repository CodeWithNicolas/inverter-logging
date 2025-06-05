"""
Main Gateway service that provides REST API for SunSpec inverter communication.
Handles periodic data collection and provides web interface for monitoring and control.
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel

from .config import Config, load_config
from .sunspec_client import SunSpecClient, SunSpecDeviceError


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WriteRequest(BaseModel):
    """Request model for writing to a point."""
    model_id: int
    point_name: str
    value: Any


class SunSpecGateway:
    """
    Main gateway service that manages SunSpec communication and provides REST API.
    """
    
    def __init__(self, config: Config):
        """Initialize the gateway."""
        self.config = config
        self.client = SunSpecClient(config)
        self.logger = logging.getLogger(__name__)
        self.is_connected = False
        self.last_data = {}
        self.polling_task = None
        
        # Create FastAPI app with lifespan
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            # Startup
            self.logger.info("Starting SunSpec Gateway v1.0.0")
            await self.startup()
            yield
            # Shutdown
            await self.shutdown()
        
        self.app = FastAPI(
            title="SunSpec Gateway",
            description="Production-grade brand-agnostic SunSpec inverter gateway",
            version="1.0.0",
            lifespan=lifespan
        )
        
        # Add CORS middleware to handle preflight requests
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Allow all origins
            allow_credentials=True,
            allow_methods=["*"],  # Allow all methods including OPTIONS
            allow_headers=["*"],  # Allow all headers
        )
        
        # Mount static files for web dashboard
        web_dir = Path(__file__).parent.parent / "web"
        if web_dir.exists():
            self.app.mount("/static", StaticFiles(directory=str(web_dir)), name="static")
            self.logger.info(f"Mounted static files from {web_dir}")
        
        self._setup_routes()
        
    async def startup(self):
        """Initialize gateway on startup."""
        try:
            # Connect to SunSpec device
            connected = await self.client.connect()
            if connected:
                self.is_connected = True
                self.logger.info("Initial connection to SunSpec device successful")
                
                # Start polling loop
                self.polling_task = asyncio.create_task(self._polling_loop())
                self.logger.info(f"Starting polling loop with interval {self.config.data_collection.poll_interval}s")
            else:
                self.logger.error("Failed to connect to SunSpec device")
                
        except Exception as e:
            self.logger.error(f"Startup error: {e}")
    
    async def shutdown(self):
        """Clean shutdown of gateway."""
        self.logger.info("Shutting down gateway...")
        
        # Cancel polling task
        if self.polling_task:
            self.polling_task.cancel()
            try:
                await self.polling_task
            except asyncio.CancelledError:
                self.logger.info("Polling loop cancelled")
        
        # Disconnect from device
        if self.client:
            await self.client.disconnect()
        
        self.logger.info("Gateway shutdown complete")
    
    async def _polling_loop(self):
        """Background task to poll device data."""
        while True:
            try:
                # Read data from all configured models using the correct method
                data = await self.client.read_data(self.config.data_collection.models_to_read)
                
                # Update last_data with the results
                if data:
                    for model_key, model_data in data.items():
                        self.last_data[model_key] = model_data
                
                # Wait for next poll interval
                await asyncio.sleep(self.config.data_collection.poll_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Polling loop error: {e}")
                await asyncio.sleep(5)  # Wait before retrying
    
    def _setup_routes(self):
        """Setup FastAPI routes."""
        
        @self.app.get("/", response_class=RedirectResponse)
        async def redirect_to_dashboard():
            """Redirect root to web dashboard."""
            return RedirectResponse(url="/static/index.html")
        
        @self.app.get("/api/status")
        async def get_status():
            """Get gateway status."""
            return {
                "name": "SunSpec Gateway",
                "version": "1.0.0",
                "description": "Production-grade brand-agnostic SunSpec inverter gateway",
                "status": "running",
                "connected": self.is_connected,
                "timestamp": datetime.now().isoformat()
            }
        
        @self.app.get("/device/info")
        async def get_device_info():
            """Get basic device information."""
            if not self.is_connected:
                raise HTTPException(status_code=503, detail="Device not connected")
            
            try:
                return await self.client.get_device_info()
            except Exception as e:
                self.logger.error(f"Error getting device info: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/device/models")
        async def get_available_models():
            """Get available SunSpec models."""
            if not self.is_connected:
                raise HTTPException(status_code=503, detail="Device not connected")
            
            try:
                available_models = await self.client.get_available_models()
                return {
                    "available_models": available_models,
                    "configured_models": self.config.data_collection.models_to_read
                }
            except Exception as e:
                self.logger.error(f"Error getting models: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/data/live")
        async def get_live_data():
            """Get live data from all models."""
            if not self.is_connected:
                raise HTTPException(status_code=503, detail="Device not connected")
            
            if not self.last_data:
                raise HTTPException(status_code=404, detail="No data available")
            
            return self.last_data
        
        @self.app.get("/data/model/{model_id}")
        async def get_model_data(model_id: int):
            """Get data from a specific model."""
            if not self.is_connected:
                raise HTTPException(status_code=503, detail="Device not connected")
            
            try:
                data = await self.client.read_model(model_id)
                if data is None:
                    raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
                
                return {
                    "model_id": model_id,
                    "points": data,
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                self.logger.error(f"Error reading model {model_id}: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/device/connect")
        async def connect_device():
            """Connect to SunSpec device."""
            try:
                connected = await self.client.connect()
                self.is_connected = connected
                
                if connected and not self.polling_task:
                    self.polling_task = asyncio.create_task(self._polling_loop())
                
                return {"connected": connected, "timestamp": datetime.now().isoformat()}
            except Exception as e:
                self.logger.error(f"Connection error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/device/disconnect")
        async def disconnect_device():
            """Disconnect from SunSpec device."""
            try:
                if self.polling_task:
                    self.polling_task.cancel()
                    self.polling_task = None
                
                await self.client.disconnect()
                self.is_connected = False
                
                return {"connected": False, "timestamp": datetime.now().isoformat()}
            except Exception as e:
                self.logger.error(f"Disconnection error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/config")
        async def get_config():
            """Get current configuration (excluding sensitive data)."""
            config_dict = self.config.model_dump()
            # Remove sensitive information
            if 'tcp' in config_dict.get('inverter', {}):
                config_dict['inverter']['tcp'].pop('timeout', None)
            return config_dict
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint."""
            return {
                "status": "healthy",
                "connected": self.is_connected,
                "models_configured": len(self.config.data_collection.models_to_read),
                "last_poll": max([data.get("timestamp", "") for data in self.last_data.values()]) if self.last_data else None,
                "timestamp": datetime.now().isoformat()
            }


async def create_gateway(config_path: str = "config.yaml") -> SunSpecGateway:
    """Create and initialize the gateway."""
    try:
        config = load_config(config_path)
        gateway = SunSpecGateway(config)
        return gateway
    except Exception as e:
        logger.error(f"Failed to create gateway: {e}")
        raise 