import re
import sys
from pathlib import Path
from sys import stdin, stdout, stderr
from dataclasses import dataclass


###############################################################################
# Parser
###############################################################################
class Parser:
    hooks = {}
    colors = None
    actionClass = {}
    logfile = None

    @staticmethod
    def send_hooks():
        for hook in sorted(Parser.hooks):
            response_line = f'register|{hook}'
            Parser.send(Parser.colors.CONFIG_RESP, response_line)
        Parser.send(Parser.colors.CONFIG_RESP, 'register|ready')
        pass

    @staticmethod
    def send(opts, line):
        Parser.log(opts, line)
        print(line, file=stdout, flush=True)

    @staticmethod
    def log(opts, line):
        color_tag, do_log = opts
        color_end = Parser.colors.END if color_tag else ''
        if do_log:
            print(f'{color_tag}{line}{color_end}', file=stderr, flush=True)
        if Parser.logfile:
            with Path(Parser.logfile).open("a") as file:
                file.write(line+'\n')

    @staticmethod
    def parse_config(line):
        Parser.log(Parser.colors.CONFIG, line)
        config = StateMgr.get('config')
        if line != 'config|ready':
            cmd, key, value = line.split('|', 2)
            config[key] = f'{config[key]}|{value}' if key in value else value
        else:
            Parser.send_hooks()

    @staticmethod
    def parse_report(line):
        protocol, version, timestamp, subsystem, phase, sid, *payload = line.split('|')
        clazz, report_color = (Parser.actionClass['ReportSmtpOut'], Parser.colors.REPORT_OUT)\
            if subsystem == 'smtp-out' else (Parser.actionClass['ReportSmtpIn'], Parser.colors.REPORT_IN)
        Parser.log(report_color, line)
        ctx = Context(StateMgr.get(sid), timestamp, sid)
        func = getattr(clazz, phase.replace('-', '_'))
        func(ctx, *payload)

    @staticmethod
    def parse_filter(line):
        protocol, version, timestamp, subsystem, phase, sid, token, *payload = line.split('|')
        clazz, color1, color2 = (Parser.actionClass['FilterSmtpIn'], Parser.colors.FILTER_IN,
                                 Parser.colors.FILTER_IN_RESP)
        Parser.log(color1, line)
        ctx = Context(StateMgr.get(sid), timestamp, sid, token)
        func = getattr(clazz, phase.replace('-', '_'))
        result = func(ctx, *payload)
        Parser.send(color2, result)

    @staticmethod
    def read(line):
        line = line.strip()
        if line.startswith('config|'):
            Parser.parse_config(line)
        if line.startswith('report|'):
            Parser.parse_report(line)
        if line.startswith('filter|'):
            Parser.parse_filter(line)

    @staticmethod
    def dispatch():
        if not Parser.hooks:
            raise Exception('Please register hooks')
        if not Parser.colors:
            raise Exception('Please register logcolors')
        while True:
            line = stdin.readline().strip()
            Parser.read(line)

    @staticmethod
    def register_logcolors(colors):
        Parser.colors = colors

    @staticmethod
    def register_logfile(logfile):
        Parser.logfile = logfile

    @staticmethod
    def register_hooks(eventlist):
        triggers = set()
        for e in eventlist:
            if isinstance(e, type):
                clazz = e
                classname = e.__name__
                functions = [f for f in dir(clazz) if not f.startswith('_')]
            else:
                clazz = vars(sys.modules[e.__module__])[e.__qualname__.split('.')[0]]
                classname, fun = e.__qualname__.split('.')
                functions = [e.__name__]
            for fun in functions:
                Parser.actionClass[clazz.__name__] = clazz
                classname2 = classname[1:] if classname.startswith('I') else classname
                protocol, system, inout = re.findall('[A-Z][^A-Z]*', classname2)
                subsystem = f'{system.lower()}-{inout.lower()}'
                fname = fun.replace('_', '-')
                triggers.add(f'{protocol.lower()}|{subsystem}|{fname}')
        Parser.hooks = triggers

###############################################################################
# Models
###############################################################################


class IReportSmtpIn:
    @staticmethod
    def link_connect(ctx, rdns, fcrdns, src, dest):
        pass

    @staticmethod
    def link_greeting(ctx, hostname):
        pass

    @staticmethod
    def link_identify(ctx, method, identity):
        pass

    @staticmethod
    def link_tls(ctx, tls_string):
        pass

    @staticmethod
    def link_disconnect(ctx):
        pass

    @staticmethod
    def link_auth(ctx, username, result):
        pass

    @staticmethod
    def tx_reset(ctx, message_id):
        pass

    @staticmethod
    def tx_begin(ctx, message_id):
        pass

    @staticmethod
    def tx_mail(ctx, message_id, result, address):
        pass

    @staticmethod
    def tx_rcpt(ctx, message_id, result, address):
        pass

    @staticmethod
    def tx_envelope(ctx, message_id, envelope_id):
        pass

    @staticmethod
    def tx_data(ctx, message_id, result):
        pass

    @staticmethod
    def tx_commit(ctx, message_id, message_size):
        pass

    @staticmethod
    def tx_rollback(ctx, message_id):
        pass

    @staticmethod
    def protocol_client(ctx, command):
        pass

    @staticmethod
    def protocol_server(ctx, response):
        pass

    @staticmethod
    def filter_report(ctx, filter_kind, name, message):
        pass

    @staticmethod
    def filter_response(ctx, phase, response, param=None):
        pass

    @staticmethod
    def timeout(ctx, phase):
        pass


# noinspection PyUnusedLocal
class IReportSmtpOut:
    @staticmethod
    def link_connect(ctx, rdns, fcrdns, src, dest):
        pass

    @staticmethod
    def link_greeting(ctx, hostname):
        pass

    @staticmethod
    def link_identify(ctx, method, identity):
        pass

    @staticmethod
    def link_tls(ctx, tls_string):
        pass

    @staticmethod
    def link_disconnect(ctx):
        pass

    @staticmethod
    def link_auth(ctx, username, result):
        pass

    @staticmethod
    def tx_reset(ctx, message_id):
        pass

    @staticmethod
    def tx_begin(ctx, message_id):
        pass

    @staticmethod
    def tx_mail(ctx, message_id, result, address):
        pass

    @staticmethod
    def tx_rcpt(ctx, message_id, result, address):
        pass

    @staticmethod
    def tx_envelope(ctx, message_id, envelope_id):
        pass

    @staticmethod
    def tx_data(ctx, message_id, result):
        pass

    @staticmethod
    def tx_commit(ctx, message_id, message_size):
        pass

    @staticmethod
    def tx_rollback(ctx, message_id):
        pass

    @staticmethod
    def protocol_client(ctx, command):
        pass

    @staticmethod
    def protocol_server(ctx, response):
        pass

    @staticmethod
    def filter_report(ctx, filter_kind, name, message):
        pass

    @staticmethod
    def filter_response(ctx, phase, response, param=None):
        pass

    @staticmethod
    def timeout(ctx, phase):
        pass


# noinspection PyUnusedLocal
class IFilterSmtpIn:
    @staticmethod
    def connect(ctx, src, dest):
        return IResultForFilter(ctx).proceed()

    @staticmethod
    def helo(ctx, identity):
        return IResultForFilter(ctx).proceed()

    @staticmethod
    def ehlo(ctx, identity):
        return IResultForFilter(ctx).proceed()

    @staticmethod
    def starttls(ctx, ssl_string):
        return IResultForFilter(ctx).proceed()

    @staticmethod
    def auth(ctx, auth):
        return IResultForFilter(ctx).proceed()

    @staticmethod
    def mail_from(ctx, address):
        return IResultForFilter(ctx).proceed()

    @staticmethod
    def rcpt_to(ctx, address):
        return IResultForFilter(ctx).proceed()

    @staticmethod
    def data(ctx, args):
        return IResultForFilter(ctx).proceed()

    @staticmethod
    def data_line(ctx, line):
        return IResultForFilter(ctx).dataline(line)

    @staticmethod
    def commit(ctx, args):
        return IResultForFilter(ctx).proceed()


class IResultForFilter:
    def __init__(self, ctx):
        self.ctx = ctx

    def _send(self, cmd, *args):
        if cmd == 'dataline':
            result = '|'.join(['filter-dataline', self.ctx.sid, self.ctx.token, args[0]])
        else:
            result = '|'.join(['filter-result', self.ctx.sid, self.ctx.token, cmd, *args])
        return result

    def proceed(self):
        return self._send('proceed')

    def junk(self):
        return self._send('junk')

    def reject(self, error):
        return self._send('reject', error)

    def disconnect(self, error):
        return self._send('disconnect', error)

    def rewrite(self, parameter):
        return self._send('rewrite', parameter)

    def report(self, parameter):
        return self._send('report', parameter)

    def dataline(self, line):
        return self._send('dataline', line)


@dataclass
class Context:
    state: dict
    timestamp: float
    sid: str
    token: str

    def __init__(self, state: dict, timestamp: float, sid: str, token: str = None):
        self.state = state
        self.timestamp = timestamp
        self.sid = sid
        self.token = token


class StateMgr:
    states = {}

    @classmethod
    def get(cls, name):
        if name not in cls.states:
            cls.states[name] = {}
        return cls.states[name]

    @classmethod
    def delete(cls, name):
        del cls.states[name]
