#!/usr/bin/env python3

"""
    Title:      GootGrabber
    Desc:       Extract IOC's from Gootloaders.
    Author:     Adithya Chandra
"""

import re
import getopt
import sys
import os
import warnings
import socket
from codecs import encode, decode
from pathlib import Path


txt1 = "\n \t GootGrabber  \n"
print('{0:{1}^100}'.format(txt1, "*"))


warnings.filterwarnings("ignore", category=DeprecationWarning)

functions_regex = r"\w+\[\d{7}\]=\w+;\s*\w+=.+$"
code_regex = r"(?<!\\)(?:\\\\)*'([^'\\]*(?:\\.[^'\\]*)*)'"
ext_code_regex = r"(\w+)\s*=\s*(?<!\\)(?:\\\\)*'([^'\\]*(?:\\.[^'\\]*)*)'"
code_order = r"\=\s*((?:\w+\+){NUM_REP}(?:\w+));"
breacket_regex = "\[(.*?)\]"
url_regex = "(?:https?:\/\/[^=]*)"
separator_regex = "([\'|\"].*?[\'|\"])"

all_args = sys.argv[1:]
    

def decode_cipher(cipher):
    plaintext = ""
    counter = 0
    while(counter < len(cipher)):
        decoded_char = cipher[counter]
        if counter % 2:
            plaintext = plaintext + decoded_char
        else:
            plaintext = decoded_char + plaintext
        counter += 1
    return plaintext

def Main():
    argv = sys.argv
    if(os.path.isfile(argv[1])): #check for file
        jsFile = ""
        f = open(argv[1],"r")
    else:
        print("File not found - Exiting")
        Help()
        return
    for l in f: #read each line into a string
        jsFile += l

    all_domains = set()
    all_urls = set()

    
    if len(jsFile) > 100000: # new version. file contains library code to obfuscate
                    print("\nThis file is from new gootkit version!!\n")
                    clean_jsFile = ""
                    matches = re.findall(functions_regex, jsFile, re.MULTILINE)
                    for m in matches:
                        clean_jsFile += m + "\n"

                    matches = re.findall(ext_code_regex, clean_jsFile, re.MULTILINE)
                    code_parts = dict()
                    for m in matches:
                        code_parts[m[0]] = m[1]
                    
                    matches = re.findall(code_order.replace("NUM_REP", str(len(code_parts)-1)), clean_jsFile, re.MULTILINE)
                    order = list()
                    for m in matches:
                        order = m.split("+")
                        
                    ordered_code = ""
                    for element in order:
                        ordered_code += code_parts[element]
                    jsFile = "'" + ordered_code + "'"
                    
    round = 0
    while round < 2:
                    matches = re.findall(code_regex, jsFile, re.MULTILINE)
                    longest_match = ""
                    for m in matches:
                        if len(longest_match) < len(m):
                            longest_match = m
                    
                    jsFile = decode_cipher(decode(encode(longest_match, 'latin-1', 'backslashreplace'), 'unicode-escape')) #
                    round += 1



    domains = re.findall(breacket_regex, jsFile.split(";")[0], re.MULTILINE)
    urls = re.findall(url_regex, jsFile, re.MULTILINE)
    if len(urls) > 0:
                    replaceables = re.findall(separator_regex, urls[0], re.MULTILINE)
                    if len(replaceables) == 2:
                        for d in domains:
                            for dom in d.replace("\"", "").replace("'", "").split(","):
                                all_domains.add(dom)
                                all_urls.add(urls[0].replace(replaceables[0], dom).replace(replaceables[1], "") + "=")
                                
                    print("\nFile recieved : - " + str(f))
    else:
                    print("Error in reading the file! \n Either the file is corrupted or the tactic is changed! \n - " + str(f))
                    
    
    print("\nFound URLs: (" + str(len(all_urls)) + ")")
    for url in all_urls:
        print(url.replace(".","[.]"))
    
    print("\nIP Address Details:")
    for domain in all_domains:
      print("IP address of domain:",domain)
      print(socket.gethostbyname(domain))

def Help():
    print("Usage: gootGrabber.py \"path to file.js\"")

if(len(sys.argv) < 2):
    Help()
else:
    Main()




