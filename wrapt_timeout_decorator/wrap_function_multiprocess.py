import multiprocess
import sys
from .wrap_helper import raise_exception


class Timeout(object):
    """Wrap a function and add a timeout (limit) attribute to it.
    Instances of this class are automatically generated by the add_timeout
    function defined above. Wrapping a function allows asynchronous calls
    to be made and termination of execution after a timeout has passed.
    """

    def __init__(self, function, timeout_exception, exception_message, dec_timeout, dec_hard_timeout):
        """Initialize instance in preparation for being called."""
        self.dec_timeout = dec_timeout
        self.dec_hard_timeout = dec_hard_timeout
        self.function = function
        self.timeout_exception = timeout_exception
        self.exception_message = exception_message
        self.__name__ = function.__name__
        self.__doc__ = function.__doc__
        self.__process = None
        self.__parent_conn = None
        self.__child_conn = None

    def __call__(self, *args, **kwargs):
        """Execute the embedded function object asynchronously.
        The function given to the constructor is transparently called and
        requires that "ready" be intermittently polled. If and when it is
        True, the "value" property may then be checked for returned data.
        """
        self.__parent_conn, self.__child_conn = multiprocess.Pipe(duplex=False)
        args = (self.__child_conn, self.dec_hard_timeout, self.function) + args
        self.__process = multiprocess.Process(target=_target, args=args, kwargs=kwargs)
        self.__process.daemon = True
        self.__process.start()
        if not self.dec_hard_timeout:
            self.wait_until_process_started()
        if self.__parent_conn.poll(self.dec_timeout):
            return self.value
        else:
            self.cancel()

    def cancel(self):
        """Terminate any possible execution of the embedded function."""
        self.__parent_conn.close()
        if self.__process.is_alive():
            self.__process.terminate()

        raise_exception(self.timeout_exception, self.exception_message)

    def wait_until_process_started(self):
        started = self.__parent_conn.recv()

    @property
    def value(self):
        exception_occured, result = self.__parent_conn.recv()
        self.__parent_conn.close()
        # when self.__parent_conn.recv() exits, maybe __process is still alive,
        # then it might zombie the process. so join it explicitly
        self.__process.join(1)

        if exception_occured:
            raise result
        else:
            return result


def _target(child_conn, dec_hard_timeout, function, *args, **kwargs):
    """Run a function with arguments and return output via a pipe.
    This is a helper function for the Process created in Timeout. It runs
    the function with positional arguments and keyword arguments and then
    returns the function's output by way of a queue. If an exception gets
    raised, it is returned to Timeout to be raised by the value property.
    """
    try:
        if not dec_hard_timeout:
            child_conn.send('started')
        exception_occured = False
        child_conn.send((exception_occured, function(*args, **kwargs)))
    except:
        exception_occured = True
        child_conn.send((exception_occured, sys.exc_info()[1]))
    finally:
        child_conn.close()
