import uuid

from flask import Flask, render_template, request

from services.awg_converter.converter import decode_config
from services.awg_converter.exceptions import DecodeError
from config import sentry_sdk



app = Flask(__name__)
app.secret_key = uuid.uuid4().hex


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/', methods=['POST'])
def convert():
    link = request.form.get('link')
    if not link:
        return render_template('index.html', output="No link provided")

    try:
        awg_config = decode_config(link)
    except DecodeError as ex:
        sentry_sdk.capture_exception(ex)
        return render_template(
            'index.html',
            output="The link could not be decrypted. Please check the correctness of the link."
        )

    return render_template('index.html', output=awg_config.get_raw_config())
