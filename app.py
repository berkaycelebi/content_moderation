import os
from PIL import Image
import image_functions as imf
import time
import json
import cv2
import pika


custom_config = r"--oem 3 --psm 6"

IMAGE_MODERATION_CHANNEL = os.getenv("IMAGE_MODERATION_CHANNEL")
IMAGE_MODERATION_CHANNEL_RESULT = os.getenv("IMAGE_MODERATION_CHANNEL_RESULT")

DATA_DIRECTORY = os.getenv("DATA_DIRECTORY")
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
RABBITMQ_PORT = os.getenv("RABBITMQ_PORT")
RABBITMQ_USER = os.getenv("RABBITMQ_USER")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD")

print("DATA_DIRECTORY: " + DATA_DIRECTORY)
print("RABBITMQ_HOST: " + RABBITMQ_HOST)
print("RABBITMQ_PORT: " + RABBITMQ_PORT)
print("RABBITMQ_USER: " + RABBITMQ_USER)
print("RABBITMQ_PASSWORD: " + RABBITMQ_PASSWORD)
print("IMAGE_MODERATION_CHANNEL: " + IMAGE_MODERATION_CHANNEL)



# pytesseract.pytesseract.tesseract_cmd = (
#     r"/opt/homebrew/bin/tesseract"  # Set the tesseract path here
# )


connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST, RABBITMQ_PORT, '/', pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)))
channel = connection.channel()


def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)
    jsonValue = json.loads(body)
    newPath = jsonValue['imagePath']
    smallImagePath = jsonValue['smallImagePath']
    mediumImagePath = jsonValue['mediumImagePath']
    appCode = jsonValue['appCode']
    userId = jsonValue['userId']
    path = DATA_DIRECTORY + newPath
    small_image_path = DATA_DIRECTORY + smallImagePath
    medium_image_path = DATA_DIRECTORY + mediumImagePath
    print("Image Moderation Request Received for: " + path)
    if os.path.exists(path) == False:
        print("File not found")
        return
    else:
        start_time = time.time()
        print("File found")
        result, reason = imageControl(path)
        if result == False:
            print("Image Moderation Reason: " + str(reason))
        else:
            img = cv2.imread(path)
            scale_percent = 50  # percent of original size
            width = int(img.shape[1] * scale_percent / 100)
            height = int(img.shape[0] * scale_percent / 100)
            widthSmall = int(width * scale_percent / 100)
            heightSmall = int(height * scale_percent / 100)
            dim = (width, height)
            dimSmall = (widthSmall, heightSmall)
            image_resized_medium = cv2.resize(
                img, dim, interpolation=cv2.INTER_AREA)
            image_resized_small = cv2.resize(
                img, dimSmall, interpolation=cv2.INTER_AREA)
            print("Small Image Path: " + small_image_path)
            print("Medium Image Path: " + medium_image_path)
            cv2.imwrite(small_image_path, image_resized_small)
            cv2.imwrite(medium_image_path, image_resized_medium)
        total_time = time.time() - start_time
        print("Image Moderation Time: " + str(total_time) + " seconds")
        print("Image Moderation Result: " + str(result))
        resultJson = {
            "newImagePath": path,
            "result": result,
            "reason": reason,
            "time": total_time,
            "appCode": appCode,
            "userId": userId
        }

        channel.basic_publish(
            exchange='', routing_key=IMAGE_MODERATION_CHANNEL_RESULT, body=json.dumps(resultJson))


def redisSub():
    print("RabbitMQ Sub Listening for Image Moderation...")
    channel.queue_declare(queue=IMAGE_MODERATION_CHANNEL)
    channel.basic_consume(
        queue=IMAGE_MODERATION_CHANNEL, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()

    # for message in p.listen():
    #     messageType = message['type']
    #     if messageType == 'message':
    #         data = message['data']
    #         jsonValue = json.loads(data)
    #         newPath = jsonValue['imagePath']
    #         smallImagePath = jsonValue['smallImagePath']
    #         mediumImagePath = jsonValue['mediumImagePath']
    #         appCode = jsonValue['appCode']
    #         userId = jsonValue['userId']
    #         path = DATA_DIRECTORY + newPath
    #         small_image_path = DATA_DIRECTORY + smallImagePath
    #         medium_image_path = DATA_DIRECTORY + mediumImagePath
    #         print("Image Moderation Request Received for: " + path)

    #         if os.path.exists(path) == False:
    #             print("File not found")
    #             continue
    #         else:
    #             start_time = time.time()
    #             print("File found")
    #             result, reason = imageControl(path)

    #             if result == False:
    #                 print("Image Moderation Reason: " + str(reason))
    #             else:
    #                 img = cv2.imread(path)
    #                 scale_percent = 50  # percent of original size
    #                 width = int(img.shape[1] * scale_percent / 100)
    #                 height = int(img.shape[0] * scale_percent / 100)
    #                 widthSmall = int(width * scale_percent / 100)
    #                 heightSmall = int(height * scale_percent / 100)
    #                 dim = (width, height)
    #                 dimSmall = (widthSmall, heightSmall)
    #                 image_resized_medium = cv2.resize(
    #                     img, dim, interpolation=cv2.INTER_AREA)
    #                 image_resized_small = cv2.resize(
    #                     img, dimSmall, interpolation=cv2.INTER_AREA)

    #                 print("Small Image Path: " + small_image_path)
    #                 print("Medium Image Path: " + medium_image_path)

    #                 cv2.imwrite(small_image_path, image_resized_small)
    #                 cv2.imwrite(medium_image_path, image_resized_medium)
    #             total_time = time.time() - start_time
    #             print("Image Moderation Time: " + str(total_time) + " seconds")
    #             print("Image Moderation Result: " + str(result))
    #             resultJson = {

    #                 "newImagePath": path,
    #                 "result": result,
    #                 "reason": reason,
    #                 "time": total_time,
    #                 "appCode": appCode,
    #                 "userId": userId

    #             }
    #             r.publish(REDIS_IMAGE_MODERATION_CHANNEL_RESULT,
    #                       json.dumps(resultJson))


def imageControl(path):
    img_org = Image.open(path)
    if imf.isviolence(img_org):
        return False, "Violence"
    if imf.isnudityImage(path):
        return False, "Nudity"

    return True, "OK"


if __name__ == "__main__":
    # app.run(debug=True, port=8049)
    redisSub()