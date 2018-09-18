#!/bin/sh
openssl genrsa -out http_testserver.key 4096
openssl req -new -key http_testserver.key -out http_testserver.csr -batch \
  -subj '/C=NL/L=Groningen/O=Example Inc./CN=127.0.0.1/emailAddress=example@localhost' -batch
openssl x509 -in http_testserver.csr -out http_testserver.crt -req \
  -signkey http_testserver.key -days 3650
