from flask import Flask, request, jsonify
from pyngrok import ngrok

app = Flask(__name__)

# Example GET method


@app.route('/get_example', methods=['GET'])
def get_example():
    return jsonify(message="This is a GET response!")

# Example POST method


@app.route('/post_example', methods=['POST'])
def post_example():
    data = request.json
    return jsonify(message="This is a POST response!", your_data=data)


if __name__ == '__main__':
    # Setup ngrok
    ngrok_tunnel = ngrok.connect(
        addr=5000, hostname="hugely-dashing-lemming.ngrok-free.app")
    print('NGROK Tunnel URL:', ngrok_tunnel.public_url)

    # Run Flask app
    app.run(port=5000)

    # Run Flask app
    app.run(port=5000)