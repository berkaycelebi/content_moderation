from flask import jsonify, Response
import speech_recognition as sr
import re
from PIL import Image
import text_functions as tf
import image_functions as imf
import numpy as np
import pytesseract
from urlextract import URLExtract
from PhishingWebsite import phishing_detection
# from pydub import AudioSegment
import subprocess


pytesseract.pytesseract.tesseract_cmd = (
    r"/opt/homebrew/bin/tesseract"  # Set the tesseract path here
)

extractor = URLExtract()


def audioControl(path) -> Response:
    output = path.split(".")[0] + ".wav"
    # conversion
    subprocess.call(['ffmpeg', '-i', path,
                     output])
    r = sr.Recognizer()  # Media storage path.
    with sr.AudioFile(output) as source:
        audio = r.record(source)
        extractedInformation = r.recognize_google(audio, show_all=False)
        if extractedInformation == "":
            return jsonify(True)
        if re.search("\*", extractedInformation):
            return jsonify(False)
        else:
            if tf.isspam(extractedInformation) or tf.ishate(extractedInformation):
                return jsonify(False)
            else:
                return jsonify(True)


def videoControl(path) -> Response:
    if imf.isnudityVideo(path):
        return jsonify(False)
    else:
        return jsonify(True)


def imageControl(path) -> Response:
    img_org = Image.open(path)
    if imf.isviolence(img_org):
        return jsonify(False)
    if imf.isnudityImage(path):
        return jsonify(False)

    img = img_org.resize((160, 160))
    img = np.array(img)
    extractedInformation = pytesseract.image_to_string(img_org)
    extractedInformation = re.sub(r"\n", " ", extractedInformation)
    extractedInformation = re.sub(r"\f", "", extractedInformation)
    if tf.ishate(extractedInformation):
        return jsonify(False)
    if tf.isspam(extractedInformation):
        return jsonify(False)
    return jsonify(True)


def textControl(text) -> Response:
    urls = extractor.find_urls(text)
    if urls:
        result_list = []
        for i in urls:
            result_list.append(phishing_detection.getResult(i))
        if "Phishing Website" in result_list:
            return jsonify(False)
    if tf.ishate(text):
        return jsonify(False)
    if tf.isspam(text):
        return jsonify(False)
    return jsonify(True)
