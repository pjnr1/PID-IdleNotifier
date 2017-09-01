import smtplib
import psutil
import sched
import time
import argparse

# Mail sender information
from mail_config import MAIL_FROM_ADDR
from mail_config import MAIL_FROM_PWD

# Mail receiver
from mail_config import MAIL_JLLAB_ADDR

# PID to check on
PID_TO_CHECK = 13183

# Check interval (in seconds)
CHECK_INTERVAL = 300


def SendIdleNotification(mail_to,p_name):
    msg = '\r\n'.join({
        ''.join(['From: ',
                 MAIL_FROM_ADDR
                 ]),
        ''.join(['To: ',
                 mail_to
                 ]),
        ''.join(['Subject: ',
                  p_name,
                  ' is idle'
                  ]),
        '',
        ''.join(['Hello, ',
                  p_name,
                  ' seems to be idle.'
                  ]),
        'Do what you want with that information.'
    })
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo()
    server.starttls()
    server.login(MAIL_FROM_ADDR,MAIL_FROM_PWD)
    server.sendmail(MAIL_FROM_ADDR,mail_to.split(),msg)
    server.quit()

def CheckStatus(pid):
    try:
        p = psutil.Process(pid)
    except psutil.NoSuchProcess:
        print("No such process (pid: {pid})".format(pid=pid))
        return -1

    cpu_usage = p.cpu_percent(interval=1)

    if cpu_usage < 10:
        return True
    else:
        return False

def GetNameFromPID(pid):
    try:
        p = psutil.Process(pid)
    except psutil.NoSuchProcess:
        print("No such process (pid: {pid})".format(pid=pid))
        return -1
    return p.name()

def ProcessCheckerWithMail(sc):
    pid = PID_TO_CHECK
    status = 'status not initialized'
    ready = CheckStatus(pid)
    name = GetNameFromPID(pid)
    current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())

    if ready == True:
        status = 'ready'
        SendIdleNotification(MAIL_JLLAB_ADDR,name)
    elif ready == False:
        status = 'not ready'
        s.enter(CHECK_INTERVAL, 1, ProcessCheckerWithMail, (sc,))
    else:
        status = 'error'

    print('{time}\t{pid}: {name}\tStatus:-> {status}'.format(time=current_time,
                                                             pid=pid,
                                                             name=name,
                                                             status=status))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--pid')
    parser.add_argument('--mailto')
    parser.add_argument('--interval')

    args = parser.parse_args()

    s = sched.scheduler(time.time, time.sleep)
    s.enter(0, 1, ProcessCheckerWithMail, (s,))
    s.run()