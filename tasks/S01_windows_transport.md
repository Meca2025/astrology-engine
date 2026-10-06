# S01 follow-up: Windows UTF-8 transport verification

The hosted Windows jobs failed because subprocess tests decoded the legacy UTF-8
chart output using the OS cp1252 default. Computation tests passed. Before the next
slice, explicitly decode the documented UTF-8 wire format in subprocess tests and
make new JSON transports ASCII-safe across console encodings. Public computations
and legacy output remain unchanged. Verify locally and inspect the hosted matrix.
