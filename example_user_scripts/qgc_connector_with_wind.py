"""
QGC Connector with Altitude-Based Wind Application

Establishes Project AirSim <-> PX4 connection for QGroundControl use.
Automatically applies wind when drone is above 10m altitude above ground.
Keep this running while using QGC.
"""

import asyncio
from projectairsim import ProjectAirSimClient, Drone, World
from projectairsim.utils import projectairsim_log


# Wind parameters to apply when above threshold
WIND_VEL_X = 0.0  # m/s in North direction
WIND_VEL_Y = 20  # m/s in East direction
WIND_VEL_Z = 0.0  # m/s in Down direction
ALTITUDE_THRESHOLD = 10 # meters above ground
CHECK_INTERVAL = 0.5  # seconds between altitude checks


async def monitor_altitude_and_apply_wind(drone, world):
    """
    Monitors drone altitude and applies wind when above threshold.
    
    Args:
        drone: Drone object
        world: World object
    """
    wind_active = False
    ground_altitude = None
    
    while True:
        try:
            # Get current geo location (includes altitude above sea level)
            geo_location = drone.get_ground_truth_geo_location()
            current_altitude = geo_location["altitude"]
            
            # Initialize ground altitude on first reading
            if ground_altitude is None:
                ground_altitude = current_altitude
                projectairsim_log().info(f"Ground altitude initialized: {ground_altitude:.2f}m")
            
            # Calculate altitude above ground
            altitude_agl = current_altitude - ground_altitude
            
            # Check if we need to apply or remove wind
            if altitude_agl > ALTITUDE_THRESHOLD and not wind_active:
                projectairsim_log().info(
                    f"Altitude {altitude_agl:.2f}m > {ALTITUDE_THRESHOLD}m - Applying wind "
                    f"(x={WIND_VEL_X}, y={WIND_VEL_Y}, z={WIND_VEL_Z})"
                )
                world.set_wind_velocity(WIND_VEL_X, WIND_VEL_Y, WIND_VEL_Z)
                wind_active = True
                
            elif altitude_agl <= ALTITUDE_THRESHOLD and wind_active:
                projectairsim_log().info(
                    f"Altitude {altitude_agl:.2f}m <= {ALTITUDE_THRESHOLD}m - Removing wind"
                )
                world.set_wind_velocity(0.0, 0.0, 0.0)
                wind_active = False
            
            # Periodically log altitude (every 2 seconds)
            if int(asyncio.get_event_loop().time()) % 2 == 0:
                projectairsim_log().debug(
                    f"Altitude AGL: {altitude_agl:.2f}m | Wind: {'ON' if wind_active else 'OFF'}"
                )
            
        except Exception as e:
            projectairsim_log().error(f"Error monitoring altitude: {e}")
        
        await asyncio.sleep(CHECK_INTERVAL)


async def maintain_connection():
    client = ProjectAirSimClient()
    
    try:
        # Connect to simulation environment
        client.connect()
        projectairsim_log().info("Connected to Project AirSim")
        
        # Create a World object and load the scene
        world = World(client, "scene_px4_sitl.jsonc", delay_after_load_sec=2)
        projectairsim_log().info("Scene loaded")
        
        # Create a Drone object to establish the connection
        drone = Drone(client, world, "Drone1")
        
        projectairsim_log().info("=" * 60)
        projectairsim_log().info("Connection established!")
        projectairsim_log().info("QGroundControl can now connect to localhost:14550")
        projectairsim_log().info(f"Wind will be applied when altitude > {ALTITUDE_THRESHOLD}m AGL")
        projectairsim_log().info("Keep this script running while using QGC.")
        projectairsim_log().info("Press Ctrl+C to stop.")
        projectairsim_log().info("=" * 60)
        
        # Start altitude monitoring task
        monitor_task = asyncio.create_task(monitor_altitude_and_apply_wind(drone, world))
        
        # Keep the connection alive
        while True:
            await asyncio.sleep(10)
            projectairsim_log().info("Connection maintained...")
            
    except KeyboardInterrupt:
        projectairsim_log().info("Connection script stopped by user")
    except Exception as e:
        projectairsim_log().error(f"Error: {e}", exc_info=True)
    finally:
        # Ensure wind is disabled before disconnecting
        try:
            world.set_wind_velocity(0.0, 0.0, 0.0)
            projectairsim_log().info("Wind disabled")
        except:
            pass
        client.disconnect()
        projectairsim_log().info("Disconnected from simulation")


if __name__ == "__main__":
    asyncio.run(maintain_connection())