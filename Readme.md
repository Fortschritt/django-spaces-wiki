django-wiki dependencies:
* zieht pillow, und das braucht libjpeg-dev auf dem host, also vorher 
aptitude install libjpeg-dev
* gcc muss wohl fürs compilen mindestens 4.9 sein, sonst gibts diesen Fehler:
x86_64-linux-gnu-gcc: error: unrecognized command line option '-fstack-protector-strong'
* außer dem aptitude install python3-dev
dependency django-wiki von git installieren, bis 0.1 installert wurde
pip install -e git+https://github.com/django-wiki/django-wiki.git#egg=django_wiki
