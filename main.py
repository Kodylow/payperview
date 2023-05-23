from flask import Flask, Response, request
from pyln.client import LightningRpc

app = Flask(__name__)

import functools
from hashlib import sha256

invoice_hashes = []

def verify_preimage(preimage):
    preimage_hash = sha256(preimage.encode('utf-8')).hexdigest()
    found = False
    for hash in invoice_hashes:
            if hash == preimage_hash:
                    found = True
    # pay-per-view means you pay every time.
    if found:
            invoice_hashes.remove(preimage_hash)
            
    return found

import random, string

def randomword(length):
   letters = string.ascii_lowercase
   return ''.join(random.choice(letters) for i in range(length))

def verify_auth(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if "Authorization" not in request.headers:
                # go get invoice!
                pass
        else:
                parts = request.headers["Authorization"].split()
                if len(parts) == 2 and parts[0] == "L402":
                        rune, preimage = parts[1].split(':', maxsplit=1)
                        if verify_preimage(preimage):
                                return func(*args, **kwargs) 

        rando_label = randomword(15)
        invoice = lnrpc.invoice(amount_msat="5555", label="{}".format(rando_label), description="Payment for {endpoint}")
        bolt11 = invoice['bolt11'] 
        invoice_hashes.append(invoice['payment_hash'])
                        
        resp = Response("Needs payment", status=402)
        resp.headers["WWW-Authenticate"] = 'L402 token="", invoice="{}"'.format(bolt11)
        return resp
    return wrapper
        

@app.route('/')
@verify_auth
def index():
    return 'This cost you 5555 sats\n'

lnrpc = LightningRpc('/home/runner/.lightning/regtest/lightning-rpc')
app.run(host='0.0.0.0', port=81)