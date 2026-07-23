#!/bin/sh

cd src
pyinstaller main.py
cp stdlib.s dist/main/stdlib.s
cd ..
cp license.txt src/dist/main/license.txt
mv src/dist/main/main src/dist/main/tincomp
