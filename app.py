#!/usr/bin/python3
import sys, configparser, json
from flask import Flask, request, abort
from monero.wallet import Wallet
from monero.backends.jsonrpc import JSONRPCWallet
from monero.address import address
from functools import wraps
from waitress import serve

configparser = configparser.ConfigParser()
configparser.read('config.ini')
rpchost = configparser['RPC']['host']
rpcport = configparser['RPC']['port']

host = configparser['Server']['host']
port = configparser['Server']['port']
authorization = configparser['Server']['authorization']

app = Flask(__name__, instance_relative_config=False)
app.config.from_pyfile("config.py")

try:
    wallet = Wallet(JSONRPCWallet(host=rpchost, port=rpcport))
    print("[+] RPC Connection successful")
except Exception as e:
    print("[-] RPC Connection failed, aborting")
    sys.exit(str(e))


def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        authorization_header = request.headers.get('Authorization')
        if authorization_header and authorization_header == authorization:
            return f(*args, **kwargs)

        abort(401, 'Invalid token')

    return decorated


# --------- Errors ---------
@app.errorhandler(400)
def bad_request(r):
    return {'error': '%s' % r.description}, 400


@app.errorhandler(401)
def bad_request(r):
    return {'error': '%s' % r.description}, 401


@app.errorhandler(404)
def bad_request(r):
    return {'error': '%s' % r.description}, 404


@app.errorhandler(405)
def bad_request(r):
    return {'error': '%s' % r.description}, 405


@app.errorhandler(500)
def internal_server_error(r):
    return {'error': '%s' % r.description}, 500


# --------- Routes ---------
@app.route('/validate_address/<string:addr>', methods=['GET'])
@auth_required
def validate_address(addr):
    try:
        try:
            a = address(addr)
            return {'network': str(a.net), 'is_valid': True}
        except ValueError as v:
            return {'error': str(v), 'is_valid': False}
    except Exception as e:
        abort(500, str(e))


@app.route('/get_balance', methods=['GET'])
@auth_required
def get_balance():
    try:
        wallet.refresh()
        data = wallet.balance()
        return {'balance': "%.8f" % data}
    except Exception as e:
        abort(500, str(e))


@app.route('/get_payments/<string:subaddress>', methods=['GET'])
@auth_required
def get_payments(subaddress):
    try:
        incoming_payments = wallet.incoming(local_address=subaddress)

        p = list()
        for i in incoming_payments:
            temp = {
                'txid': i.transaction.hash,
                'amount': float(i.amount),
                'confirmations': wallet.confirmations(i)
            }
            p.append(temp)

        return {'payments': p}
    except Exception as e:
        abort(500, str(e))


@app.route('/create_subaddress', methods=['POST'])
@auth_required
def create_subaddress():
    try:
        a = wallet.new_address()
        return {'address': str(a[0])}
    except Exception as e:
        abort(500, str(e))


@app.route('/transfer', methods=['POST'])
@auth_required
def transfer():
    try:
        data = json.loads(request.data)
        to_address = str(data['to'])
        amount = float(data['amount'])
    except:
        return abort(400, 'Invalid data')

    try:
        txid = wallet.transfer(to_address, amount)
        print(str(txid[0]))
        return {'transaction_id': str(txid[0])}
    except Exception as e:
        abort(500, str(e))


if __name__ == '__main__':
    serve(app, host=host, port=port)

