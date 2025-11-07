"""
Simple connector script to establish Project AirSim <-> PX4 connection for QGroundControl use.
Keep this running while using QGC.
"""

import asyncio
from projectairsim import ProjectAirSimClient, Drone, World
from projectairsim.utils import projectairsim_log


async def maintain_connection():
    client = ProjectAirSimClient()
    
    try:
        # Connect to simulation environment
        client.connect()
        
        # Create a World object and load the scene
        world = World(client, "scene_px4_sitl.jsonc", delay_after_load_sec=2)
        
        # Create a Drone object to establish the connection
        drone = Drone(client, world, "Drone1")
        
        projectairsim_log().info("Connection established. QGroundControl can now connect to localhost:14550")
        projectairsim_log().info("Keep this script running while using QGC. Press Ctrl+C to stop.")
        
        # Keep the connection alive
        while True:
            await asyncio.sleep(10)
            projectairsim_log().info("Connection maintained...")
            
    except KeyboardInterrupt:
        projectairsim_log().info("Connection script stopped by user")
    except Exception as e:
        projectairsim_log().error(f"Error: {e}")
    finally:
        client.disconnect()


if __name__ == "__main__":
    asyncio.run(maintain_connection())