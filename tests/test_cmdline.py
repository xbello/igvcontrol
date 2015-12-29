"""Tests for the command line interface."""
import socketserver
import threading
from unittest import TestCase

import cmdline


class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        """Return the same it receives."""
        data = str(self.request.recv(1024), 'ascii')

        response = bytes("", "ascii")
        if data == "echo":
            response = bytes("{}".format(data), 'ascii')
        elif data.startswith(("goto", "load")):
            response = bytes("OK\n", 'ascii')

        self.request.sendall(response)


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True


class TestCmd(TestCase):
    def setUp(self):
        super().setUp()
        self.igv_server = ThreadedTCPServer(
            ("", 60151), ThreadedTCPRequestHandler)

        server_thread = threading.Thread(target=self.igv_server.serve_forever)
        server_thread.daemon = True
        server_thread.start()

        self.igv_client = cmdline.IGV()

    def tearDown(self):
        self.igv_server.shutdown()
        self.igv_server.server_close()
        super().tearDown()

    def test_can_IGV_client_as_object(self):
        self.assertTrue(isinstance(self.igv_client, cmdline.IGV))

    def test_we_can_send_multiple_commands(self):
        self.assertTrue(self.igv_client.check_igv())
        self.assertTrue(self.igv_client.goto("chr1:12345"))

    def test_check_igv_is_running(self):
        self.assertTrue(self.igv_client.check_igv())

    def test_we_can_send_goto_signal(self):
        self.assertTrue(self.igv_client.goto("chr1:123456"))

    def test_we_can_send_load_signal(self):
        self.assertTrue(self.igv_client.load("path/to/file.bam"))

    def test_we_can_send_through_command_method(self):
        self.assertEqual(self.igv_client.command("echo"), "echo")
