import json
import time
import pika

# Define connection parameters
connection_params = pika.ConnectionParameters(
    host="rabbitmq"  # Replace with your RabbitMQ server address if different
)

# Create a connection to RabbitMQ
connection = pika.BlockingConnection(connection_params)

# Create a channel
channel = connection.channel()

# Declare a queue (ensure the queue exists)
channel.queue_declare(queue="payment_queue", durable=True)

# # Publish a message to the queue
# channel.basic_publish(
#     exchange="",  # Default exchange
#     routing_key="test_queue",  # The name of the queue
#     body="Hello RabbitMQ!",  # The message body
#     properties=pika.BasicProperties(delivery_mode=2),  # Make the message persistent
# )

print(" [x] Sent 'Hello RabbitMQ!'")

count = 10

while count > 0:
    time.sleep(10)
    print("Waited for 10 seconds")
    count -= 1

print("Finished waiting")

channel.basic_publish(
    exchange="",
    routing_key="payment_queue",
    body=json.dumps(
        {
            "booking_id": "66b4e4cdd81677617aff5939",
            "email": "dummy25@gmail.com",
            "cost": 4,
            "result": "success",
        }
    ),
)

print("Sent 'Payment request'")

# Close the connection
connection.close()

print("Connection closed")
