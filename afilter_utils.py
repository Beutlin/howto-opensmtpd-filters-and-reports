import re
import sys
import types
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Callable


###############################################################################
# Config
###############################################################################

class LogColor:
    INCOMING = '\033[35m'
    OUTCOMING = '\033[32m'
    LOG = '\033[31m'
    END = '\033[0m'


###############################################################################
# Parser
###############################################################################

def log(line: str):
    print(f'{LogColor.LOG}{line}{LogColor.END}', file=sys.stderr, flush=True)


class Parser:
    event_list = []
    event_handlers = {}

    def __init__(self, logfile: Path = None, debugmode: bool = False):
        self.logfile = logfile
        self.debugmode = debugmode

    def _log(self, line, logcolor):
        if self.debugmode and logcolor:
            print(f'{logcolor}{line}{LogColor.END}', file=sys.stderr, flush=True)
        if self.logfile:
            with Path(self.logfile).open("a") as file:
                file.write(line + '\n')

    # noinspection PyUnusedLocal
    def _in(self, logline_type, line):
        self._log(line, LogColor.INCOMING)

    # noinspection PyUnusedLocal
    def _out(self, logline_type, line):
        self._log(line, LogColor.OUTCOMING)
        print(line, file=sys.stdout, flush=True)

    def _register_observers(self):
        for event_name in sorted(self.event_list):
            response_line = f'register|{event_name}'
            self._out(LogLineType.RESPONSE_CONFIG, response_line)
        self._out(LogLineType.RESPONSE_CONFIG, 'register|ready')

    def parse_config(self, line: str):
        self._in(LogLineType.CONFIG, line)
        config = StateMgr.get('config')
        if line != 'config|ready':
            cmd, key, value = line.split('|', 2)
            config[key] = f'{config[key]}|{value}' if key in value else value
        else:
            self._register_observers()

    def parse_report(self, line: str):
        protocol, version, timestamp, subsystem, phase, sid, *payload = line.split('|')
        clazz, logline_type = (self.event_handlers['ReportSmtpOut'], LogLineType.REPORT_OUT) \
            if subsystem == 'smtp-out' else (self.event_handlers['ReportSmtpIn'], LogLineType.REPORT_IN)
        self._in(logline_type, line)
        ctx = Context(StateMgr.get(sid), timestamp, sid)
        func = getattr(clazz, phase.replace('-', '_'))
        func(ctx, *payload)
        if func.__name__ == 'link_disconnect':
            StateMgr.delete(sid)

    def parse_filter(self, line: str):
        protocol, version, timestamp, subsystem, phase, sid, token, *payload = line.split('|')
        clazz, logline_type_request, logline_type_response = (self.event_handlers['FilterSmtpIn'],
                                                              LogLineType.FILTER_IN, LogLineType.RESPONSE_FILTER)
        self._in(logline_type_request, line)
        ctx = Context(StateMgr.get(sid), timestamp, sid, token)
        func = getattr(clazz, phase.replace('-', '_'))
        result = func(ctx, *payload)
        self._out(logline_type_response, result)

    def read(self, line):
        line = line.strip()
        if line.startswith('config|'):
            self.parse_config(line)
        if line.startswith('report|'):
            self.parse_report(line)
        if line.startswith('filter|'):
            self.parse_filter(line)

    def dispatch(self):
        while True:
            line = sys.stdin.readline().strip()
            self.read(line)
            if line == 'exit':
                break

    def prepare_observers(self, class_method_list: list[Callable]):
        event_list = set()
        handlers = {}
        for e in class_method_list:
            if isinstance(e, types.MethodType):
                clazz = e.__self__
                classtype = type(clazz)
                classname = classtype.__name__
                functions = [e.__name__]
            elif isinstance(e, types.FunctionType):
                classname = e.__qualname__.split('.')[0]
                classtype = vars(sys.modules[e.__module__])[classname]
                clazz = classtype()
                functions = [e.__name__]
            elif isinstance(e, type):
                clazz = e()
                classtype = e
                classname = e.__name__
                functions = [f for f in dir(classtype) if not f.startswith('_')]
            else:
                clazz = e
                classtype = type(clazz)
                classname = classtype.__name__
                functions = [f for f in dir(classtype) if not f.startswith('_')]
            for fun in functions:
                classname2 = classname[1:] if classname.startswith('I') else classname
                handlers[classname2] = clazz
                protocol, system, inout = re.findall('[A-Z][^A-Z]*', classname2)
                subsystem = f'{system.lower()}-{inout.lower()}'
                fname = fun.replace('_', '-')
                event_list.add(f'{protocol.lower()}|{subsystem}|{fname}')
        self.event_list = event_list
        self.event_handlers = handlers


# noinspection PyArgumentList
class LogLineType(Enum):
    LOG = auto()
    CONFIG = auto()
    REPORT_IN = auto()
    REPORT_OUT = auto()
    FILTER_IN = auto()
    RESPONSE_CONFIG = auto()
    RESPONSE_FILTER = auto()


###############################################################################
# Models
###############################################################################
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


class IReportSmtpIn:
    def link_connect(self, ctx: Context, rdns, fcrdns, src, dest):
        pass

    def link_greeting(self, ctx: Context, hostname):
        pass

    def link_identify(self, ctx: Context, method, identity):
        pass

    def link_tls(self, ctx: Context, tls_string):
        pass

    def link_disconnect(self, ctx: Context):
        pass

    def link_auth(self, ctx: Context, username, result):
        pass

    def tx_reset(self, ctx: Context, message_id):
        pass

    def tx_begin(self, ctx: Context, message_id):
        pass

    def tx_mail(self, ctx: Context, message_id, result, address):
        pass

    def tx_rcpt(self, ctx: Context, message_id, result, address):
        pass

    def tx_envelope(self, ctx: Context, message_id, envelope_id):
        pass

    def tx_data(self, ctx: Context, message_id, result):
        pass

    def tx_commit(self, ctx: Context, message_id, message_size):
        pass

    def tx_rollback(self, ctx: Context, message_id):
        pass

    def protocol_client(self, ctx: Context, command):
        pass

    def protocol_server(self, ctx: Context, response):
        pass

    def filter_report(self, ctx: Context, filter_kind, name, message):
        pass

    def filter_response(self, ctx: Context, phase, response, param=None):
        pass

    def timeout(self, ctx: Context, phase):
        pass


class IReportSmtpOut:
    def link_connect(self, ctx: Context, rdns, fcrdns, src, dest):
        pass

    def link_greeting(self, ctx: Context, hostname):
        pass

    def link_identify(self, ctx: Context, method, identity):
        pass

    def link_tls(self, ctx: Context, tls_string):
        pass

    def link_disconnect(self, ctx: Context):
        pass

    def link_auth(self, ctx: Context, username, result):
        pass

    def tx_reset(self, ctx: Context, message_id):
        pass

    def tx_begin(self, ctx: Context, message_id):
        pass

    def tx_mail(self, ctx: Context, message_id, result, address):
        pass

    def tx_rcpt(self, ctx: Context, message_id, result, address):
        pass

    def tx_envelope(self, ctx: Context, message_id, envelope_id):
        pass

    def tx_data(self, ctx: Context, message_id, result):
        pass

    def tx_commit(self, ctx: Context, message_id, message_size):
        pass

    def tx_rollback(self, ctx: Context, message_id):
        pass

    def protocol_client(self, ctx: Context, command):
        pass

    def protocol_server(self, ctx: Context, response):
        pass

    def filter_report(self, ctx: Context, filter_kind, name, message):
        pass

    def filter_response(self, ctx: Context, phase, response, param=None):
        pass

    def timeout(self, ctx: Context, phase):
        pass


# noinspection PyUnusedLocal,PyMethodMayBeStatic
class IFilterSmtpIn:
    def connect(self, ctx: Context, src, dest):
        return ResultForFilter(ctx).proceed()

    def helo(self, ctx: Context, identity):
        return ResultForFilter(ctx).proceed()

    def ehlo(self, ctx: Context, identity):
        return ResultForFilter(ctx).proceed()

    def starttls(self, ctx: Context, ssl_string):
        return ResultForFilter(ctx).proceed()

    def auth(self, ctx: Context, auth):
        return ResultForFilter(ctx).proceed()

    def mail_from(self, ctx: Context, address):
        return ResultForFilter(ctx).proceed()

    def rcpt_to(self, ctx: Context, address):
        return ResultForFilter(ctx).proceed()

    def data(self, ctx: Context, args):
        return ResultForFilter(ctx).proceed()

    def data_line(self, ctx: Context, line):
        return ResultForFilter(ctx).dataline(line)

    def commit(self, ctx: Context, args):
        return ResultForFilter(ctx).proceed()


class ResultForFilter:
    def __init__(self, ctx: Context):
        self.ctx = ctx

    def _complete(self, cmd, *args):
        if cmd == 'dataline':
            result = '|'.join(['filter-dataline', self.ctx.sid, self.ctx.token, args[0]])
        else:
            result = '|'.join(['filter-result', self.ctx.sid, self.ctx.token, cmd, *args])
        return result

    def proceed(self):
        return self._complete('proceed')

    def junk(self):
        return self._complete('junk')

    def reject(self, error):
        return self._complete('reject', error)

    def disconnect(self, error):
        return self._complete('disconnect', error)

    def rewrite(self, parameter):
        return self._complete('rewrite', parameter)

    def report(self, parameter):
        return self._complete('report', parameter)

    def dataline(self, line):
        return self._complete('dataline', line)


class StateMgr:
    states = {}

    @classmethod
    def get(cls, name: str):
        if name not in cls.states:
            cls.states[name] = {}
        return cls.states[name]

    @classmethod
    def delete(cls, name: str):
        del cls.states[name]
