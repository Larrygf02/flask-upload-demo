from flask import Flask, request, jsonify, make_response
import boto3
import os
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
CORS(app)  # Permitir acceso desde tu frontend (importante)

# Configuración de AWS S3
s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name="us-east-1"  # cambia si usas otra región
)

BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return make_response(jsonify({"error": "No se envió archivo"}), 400)

    file = request.files['file']
    filename = secure_filename(file.filename)

    try:
        # Subir a S3 de forma privada
        s3.upload_fileobj(
            file,
            BUCKET_NAME,
            filename,
            ExtraArgs={
                "ACL": "private",
                "ContentType": file.content_type
            }
        )

        # Crear URL temporal (presigned)
        presigned_url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': BUCKET_NAME, 'Key': filename},
            ExpiresIn=3600  # válido por 1 hora
        )

        return jsonify({
            "message": "Imagen subida con éxito",
            "url": presigned_url
        })

    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
