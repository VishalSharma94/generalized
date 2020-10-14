#!/usr/bin/env python
import pika, sys, os

def main():
    credentials = pika.PlainCredentials('admin', 'qweqwe')
    parameters = pika.ConnectionParameters(host='3.82.45.61',
                                           port=5672,
                                           virtual_host='/',
                                           credentials=credentials,
                                           ssl_options=None)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    channel.queue_declare(queue='hello', durable=True)

    def callback(ch, method, properties, body):
        print(" [x] Received %r" % body)

    channel.basic_consume(queue='hello', on_message_callback=callback, auto_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)