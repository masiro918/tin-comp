#!/bin/sh

cd src
pyinstaller main.py
cp stdlib.s dist/main/stdlib.s
cd ..
cp license.txt src/dist/main/license.txt
mv src/dist/main/main src/dist/main/tincomp

mkdir src/dist/main/THIRD_PARTY_LICENSES
mv doc/licenses/cpython_license.txt src/dist/main/THIRD_PARTY_LICENSES/cpython_license.txt
mv doc/licenses/py_installer_license.txt src/dist/main/THIRD_PARTY_LICENSES/py_installer_license.txt
