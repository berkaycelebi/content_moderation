from flask import Flask, request, jsonify, abort, Response
import post_method_functions as pmf
import os
import redis
from flask import jsonify, Response
import speech_recognition as sr
import re
from PIL import Image
import text_functions as tf
import image_functions as imf
import numpy as np
import pytesseract
import time
import json
import cv2
import pika


app = Flask(__name__)

custom_config = r"--oem 3 --psm 6"

REDIS_IMAGE_MODERATION_CHANNEL = "image_moderation"
REDIS_IMAGE_MODERATION_CHANNEL_RESULT = "image_moderation_result"

DATA_DIRECTORY = "/Users/mac5/Projects/WorkoutAppsSocial/WorkoutAppsSocial.Api/wwwroot/"


connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()


"""
    data: {
        type: "audio" | "video" | "image" | "text",
        data: string (path file)
    }

    return: {
        true if is okey
        false if is not okey
        true | false
    }

"""


@app.route("/", methods=["POST"])
def main():
    if request.method == 'POST':
        data = request.get_json()
        t = data["type"]

        path = data['data']

        if os.path.exists(path) == False and t != "text":
            return abort(Response(status=400, response="File not found"))

        if t == "audio":
            return pmf.audioControl(path)
        elif t == "video":
            return pmf.videoControl(path)
        elif t == "image":
            return pmf.imageControl(path)
        elif t == "text":
            return pmf.textControl(path)
        else:
            return abort(Response(status=400, response="Invalid type"))

    else:
        return abort(Response(status=400, response="Invalid method"))


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
      
        channel.basic_publish(exchange='', routing_key=REDIS_IMAGE_MODERATION_CHANNEL_RESULT, body=json.dumps(resultJson))


def redisSub():
    print("RabbitMQ Sub Listening for Image Moderation...")
    channel.queue_declare(queue=REDIS_IMAGE_MODERATION_CHANNEL)
    channel.basic_consume(
        queue=REDIS_IMAGE_MODERATION_CHANNEL, on_message_callback=callback, auto_ack=True)
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

    img = img_org.resize((160, 160))
    img = np.array(img)
    extractedInformation = pytesseract.image_to_string(img_org)
    extractedInformation = re.sub(r"\n", " ", extractedInformation)
    extractedInformation = re.sub(r"\f", "", extractedInformation)
    if tf.ishate(extractedInformation):
        return False, "Hate"
    if tf.isspam(extractedInformation):
        return False, "Spam"
    return True, "OK"


if __name__ == "__main__":
    # app.run(debug=True, port=8049)
    redisSub()
