#!/bin/sh
python extracthistos_2.py test-extracted.root ttH0JetNoFxFx8TeVCTEQ6M.root
#kate event54.di
dot event54.di -Tpng -o -O
eog event54.di.png