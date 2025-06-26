import time
from azure.iot.device import IoTHubDeviceClient

# Connection string for my device
connection_string = "HostName=FisrtIoTHub1.azure-devices.net;DeviceId=Rosberrypi2;SharedAccessKey=lCJlMlQwbyZtBZ+E60SfdF7P81uxSJk0ZzzipCWDUDc="

# Creating an IoT Hub client
client = IoTHubDeviceClient.create_from_connection_string(connection_string)


# Defining a message callback function
def message_received_handler(message):
    print("Message received: ", message.data)


# Setting the message callback on the client
client.on_message_received = message_received_handler

# Connecting to Azure IoT Hub
client.connect()

try:
    while True:
        print("Robot is working...")

        time.sleep(5)

except KeyboardInterrupt:
    print("Sample stopped by user")

finally:
    # Disconnect from Azure IoT Hub
    client.disconnect()
