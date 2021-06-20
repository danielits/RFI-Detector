#!/bin/bash
calibrate_adc5g.py \
    --ip         192.168.1.12 \
    --bof        spectrometerv2.bof.gz \
    --upload \
    `#--genname    TCPIP::192.168.1.34::INSTR` \
    --genfreq    10 \
    --genpow     -4 \
    --zdok0snaps adcsnap0 adcsnap1\
    `#--zdok1snaps adcsnap2 adcsnap3` \
    --do_mmcm \
    --do_ogp \
    --do_inl \
    `#--load_ogp` \
    `#--load_inl` \
    --plot_snap \
    --plot_spec \
    --nsamples   200 \
    --bandwidth  600 \
    `#--loaddir    adc5gcal\ 2020-01-09\ 15:31:42` \
    --caldir adc5gcal/