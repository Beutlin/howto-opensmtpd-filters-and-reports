from pathlib import Path

from afilter_utils import IReportSmtpIn, IReportSmtpOut, IFilterSmtpIn, Parser, ResultForFilter

LOGFILE = './out.log'


# noinspection PyMethodMayBeStatic
class FilterSmtpIn(IFilterSmtpIn):
    def _some_private_function(self):
        pass

    # for further methods see interface
    def rcpt_to(self, ctx, address):
        # _some_private_function()
        return ResultForFilter(ctx).proceed()

    def mail_from(self, ctx, address):
        # _some_private_function()
        return ResultForFilter(ctx).proceed()

    # for further methods see interface


# noinspection PyMethodMayBeStatic
class ReportSmtpIn(IReportSmtpIn):
    # for further methods see interface
    def link_connect(self, ctx, rdns, fcrdns, src, dest):
        pass

    def link_disconnect(self, ctx):
        pass


def main():
    class_method_list = [FilterSmtpIn.rcpt_to, FilterSmtpIn.mail_from, ReportSmtpIn, IReportSmtpOut]
    parser = Parser(
        debugmode=True,
        logfile=Path(LOGFILE) if LOGFILE else None
    )
    parser.prepare_observers(class_method_list)
    parser.dispatch()


if __name__ == '__main__':
    main()
