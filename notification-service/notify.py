import signal
import sys
import pika
import time

connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
channel = connection.channel()
channel.queue_declare(queue="payment_queue")


def notify_user():
    time.sleep(10)


def callback(ch, method, properties, body):
    notify_user()
    print(f"Email sent: {body.decode()}")


def signal_handler(signal, frame):
    print("\nGracefully shutting down...")
    connection.close()
    sys.exit(0)


if __name__ == "__main__":
    try:
        signal.signal(signal.SIGINT, signal_handler)
        print(" [*] Waiting for messages. To exit press CTRL+C")
        channel.basic_consume(
            queue="payment_queue", on_message_callback=callback, auto_ack=True
        )
        channel.start_consuming()

    except Exception as e:
        print(e.args[0])
