how to get site ssl certs:

* open browser (im using brave browser (should be same as chrome))
* visit website of interest (for example google.com)
* in url address bar click on `lock` icon
* in drop down menu, click on `Connection is secure`
* in menu, click on `Certificate is valid`
* in Certificate Viewer menu, click on `Details` tab
* on bottom of Details tab menu, click on `Export...` and save
* take the cert file and move into folder with `sim7080g_load_certs.py`
* edit `sim7080g_load_certs.py` to reflect cert file name
* connect sim7080g module to computer via usb
* run `sim7080g_load_certs.py` with sim7080g connected
