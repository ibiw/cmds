from telnetlib import Telnet
from time import sleep
from config import *
import config
import re
import datetime
import logging
import sys
import argparse


#reload(sys)
#sys.setdefaultencoding("utf8")    ## this is for Python 2.7, and it is not recommand after Python 3


## define all the global variables here


class MyLogger():

    def __init__(self, log_file_path, log_file_name, device):

        self.log_file_path = log_file_path
        self.log_file_name = log_file_name         ## should include device, config_file, date, and time
        self.device = device
        t = datetime.datetime.now().strftime("%d_%B_%Y_%H_%M_%S") ## 12_March_2016_20:57:37

        # logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
        logFormatter = logging.Formatter("%(asctime)s  %(message)s")
        self.rootLogger = logging.getLogger()
        self.rootLogger.setLevel(logging.DEBUG)
        # fileHandler = logging.FileHandler("{0}/{1}.log".format(logPath, fileName))
        #fileHandler = logging.FileHandler("{0}/{1}.log".format("/Users/ryan/Dropbox/cnyahoo/Python/", "test"))
        #fileHandler = logging.FileHandler("{0}/{1}.log".format("E:\qa\\test\\", device + "_" + cmd_file + "_" + cmd + "_ "  + "_test01"))
        try:
            fileHandler = logging.FileHandler("{0}/{1}.log".format(log_file_path, log_file_name + "_" + self.device + "_"  + t))
        except:
            print("Please check log file path and name")
        fileHandler.setFormatter(logFormatter)
        self.rootLogger.addHandler(fileHandler)

        consoleHandler = logging.StreamHandler()
        consoleHandler.setFormatter(logFormatter)
        self.rootLogger.addHandler(consoleHandler)

    def log(self, msg):
        self.rootLogger.info(msg)

class MyTelnet():
    
    def __init__(self, host, port, username, password, timeout, device, cmd_file, cmd, log_file_path, log_file_name, exit, reboot):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.username = username            
        self.password = password
        self.cmd_file = cmd_file
        self.cmd = cmd
        self.device = device
        self.log_file_path = log_file_path
        self.log_file_name = log_file_name         ## should include device, config_file, date, and time
        #self.device_file = device_file
        self.tmp_msg = b''
        self.loop = 1
        self.wait = 0.5
        self.tn = Telnet(self.host, self.port, self.timeout)
        sleep(2)
        #self.send("")
        self.tn.write("\r\n".encode('utf8'))
        self.dt = datetime.datetime.now().strftime("%d_%B_%Y_%H:%M:%S\t\t") ## 12_March_2016_20:57:37
        self.exit = exit
        self.reboot = reboot
        #self.receive_utf8
        #self.tn.set_debuglevel(8)

        self.prompt_1 = ["# ", "login: ", "Password: ", "Do you want to continue?"]           ## Do you want to continue? (y/n)y  --> \(y\/n\)
        self.prompt_re = ["# $", "login: $", "Password: $", "\(y\/n\)$"]           ## Do you want to continue? (y/n)y  --> \(y\/n\)
        self.prompt = [b"\r\n", b"# ", b"login: ", b"Password: ", b"Do you want to continue?", b"xxxyyyzzz "]
        #print(self.prompt)
        print("MyTelnet port is: ", port)
        self.mylogger = MyLogger(self.log_file_path, self.log_file_name, self.device)

    def receive_line(self):
        while True:
            n, match, msg = self.tn.expect(self.prompt, 15)   ## expect list self.prompt
            if n == 0:                                          ## just recive new line
                if self.tmp_msg != b'':
                    msg = (self.tmp_msg + msg)
                    self.tmp_msg = b''  
                    # print("0 if 1")
                if (msg != b'\r\n' and msg != b'\r\r\n'):              
                    #print("this is msg: ", msg)
                    msg = msg.decode('utf8', 'ignore')
                    self.mylogger.log(re.sub(r'\x1b[^m]*m', '', msg.strip()))       ## logging it line by line, and remove ANSI sequence with re.sub(r'\x1b[^m]*m', '', line), and remove newline when logging
                    # print("0 if 2")
                
            elif n == 1:                                               ## if receive "# ", that means last command is finished
                self.tmp_msg = msg                                     
                if (re.search(self.prompt_re[0], msg.decode('utf-8'))) and (not self.reboot):  ## doubhe check if " #" is at the end of the line
                    
                    #self.exit = True
                    # print("1 if ")
                    # print(self.reboot)
                    # print("break")
                    break
                elif self.reboot:
                    self.tmp_msg = msg
                    self.reboot = False
                    # print("reboot is true")
                else:
                    pass
            elif n == 2:                                        ## login
                sleep(0.5)
                self.tn.write((self.username + "\n").encode('utf-8'))
                self.tmp_msg = msg                
            elif n == 3 :                                       ## password
                sleep(0.5)
                self.tn.write((self.password + "\n").encode('utf-8'))
                self.tmp_msg = msg
            elif n == 4:                                        # yes or no
                #exit("test")
                self.tn.write("y".encode('utf-8'))
                self.tmp_msg = msg
                self.reboot = True
                # print("4 %s " % self.tmp_msg)
                sleep(5)
            elif n == 5:        ## exit when catch specific string
                self.exit = True
            else:
                pass
            sleep(0.01)


            #print(n, match, msg)
            """if n == 1:
                break"""

    def send(self, cmd):           ## do not call receive_utf8 again here
        if self.exit == True:
            exit("Exit as issue may happens")
        else:
            pass
        cmd_s = cmd.split("::")
        cmd = cmd_s[0] + "\r\n"
        #print(cmd)
        """if len(cmd_s) == 1:
            #self.tn.write(cmd.encode('utf8'))
            self.tn.write(cmd.encode('utf8'))
            #self.logger(cmd)
            sleep(self.wait)
            #sleep(0.5)    
        else:"""
        if len(cmd_s) == 3:
            self.loop = int(cmd_s[1])
            self.wait = int(cmd_s[2])
                #cmd = cmd_s[0] + "\r\n"
        for i in range(self.loop):
            #self.tn.write(cmd.encode('utf8'))
            self.tn.write(cmd.encode('utf-8'))
            #self.logger(cmd)
            sleep(self.wait)
                            ##  FMG3000F login: admin
                            ##  Password:
                            ##  FMG3000F #

                            ## Boot up, boot device capacity: 15272MB.
                            ## Press any key to display configuration menu...
                            ## ..................
                            ## output.splitlines()[:-1]
            self.loop = 1
            self.sleep = 0.5
            self.receive_line()

    def send_file(self, cmd_file):
        cmd_file_s = cmd_file.split("::")
        cmd_file = cmd_file_s[0]
        loop = 1
        i = 1
        wait = 0.1
        if len(cmd_file_s) == 3:
            loop = int(cmd_file_s[1])
            wait = int(cmd_file_s[2])

        while i <= loop:
            with open(cmd_file) as f:
                for line in f:
                    line = line.replace("\n", "")
                    self.send(line)
            print(i)
            i += 1
            sleep(wait)

def main():

    #s = None
    #data = []
    host = ""                         ## my default terminal server ip address            
    port = ""
    timeout = 15
    username = ""                          ## default username is "admin"
    password = ""                               ## default password is ""
    cmd = ""
    cmd_file = ""
    device = ""
    log_file_path = "E:\\qa\\test\\logs\\"
    log_file_name = ""
    exit = False
    reboot = False
    #device_file = ""


    parser = argparse.ArgumentParser(description = "Pleae use -d -f(-c) or -i -p -U -P -f(-c) combinations")
    parser.add_argument("-i", "--ip", dest = "host", default = "", help = "The host or IP Address to connect")
    parser.add_argument("-p", "--port", dest = "port", default = "", help = "The port to connect")
    parser.add_argument("-U", "--username", dest = "username", default = "admin", help = "username")
    parser.add_argument("-P", "--password", dest = "password", default = "", help = "password")
    parser.add_argument("-c", "--cmd", dest = 'cmd', default = "", help = "command")
    parser.add_argument("-f", "--cmdfile", dest = "cmd_file", default = "", help = "cmd file name")
    parser.add_argument("-d", "--device", dest = "device", default = "", help = "device name")
    parser.add_argument("-lp", "--logpath", dest = "log_path", default = "", help = "log path")
    parser.add_argument("-lf", "--logname", dest = "log_name", default = "", help = "log name")
    parser.add_argument("-t", "--timeout", dest = "timeout", default = 30, help = "timeout")
    #parser.add_argument("-D", "--devicefile", dest = "device_file", default = "", help = "device file")

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()
    print(args)
    #print(args.host)

## check_cmd run cmd or cmds in cmd_file
    def check_cmd():
        
        if args.cmd_file:
            cmd_file = args.cmd_file
            cmd = ""
            try:
                tn = MyTelnet(host, port, username, password, timeout, device, cmd_file, cmd, log_file_path, log_file_name, exit, reboot)
            except:
                exit(1)
            tn.receive_line()
            tn.send_file(cmd_file)
        
        elif args.cmd:
            cmd = args.cmd
            cmd_file = ""
            print("cmd: ", cmd)
            try:
                #tn = MyTelnet(host, port, username, password, timeout, device, cmd, cmd_file)
                tn = MyTelnet(host, port, username, password, timeout, device, cmd_file, cmd, log_file_path, log_file_name, exit, reboot)
            except:
               print("Telnet connection error!")
               exit(1)
            tn.receive_line()
            tn.send(cmd)

        else:
            print("Hi Man, please include '-f cmd_file' or '-c cmd'!")

## when input 'option' parameters
    if args.timeout:
        timeout = args.timeout
    
    if args.log_path:
        log_file_path = args.log_path

    if args.log_name:
        log_file_name = args.log_name

## when input -h host
    if args.host:
        host = args.host

        if args.port:
            port = args.port
        else:
            print("Hi there, please include '-p port'!")
            exit(1)

        if args.username:
            username = args.username
        else:
            print("Hi there, please include '-U username'!")
            exit(1)

        if args.password:
            password = args.password
        else:
            print("Hi there, please include '-P password'!")
            exit(1)

        check_cmd()

## when input -d device
    if args.device:

        device = args.device
        print(device)
        dev = globals()[args.device]   ## transfer the '-d device' to corresponding dictionary
        print(dev)
        host = dev['host']
        port = dev['port']
        username = dev['username']
        password = dev['password']
        timeout = dev['timeout']
        #print(config.(locals()['device']['username']))
        check_cmd()


main()

