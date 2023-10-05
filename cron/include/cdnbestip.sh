cdnbestip() {
        export CLOUDFLARE_TOKEN=''
        export BARK_TOKEN=''
        export GCORE_DOMAIN='gcore.xxx.xyz'
        export CLOUDFLARE_DOMAIN='cloudflare.xxx.xyz'
        
	PROJPATH='/root/proj/cdnbestip'

        pushd "$PROJPATH" > /dev/null 2>&1
                source /root/pyvenv/bin/activate
                python run.py 
                deactivate
        popd > /dev/null 2>&1
}

