* Link your domain name to ip of yor machine  
* Make a cert files on a server machine:  
When asked for "Common Name (e.g. server FQDN or YOUR name)" you need to reply this way:  
your_domain.name
```
openssl genrsa -out webhook_pkey.pem 2048
openssl req -new -x509 -days 3650 -key webhook_pkey.pem -out webhook_cert.pem
```
