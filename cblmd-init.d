#!/bin/bash
#
# CBLM
#
# chkconfig: 35 86 15
# description: Start CBLM service
#
### BEGIN INIT INFO
# Provides: CBLM
# Required-Start:
# Required-Stop:
# Default-Start: 2 3 4 5
# Default-Stop:
# Description:  CBLM
### END INIT INFO

# Source function library.
. /etc/init.d/functions

if [ ! -f /etc/sysconfig/cblm ]; then
    exit 6
fi

. /etc/sysconfig/cblm

USER=root
CBLM=/usr/bin/cblmd     # 2.9.4
#CBLM=/sbin/cblmd       # 2.9.5
CBLMDPID=`/bin/ps x --no-headers | /bin/awk --assign=pattern="${CBLM}" ' $0 ~ pattern && $0 !~ "awk" { print $1 }'`
SOURCE=`/sbin/ip -4 -o a | /bin/awk --assign=pattern="${IFACE}" ' $0 ~ pattern { gsub(/\/.*/, "", $4); print $4 }'`
STAT=/var/run/cblmd.stat

start() {
    echo -n "Starting CBLM service"
    if [ "${CBLMDPID}" != "" ]; then
        echo -n $": cannot start cblmd: cblmd is already running.";
        failure $": cannot start cblmd: cblmd already running.";
        echo
        return 0
    fi
    if [ -f ${CBLM} ]; then
        su - ${USER} -c "${CBLM} --source=${SOURCE} --interface=${IFACE} --rate=30 --precedence=0 --precedence=1 --precedence=2 --precedence=5 --dbhost=${DBHOST} --dbname=${DBNAME} --dbuser=${DBUSER} --dbpass=${DBPASS} --stats=${STAT}"
    fi
    RETVAL=$?
    echo
    [ $RETVAL -eq 0 ] && touch /var/lock/subsys/cblmd;
    return $RETVAL
}

stop() {
    echo -n "Stopping CBLM service"
    if [ "${CBLMDPID}" == "" ]; then
        echo -n $": cannot stop cblmd: cblmd is not running."
        failure $": cannot stop cblmd: cblmd is not running."
        echo
        return 1;
    fi
    kill -9 ${CBLMDPID}
    RETVAL=$?
    echo
    [ $RETVAL -eq 0 ] && rm -f /var/lock/subsys/cblmd;
    return $RETVAL
}

rhstatus() {
        status -p /var/run/cblmd.pid cblmd
}

is_root_user()
{
    if [ 0 != `id -u` ]; then
        echo "You need to be root in order to run this script. Will not proceed."
        exit 2
    fi
}

case "$1" in
    start)
        is_root_user
        start
        ;;
    stop)
        is_root_user
        stop
        ;;
    status)
        rhstatus
        ;;
    restart)
        is_root_user
        stop
        start
        ;;
    *)
        echo $"Usage: cblmd {start|stop|status|restart}"
esac
