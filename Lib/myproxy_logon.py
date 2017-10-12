#
# myproxy client
#
# Tom Uram <turam@mcs.anl.gov>
# 2005/08/04
#


import socket
from OpenSSL import crypto, SSL


class GetException(Exception):
    pass


class RetrieveProxyException(Exception):
    pass


debug = 0


def debuglevel(level):
    global debug
    return debug >= level


def create_cert_req(keyType=crypto.TYPE_RSA,
                    bits=1024,
                    messageDigest="md5"):
    """
    Create certificate request.

    Returns: certificate request PEM text, private key PEM text
    """

    # Create certificate request
    req = crypto.X509Req()

    # Generate private key
    pkey = crypto.PKey()
    pkey.generate_key(keyType, bits)

    req.set_pubkey(pkey)
    req.sign(pkey, messageDigest)

    return (crypto.dump_certificate_request(crypto.FILETYPE_ASN1, req),
            crypto.dump_privatekey(crypto.FILETYPE_PEM, pkey))


def deserialize_response(msg):
    """
    Deserialize a MyProxy server response

    Returns: integer response, errortext (if any)
    """

    lines = msg.split('\n')

    # get response value
    responselines = [x for x in lines if x.startswith('RESPONSE')]
    responseline = responselines[0]
    response = int(responseline.split('=')[1])

    # get error text
    errortext = ""
    errorlines = [x for x in lines if x.startswith('ERROR')]
    for e in errorlines:
        etext = e.split('=')[1]
        errortext += etext

    return response, errortext


def deserialize_certs(inp_dat):

    pem_certs = []

    dat = inp_dat

    while dat:

        # find start of cert, get length
        ind = dat.find('\x30\x82')
        if ind < 0:
            break

        len = 256 * ord(dat[ind + 2]) + ord(dat[ind + 3])

        # extract der-format cert, and convert to pem
        c = dat[ind:ind + len + 4]
        x509 = crypto.load_certificate(crypto.FILETYPE_ASN1, c)
        pem_cert = crypto.dump_certificate(crypto.FILETYPE_PEM, x509)
        pem_certs.append(pem_cert)

        # trim cert from data
        dat = dat[ind + len + 4:]

    return pem_certs


CMD_GET = """VERSION=MYPROXYv2
COMMAND=0
USERNAME=%s
PASSPHRASE=%s
LIFETIME=%d\0"""


def myproxy_logon_py(hostname, username, passphrase,
                     outfile, lifetime=43200, port=7512):
    """
    Function to retrieve a proxy credential from a MyProxy server

    Exceptions:  GetException, RetrieveProxyException
    """

    context = SSL.Context(SSL.SSLv3_METHOD)

    # disable for compatibility with myproxy server (er, globus)
    # globus doesn't handle this case, apparently, and instead
    # chokes in proxy delegation code
    context.set_options(0x00000800)

    # connect to myproxy server
    if debuglevel(1):
        print("debug: connect to myproxy server")
    conn = SSL.Connection(context, socket.socket())
    conn.connect((hostname, port))

    # send globus compatibility stuff
    if debuglevel(1):
        print("debug: send globus compat byte")
    conn.write('0')

    # send get command
    if debuglevel(1):
        print("debug: send get command")
    cmd_get = CMD_GET % (username, passphrase, lifetime)
    conn.write(cmd_get)

    # process server response
    if debuglevel(1):
        print("debug: get server response")
    dat = conn.recv(8192)
    if debuglevel(1):
        print(dat)
    response, errortext = deserialize_response(dat)
    if response:
        raise GetException(errortext)
    else:
        if debuglevel(1):
            print("debug: server response ok")

    # generate and send certificate request
    # - The client will generate a public/private key pair and send a
    #   NULL-terminated PKCS#10 certificate request to the server.
    if debuglevel(1):
        print("debug: send cert request")
    certreq, privatekey = create_cert_req()
    conn.send(certreq)

    # process certificates
    # - 1 byte , number of certs
    dat = conn.recv(1)
    numcerts = ord(dat[0])

    # - n certs
    if debuglevel(1):
        print("debug: receive certs")
    dat = conn.recv(8192)
    if debuglevel(2):
        print("debug: dumping cert data to myproxy.dump")
        f = open('myproxy.dump', 'w')
        f.write(dat)
        f.close()

    # process server response
    if debuglevel(1):
        print("debug: get server response")
    resp = conn.recv(8192)
    response, errortext = deserialize_response(resp)
    if response:
        raise RetrieveProxyException(errortext)
    else:
        if debuglevel(1):
            print("debug: server response ok")

    # deserialize certs from received cert data
    pem_certs = deserialize_certs(dat)
    if len(pem_certs) != numcerts:
        print(
            "Warning: %d certs expected, %d received" %
            (numcerts, len(pem_certs)))

    # write certs and private key to file
    # - proxy cert
    # - private key
    # - rest of cert chain
    if debuglevel(1):
        print("debug: write proxy and certs to", outfile)
    if isinstance(outfile, str):
        f = open(outfile, 'w')
    else:
        f = outfile
    f.write(pem_certs[0])
    f.write(privatekey)
    for c in pem_certs[1:]:
        f.write(c)
    if isinstance(outfile, str):
        f.close()


myproxy_logon = myproxy_logon_py
