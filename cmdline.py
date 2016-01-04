"""Provide access through command line to IGV controlling."""
import socket

import vcf


class SocketManager():

    """A Context Manager to deal with Sockets."""

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = None

    def __enter__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        self.socket.settimeout(1)

        return self.socket

    def __exit__(self, *exc_info):
        self.socket.close()


class IGV():

    """IGV wrapper to control the program through a socket."""

    def __init__(self, host="", port=60151):
        self.host = host
        self.port = port

    def check_igv(self):
        """Return True if a copy of IGV is reachable."""

        response = self.command("echo")

        if response.startswith("echo"):
            return True
        return False

    def command(self, command):
        """Return the response from IGV for command."""
        response = ""
        with SocketManager(self.host, self.port) as s:
            s.sendall(bytes(command, "ascii"))
            response = str(s.recv(1024), "ascii")

        return response

    def goto(self, position):
        """Return "True" if IGV answered "OK" to a goto command."""

        response = self.command("goto {}".format(position))

        if response.startswith("OK"):
            return True
        return False

    def load(self, filepath):
        """Return "True" if IGV answered "OK" to a load command."""

        response = self.command("load {}".format(filepath))

        if response.startswith("OK"):
            return True
        return False


def loadtab(filepath):
    """Return a generator if the filepath is a valid VCF 4.0 file."""
    with open(filepath) as tabfile:
        first_line = tabfile.readline().split("\t")
        if len(first_line) < 5:
            # This doesn't seem to be a valid tab file.
            return False

    return generate_tab(filepath)


def generate_tab(filepath):
    """Yield line by line from a tab file except the header line."""
    first_line = False
    with open(filepath) as tabfile:
        for line in tabfile:
            if first_line:
                yield line.split("\t")
            else:
                first_line = line.lower().split("\t")
                if not any(
                    [_ in first_line for _ in ["start", "end", "alt", "ref"]]):
                    # This file doesn't have a header
                    yield first_line


def loadvcf(filepath):
    """Return a generator if the filepath is a valid VCF 4.0 file."""
    vcf_reader = vcf.Reader(open(filepath))

    if vcf_reader.infos:
        # It seems to be a valid VCF file
        return vcf_reader

    return False
