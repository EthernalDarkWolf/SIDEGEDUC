import urllib.request,os,hashlib;
h='f156a91e512dfcf93efb29d1cfb3b1c79a3f54e38a1b9a4ad2c6c0a4f3d8f7d1';
pf=os.path.join(os.path.expanduser('~'),'AppData/Roaming/Sublime Text/Installed Packages');
os.makedirs(pf,exist_ok=True);
urllib.request.install_opener(urllib.request.build_opener(urllib.request.ProxyHandler()));
by=urllib.request.urlopen('https://packagecontrol.io/Package%20Control.sublime-package').read();
if hashlib.sha256(by).hexdigest()==h:
    open(os.path.join(pf,'Package Control.sublime-package'),'wb').write(by)
