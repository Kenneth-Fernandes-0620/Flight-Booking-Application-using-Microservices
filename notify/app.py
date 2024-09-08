import signal
import sys
import pika
import time


def connect_to_rabbitmq():
    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host="rabbitmq", heartbeat=60)
            )
            return connection
        except pika.exceptions.AMQPConnectionError:
            print("RabbitMQ is not available. Retrying...")
            time.sleep(5)


connection = connect_to_rabbitmq()
channel = connection.channel()
channel.queue_declare(queue="payment_queue", durable=True)
channel.basic_qos(prefetch_count=100)

print("Connected to RabbitMQ")


def notify_user():
    time.sleep(10)


def callback(ch, method, properties, body):
    notify_user()
    print(f"Email sent: {body.decode()}")
    ch.basic_ack(delivery_tag=method.delivery_tag)


def signal_handler(signal, frame):
    print("\nGracefully shutting down...")
    connection.close()
    sys.exit(0)


if __name__ == "__main__":
    try:
        signal.signal(signal.SIGINT, signal_handler)
        print(" [*] Waiting for messages")
        channel.basic_consume(
            queue="payment_queue", on_message_callback=callback, auto_ack=True
        )
        channel.start_consuming()

    except Exception as e:
        print(e.args[0])
