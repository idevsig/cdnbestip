#!/usr/bin/env bash

cdnbestip() {
        export CLOUDFLARE_TOKEN=''
        export BARK_TOKEN=''
        export CHANIFY_TOKEN=''
        export GCORE_DOMAIN='gcore.xxx.xyz'
        export CLOUDFLARE_DOMAIN='cloudflare.xxx.xyz'

        PROJPATH='/root/proj/cdnbestip'

        pushd "$PROJPATH" >/dev/null 2>&1 || exit
        /root/pyvenv/bin/python run.py
        popd >/dev/null 2>&1 || exit
}
