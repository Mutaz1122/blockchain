import sys
from flask import Flask, request, jsonify
from phe import paillier

app = Flask(__name__)

# Generate Paillier key pair
public_key, private_key = paillier.generate_paillier_keypair(n_length=2048)


# Generate the corresponding private key
private_key = paillier.PaillierPrivateKey(public_key2, p=fixed_p, q=fixed_q)

@app.route('/encrypt/<int:x>', methods=['GET'])
def encrypt(x):
    encrypted_x = public_key.encrypt(x)
    return jsonify({'encrypted_x': encrypted_x.ciphertext()})

@app.route('/decrypt/<int:ciphertext>', methods=['GET'])
def decrypt(ciphertext):
    encrypted_x = paillier.EncryptedNumber(public_key, ciphertext)
    decrypted_x = private_key.decrypt(encrypted_x)
    return jsonify({'decrypted_x': decrypted_x})

@app.route('/add', methods=['POST'])
def add():
    values = request.get_json()
    encrypted_x = paillier.EncryptedNumber(public_key, int(values["x"]))
    encrypted_y = paillier.EncryptedNumber(public_key, int(values["y"]))
    encrypted_sum = encrypted_x + encrypted_y
    decrypted_sum = private_key.decrypt(encrypted_sum)
    return jsonify({'result': decrypted_sum})
@app.route('/get_key_params', methods=['GET'])
def get_key_params():
    key_params = {
        'n': public_key.n,
        'p': public_key.p,
        'q': public_key.q
    }
    return jsonify(key_params)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(sys.argv[1]))


