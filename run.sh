#!/bin/bash
#python extracthistos_2.py test-extracted.root ttH0JetNoFxFx8TeVCTEQ6M.root
python extracthistos_2.py test-extracted.root ttH1JetNoFxFx8TeVCTEQ6M.root
for f in *.di ; do echo "$f"; twopi "$f" -Tpng -o "${f%.di}.png" ; done

#kate event54.di
#eog output.png