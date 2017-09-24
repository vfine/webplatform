#!/bin/bash

export PANDAROOT=$HOME/panda
# panda-common, panda-server, and boto should be installed as indicated by PYTHONPATH.
# checkouts for panda components are
#   svn co svn+ssh://svn.cern.ch/reps/panda/panda-server/current/pandaserver panda-server
#   svn co svn+ssh://svn.cern.ch/reps/panda/panda-common/current/pandacommon panda-common
export PYTHONPATH=$PANDAROOT/pandamon:$PANDAROOT/panda-common:$PANDAROOT/panda-server:$HOME/products/boto-1.9b:$PYTHONPATH
case "`whoami`" in
    wenaus)
        export PANDAMON_HOST=localhost
        export PANDAMON_PORT=26882
        ;;
    *)
        export PANDAMON_HOST=`hostname`
        # Awkward! On EC2, hostname gives internal name. We need the external name.
        if test $PANDAMON_HOST = 'domU-12-31-39-0B-D5-E1' ; then PANDAMON_HOST='ec2-50-17-5-13.compute-1.amazonaws.com' ; fi
        export PANDAMON_PORT=26881
        ;;
esac

export SERVER=$PANDAROOT/pandamon/pmServer/pmMain.py
python $SERVER local
