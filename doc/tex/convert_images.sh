#!/bin/sh
#

# Convert images to eps for TeX:

for f in `find ./images -name "*.png"`; do
	convert ${f} ${f}.eps
done

