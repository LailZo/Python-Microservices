# # myproject/views.py
# from rest_framework import status
# from rest_framework.response import Response
# from rest_framework.views import APIView
# from .models import Order
# from .serializers import OrderSerializer
# import pika
# import json
# from datetime import datetime

# class OrderView(APIView):
#     def post(self, request, *args, **kwargs):
#         serializer = OrderSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             # Publish message to RabbitMQ
#             self.publish_message(serializer.data)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def publish_message(self, order_data):
#         try:
#             credentials = pika.PlainCredentials('hellofresh', 'food')
#             parameters = pika.ConnectionParameters('localhost', 5672, '/', credentials)
#             connection = pika.BlockingConnection(parameters)
#             channel = connection.channel()

#             # Declare an exchange
#             channel.exchange_declare(exchange='orders', exchange_type='direct')

#             # Publish the message to the exchange with routing key 'created_order'
#             channel.basic_publish(
#                 exchange='orders',
#                 routing_key='created_order',
#                 body=self.build_message(order_data),
#                 properties=pika.BasicProperties(
#                     delivery_mode=2,  # Make the message persistent
#                 )
#             )

#             connection.close()
#             print("Message published successfully")
#         except Exception as e:
#             print(f"Error publishing message to RabbitMQ: {e}")

#     def build_message(self, order_data):
#         # Use the actual current date and time
#         current_datetime = datetime.utcnow().isoformat()

#         # Implement the message format as per the given schema
#         message = {
#             "producer": "OrderService",
#             "sent_at": current_datetime,
#             "type": "created_order",
#             "payload": {
#                 "order": {
#                     "order_id": order_data["id"],
#                     "customer_fullname": order_data["customer_fullname"],
#                     "product_name": order_data["product_name"],
#                     "total_amount": order_data["total_amount"],
#                     "created_at": order_data["created_at"].isoformat(),
#                 }
#             }
#         }
#         return json.dumps(message)





import asyncio
import json
from datetime import datetime
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Order
from .serializers import OrderSerializer
import aio_pika

class OrderView(APIView):
    # Asynchronous method to handle HTTP POST requests
    async def post(self, request, *args, **kwargs):
        # Deserialize the incoming JSON data using the OrderSerializer
        serializer = OrderSerializer(data=request.data)
        
        # Check if the data is valid
        if serializer.is_valid():
            # Save the valid data to the database
            serializer.save()
            
            # Asynchronously publish a message to RabbitMQ
            await self.publish_message(serializer.data)
            
            # Return a success response with the serialized data
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        # Return an error response if the data is not valid
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Asynchronous method to publish a message to RabbitMQ
    async def publish_message(self, order_data):
        try:
            # Set up RabbitMQ connection credentials
            credentials = aio_pika.PlainCredentials('hellofresh', 'food')
            parameters = aio_pika.ConnectionParameters('localhost', 5672, '/', credentials)
            
            # Establish a robust asynchronous connection to RabbitMQ
            connection = await aio_pika.connect_robust(parameters)
            # Create a channel for communication
            channel = await connection.channel()

            # Declare a RabbitMQ exchange named 'orders' with a direct type
            await channel.exchange_declare(exchange='orders', exchange_type='direct')

            # Publish the message to the 'orders' exchange with a routing key 'created_order'
            await channel.basic_publish(
                exchange='orders',
                routing_key='created_order',
                body=self.build_message(order_data),
                properties=aio_pika.BasicProperties(
                    delivery_mode=2,  # Make the message persistent
                )
            )

            # Close the RabbitMQ connection
            await connection.close()
            print("Message published successfully")
        
        # Handle exceptions and print an error message
        except Exception as e:
            print(f"Error publishing message to RabbitMQ: {e}")

    # Method to build a JSON message based on the provided order data
    def build_message(self, order_data):
        # Get the current UTC date and time in ISO format
        current_datetime = datetime.utcnow().isoformat()
        
        # Build a structured message in the required format
        message = {
            "producer": "OrderService",
            "sent_at": current_datetime,
            "type": "created_order",
            "payload": {
                "order": {
                    "order_id": order_data["id"],
                    "customer_fullname": order_data["customer_fullname"],
                    "product_name": order_data["product_name"],
                    "total_amount": order_data["total_amount"],
                    "created_at": order_data["created_at"].isoformat(),
                }
            }
        }
        
        # Convert the message dictionary to a JSON string
        return json.dumps(message)
