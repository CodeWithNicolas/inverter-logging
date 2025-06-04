#!/usr/bin/env python3
"""
Main entry point for the SunSpec Gateway.
Production-grade brand-agnostic gateway for SunSpec-compliant inverters.
"""

import asyncio
import signal
import sys
import logging
from pathlib import Path

import uvicorn
from dotenv import load_dotenv

from src.gateway import create_gateway
from src.config import load_config


# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('gateway.log')
    ]
)
logger = logging.getLogger(__name__)


class GatewayManager:
    """Manages the gateway lifecycle."""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.gateway = None
        self.server = None
        
    async def start(self):
        """Start the gateway and web server."""
        try:
            # Load configuration
            config = load_config(self.config_path)
            
            # Create and initialize gateway
            logger.info("Initializing SunSpec Gateway...")
            self.gateway = await create_gateway(self.config_path)
            
            # Setup signal handlers for graceful shutdown
            self._setup_signal_handlers()
            
            # Start the web server
            server_config = uvicorn.Config(
                app=self.gateway.app,
                host=config.server.host,
                port=config.server.port,
                log_level=config.server.log_level.lower(),
                reload=False,
                access_log=True
            )
            
            self.server = uvicorn.Server(server_config)
            
            logger.info(f"Starting web server on {config.server.host}:{config.server.port}")
            await self.server.serve()
            
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        except Exception as e:
            logger.error(f"Gateway startup failed: {e}")
            sys.exit(1)
        finally:
            await self.shutdown()
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}")
            asyncio.create_task(self.shutdown())
        
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
    
    async def shutdown(self):
        """Graceful shutdown of the gateway."""
        logger.info("Initiating graceful shutdown...")
        
        # Stop the web server
        if self.server:
            self.server.should_exit = True
        
        # Shutdown the gateway
        if self.gateway:
            await self.gateway.shutdown()
        
        logger.info("Shutdown complete")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="SunSpec Gateway - Production-grade brand-agnostic SunSpec inverter gateway"
    )
    parser.add_argument(
        "--config", 
        default="config.yaml",
        help="Path to configuration file (default: config.yaml)"
    )
    parser.add_argument(
        "--version",
        action="version",
        version="SunSpec Gateway 1.0.0"
    )
    
    args = parser.parse_args()
    
    # Check if config file exists
    config_path = Path(args.config)
    if not config_path.exists():
        logger.error(f"Configuration file not found: {args.config}")
        logger.info("Please create a config.yaml file or specify the path with --config")
        sys.exit(1)
    
    # Create and run the gateway
    manager = GatewayManager(args.config)
    
    try:
        asyncio.run(manager.start())
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 