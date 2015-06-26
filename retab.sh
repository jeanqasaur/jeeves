#!/bin/sh
for i in *.html
do
    sed 's/\t\t/\t/g' "${i}" > filename.notabs && mv filename.notabs "${i}"
done
