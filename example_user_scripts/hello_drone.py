"""
Copyright (C) Microsoft Corporation. 
Copyright (C) 2025 IAMAI CONSULTING CORP
MIT License.

Demonstrates flying a quadrotor drone with camera sensors.

Usage:
    python hello_drone.py [--address ADDRESS] [--port-topics PORT] [--port-services PORT]

Examples:
    # Run with default connection (127.0.0.1:8989:8990)
    python hello_drone.py

    # Connect to a specific address and ports
    python hello_drone.py --address 192.168.1.100 --port-topics 9000 --port-services 9001

    # Show help
    python hello_drone.py --help
"""

import asyncio
import argparse

from projectairsim import ProjectAirSimClient, Drone, World
from projectairsim.utils import projectairsim_log
from projectairsim.image_utils import ImageDisplay

def parse_args():
    parser = argparse.ArgumentParser(description='ProjectAirSim Drone Demo')
    parser.add_argument('--address', type=str, default='127.0.0.1',
                      help='Address of the AirSim server (default: 127.0.0.1)')
    parser.add_argument('--port-topics', type=int, default=8989,
                      help='Port for topics (default: 8989)')
    parser.add_argument('--port-services', type=int, default=8990,
                      help='Port for services (default: 8990)')
    return parser.parse_args()

# Async main function to wrap async drone commands
async def main():
    # Parse command line arguments
    args = parse_args()
    
    # Create a Project AirSim client with command line arguments
    client = ProjectAirSimClient(
        address=args.address,
        port_topics=args.port_topics,
        port_services=args.port_services
    )

    # Initialize an ImageDisplay object to display camera sub-windows
    image_display = ImageDisplay()


    try:
        # Connect to simulation environment
        client.connect()

        # Create a World object to interact with the sim world and load a scene
        world = World(client, "scene_basic_drone.jsonc", delay_after_load_sec=2)

        # Create a Drone object to interact with a drone in the loaded sim world
        drone = Drone(client, world, "Drone1")

        # ------------------------------------------------------------------------------

        # # Subscribe to chase camera sensor as a client-side pop-up window
        # chase_cam_window = "ChaseCam"
        # image_display.add_chase_cam(chase_cam_window)
        # client.subscribe(
        #     drone.sensors["Chase"]["scene_camera"],
        #     lambda _, chase: image_display.receive(chase, chase_cam_window),
        # )

        # # Subscribe to the downward-facing camera sensor's RGB and Depth images
        # rgb_name = "RGB-Image"
        # image_display.add_image(rgb_name, subwin_idx=0)
        # client.subscribe(
        #     drone.sensors["DownCamera"]["scene_camera"],
        #     lambda _, rgb: image_display.receive(rgb, rgb_name),
        # )

        # depth_name = "Depth-Image"
        # image_display.add_image(depth_name, subwin_idx=2)
        # client.subscribe(
        #     drone.sensors["DownCamera"]["depth_camera"],
        #     lambda _, depth: image_display.receive(depth, depth_name),
        # )

        # image_display.start()

        # ------------------------------------------------------------------------------

        # Set the drone to be ready to fly
        drone.enable_api_control()
        drone.arm()

        # ------------------------------------------------------------------------------

        projectairsim_log().info("takeoff_async: starting")
        takeoff_task = (
            await drone.takeoff_async()
        )  # schedule an async task to start the command

        # Example 1: Wait on the result of async operation using 'await' keyword
        await takeoff_task
        projectairsim_log().info("takeoff_async: completed")

        # ------------------------------------------------------------------------------

        # Command the drone to move up in NED coordinate system at 1 m/s for 4 seconds
        move_up_task = await drone.move_by_velocity_async(
            v_north=0.0, v_east=0.0, v_down=-1.0, duration=4.0
        )
        projectairsim_log().info("Move-Up invoked")

        await move_up_task
        projectairsim_log().info("Move-Up completed")

        # ------------------------------------------------------------------------------

        # Command the Drone to move down in NED coordinate system at 1 m/s for 4 seconds
        move_down_task = await drone.move_by_velocity_async(
            v_north=0.0, v_east=0.0, v_down=1.0, duration=4.0
        )  # schedule an async task to start the command
        projectairsim_log().info("Move-Down invoked")

        # Example 2: Wait for move_down_task to complete before continuing
        while not move_down_task.done():
            await asyncio.sleep(0.005)
        projectairsim_log().info("Move-Down completed")

        # ------------------------------------------------------------------------------

        projectairsim_log().info("land_async: starting")
        land_task = await drone.land_async()
        await land_task
        projectairsim_log().info("land_async: completed")

        # ------------------------------------------------------------------------------

        # Shut down the drone
        drone.disarm()
        drone.disable_api_control()

        # ------------------------------------------------------------------------------

    # logs exception on the console
    except Exception as err:
        projectairsim_log().error(f"Exception occurred: {err}", exc_info=True)

    finally:
        # Always disconnect from the simulation environment to allow next connection
        client.disconnect()

        image_display.stop()


if __name__ == "__main__":
    asyncio.run(main())  # Runner for async main function
