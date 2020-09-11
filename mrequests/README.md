# mrequests

This is a variant of the `urequests` module from `micropython-lib` with a few
extension:

* Response headers can optionally be saved in the response object.
* The class for reponse objects can be substituted by a custon response class.
* Support for HTTP basic auth (requires `ubinascii` module).
* Support for responses with chunked transfer encoding.
* Respects `Content-length` header in response.
* Response objects have a `save` method, to save the response body to
  a file, reading the response data and writing the file in small chunks.

Otherwise the API remains the same.
