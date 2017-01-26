import netifaces
import zmq
import random
import os
import tempfile
import zipfile
import binascii

def get_my_ip():
    eth_interfaces = sorted([ifname for ifname in netifaces.interfaces() if ifname.startswith('eth')])
    if len(eth_interfaces) < 1:
        ifname = 'lo'
    else:
        ifname = eth_interfaces[-1]
    for x in netifaces.ifaddresses(ifname)[netifaces.AF_INET]:
        # Return first addr found
        return x['addr']

def bind_to_random_port(socket, addr, min_port=49152, max_port=65536, max_tries=100):
    "We can't just use the zmq.Socket.bind_to_random_port, as we wan't to set the identity before binding"
    for i in range(max_tries):
        try:
            port = random.randrange(min_port, max_port)
            socket.identity = '%s:%s' % (addr, port)
            socket.bind('tcp://*:%s' % port)
            #socket.bind('%s:%s' % (addr, port))
        except zmq.ZMQError as exception:
            en = exception.errno
            if en == zmq.EADDRINUSE:
                continue
            else:
                raise
        else:
            return socket.identity
    raise zmq.ZMQBindError("Could not bind socket to random port.")

def zip_to_file(file_path, destination):
    fd, zip_filename = tempfile.mkstemp(suffix=".zip", dir=destination)
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED, allowZip64=True) as myzip:
        if os.path.isdir(file_path):
            abs_src = os.path.abspath(file_path)
            for root, dirs, files in os.walk(file_path):
                for current_file in files:
                    absname = os.path.abspath(os.path.join(root, current_file))
                    arcname = absname[len(abs_src) + 1:]
                    myzip.write(absname, arcname)
        else:
            myzip.write(file_path, file_path)
        zip_info = ''.join(str(zipinfoi.CRC) for zipinfoi in  myzip.infolist())
        checksum = hex(binascii.crc32(zip_info) & 0xffffffff)

    return zip_filename, checksum