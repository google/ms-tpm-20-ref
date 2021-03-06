#!/usr/bin/env python
#
# Copyright (c) 2015, Linaro Limited
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#

def get_args():
	from argparse import ArgumentParser

	parser = ArgumentParser()
	parser.add_argument('--in', required=True, dest='inf', \
			help='Name of input file (unsigned TA)')
	return parser.parse_args() 

def assert_file_exists(fname):
	import os.path
	
	if(os.path.isfile(fname)):
		return True
	else:
		raise FileNotFoundError('File ' + fname + ' was not found')
    
def main():
	from Crypto.Signature import PKCS1_v1_5
	from Crypto.Hash import SHA256
	from Crypto.PublicKey import RSA
	import struct, base64, os.path, sys
	
	args = get_args()

	assert_file_exists(args.inf)
	
	# Read input file (unsigned TA)
	f = open(args.inf, 'rb')
	img = f.read()
	f.close()

	h = SHA256.new()

	digest_len = h.digest_size
	#We plan to use RSA 2048 bit keys so signature is 256 bytes
	sig_len = 256 #len(signer.sign(h))
	img_size = len(img)

	magic = 0x4f545348	# SHDR_MAGIC
	img_type = 0		# SHDR_TA
	algo = 0x70004830	# TEE_ALG_RSASSA_PKCS1_V1_5_SHA256
	shdr = struct.pack('<IIIIHH', magic, img_type, img_size, algo, digest_len, sig_len)

	h.update(shdr)
	h.update(img)
	dig = h.digest()
	
	print("Image size is:", img_size)
	print("Digest length is:", digest_len)
	print("Digest is:", base64.b64encode(dig))
	
	digest_filename = os.path.splitext(args.inf)[0].split(".")[0]+'.dig'
	
	print('Digest Filename:', digest_filename)
	
	# Write digest to file
	dig_out = open(digest_filename, 'wb+')
	dig_out.write(base64.b64encode(dig))
	dig_out.close()
	
if __name__ == "__main__":
	main()
