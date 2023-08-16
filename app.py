from flask import Flask, request, jsonify, abort, Response
import post_method_functions as pmf
import os

app = Flask(__name__)

custom_config = r"--oem 3 --psm 6"


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


if __name__ == "__main__":
    app.run(debug=True, port=8049)
