from afilter_utils import Parser
from afilter_utils import IReportSmtpIn, IReportSmtpOut, IFilterSmtpIn

logfile = '/tmp/opensmtpd_afilter.log'


class Colors:
    # PROPERTY = (color, do_log)
    CONFIG = ('\033[35m', 1)
    CONFIG_RESP = ('\033[32m', 1)
    REPORT_IN = ('\033[35m', 1)
    REPORT_OUT = ('\033[35m', 1)
    FILTER_IN = ('\033[35m', 1)
    FILTER_IN_RESP = ('\033[32m', 1)
    END = '\033[0m'


class ReportSmtpIn(IReportSmtpIn):
    @staticmethod
    def link_connect(ctx, rdns, fcrdns, src, dest):
        # your implementation
        pass


class ReportSmtpOut(IReportSmtpOut):
    pass


class FilterSmtpIn(IFilterSmtpIn):
    pass


hooks = [
    ReportSmtpIn, ReportSmtpOut, FilterSmtpIn
]

Parser.register_hooks(hooks)
Parser.register_logcolors(Colors)
Parser.register_logfile(logfile)
Parser.dispatch()
