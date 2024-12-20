# !/usr/bin/python
# coding=utf-8
#
# Copyright (C) 2018-2025 by dream-alpha
#
# In case of reuse of this source code please do not remove this copyright.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# For more information on the GNU General Public License see:
# <http://www.gnu.org/licenses/>.

# pylint: disable=W1113, W0212, W0221, W0222


import json
from cookielib import CookieJar
from twisted.internet import reactor
from twisted.web.http_headers import Headers
from twisted.internet.task import deferLater
from twisted.web.client import Agent, RedirectAgent, _GzipProtocol, CookieAgent, BrowserLikePolicyForHTTPS, HTTPConnectionPool, _requireSSL, PartialDownloadError
from twisted.internet.protocol import Protocol
from twisted.internet.defer import Deferred, DeferredSemaphore, succeed
from twisted.web.iweb import IBodyProducer
from twisted.internet.ssl import ClientContextFactory as ssl_ClientContextFactory, CertificateOptions, AcceptableCiphers
from twisted.internet._sslverify import ClientTLSOptions, verifyHostname, VerificationError
from twisted.web._newclient import ResponseDone, ResponseFailed, PotentialDataLoss
from twisted.python.failure import Failure
from twisted.internet.error import CertificateError
from twisted.web import http
from zope.interface import implementer
from OpenSSL import SSL as _SSL
from API import session as mysession
from .__init__ import _
from .Debug import logger


_headers = Headers({"User-Agent": ["Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"]})
_headers.addRawHeader("content-type", "text/html; charset=UTF-8")
_headers.addRawHeader("Accept-Language", "de, de-DE;q=0.9, en;q=0.8, en-GB;q=0.7, en-US;q=0.6")
_headers.addRawHeader("Accept-Charset", "utf-8, iso-8859-1;q=0.5")
_headers.addRawHeader("Accept", "text/html, application/xhtml+xml, application/xml;q=0.9, image/webp, */*;q=0.8")
_headers.addRawHeader("Cache-Control", "public, max-age=86400, max-stale=86400")
_headers.addRawHeader("Sec-CH-UA", 'Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24')
_headers.addRawHeader("SEC-CH-UA-FULL-VERSION", "107.0.5304.88")
_headers.addRawHeader("Sec-CH-UA-Mobile", "?0")
_headers.addRawHeader("Sec-CH-UA-Platform", "Windows")
_headers.addRawHeader("Sec-CH-UA-Platform-Version", "10.0.0")
_headers.addRawHeader("Sec-CH-UA-Model", "")
_headers.addRawHeader("SEC-CH-UA-ARCH", "x86")
_headers.addRawHeader("Sec-CH-UA-Bitness", "64")
_headers.addRawHeader("DNT", "1")
_headers.addRawHeader("Connection", "keep-alive")
headers_gzip = _headers.copy()
headers_gzip.addRawHeader("Accept-Encoding", "gzip, deflate")
headersplain = _headers.copy()
headersplain.setRawHeaders("content-type", ["text/plain; charset=UTF-8"])
headers_ts = Headers({"User-Agent": ["GStreamer souphttpsrc libsoup/2.52.2"]})
headers_ts.setRawHeaders("content-type", ["application/x-mpegURL"])
headers_dash = _headers.copy()
headers_dash.setRawHeaders("content-type", ["application/dash+xml"])
_headers_jpeg = _headers.copy()
_headers_jpeg.setRawHeaders("content-type", ["image/jpeg"])
_headers_svg = _headers.copy()
_headers_svg.setRawHeaders("content-type", ["image/svg+xml"])
_headers_json = _headers.copy()
_headers_json.setRawHeaders("content-type", ["application/json; charset=utf-8"])


_downloads = dict()
_downloads["state"] = True


def MyCallLater(ltime, iscallable, *args, **kwargs):
	logger.info("...")
	return reactor.callLater(ltime, iscallable, *args, **kwargs)


class CallLater:
	def __init__(self, result, iscallable, *args, **kwargs):
		logger.info("...")
		reactor.callLater(0, iscallable, result, *args, **kwargs)

	def __del__(self):
		logger.info("...")


class MyDeferredSemaphore:
	def __init__(self, tokens=1):
		logger.info("...")
		self.ds = DeferredSemaphore(tokens=tokens)
		self._deferreds = []
		self.work = dict()
		_downloads["state"] = True

	def run(self, *args, **kwargs):
		logger.info("...")
		return self.ds.run(*args, **kwargs)

	def rundeferLater(self, ltime=0.0, *args, **kwargs):
		logger.info("...")
		return deferLater(reactor, ltime, self.ds.run, *args, **kwargs)

	def start(self, *args, **kwargs):
		logger.info("...")
		return self.rundeferLater(0.0, *args, **kwargs)

	def deferCanceler(self, _cancel=True):
		logger.info("...")
		for items in self.ds.waiting:
			items.cancel()

	def settokens(self, tokens=10):
		logger.info("...")
		self.ds.tokens = tokens
		self.ds.limit = tokens

	def finished(self):
		logger.info("...")
		return self.ds.tokens >= self.ds.limit

	def __del__(self):
		logger.info("...")
		self.deferCanceler()
		self.work.clear()


class _MyClientTLSOptions(ClientTLSOptions):
	def _identityVerifyingInfoCallback(self, connection, where, _ret):
		logger.info("...")
		if where & _SSL.SSL_CB_HANDSHAKE_START:
			connection.set_tlsext_host_name(self._hostnameBytes)
		elif where & _SSL.SSL_CB_HANDSHAKE_DONE:
			try:
				verifyHostname(connection, self._hostnameASCII)
			except (CertificateError, VerificationError) as e:
				logger.debug("Remote certificate is not valid for hostname %s; %s", self._hostnameASCII, e)
			except ValueError as e:
				logger.debug("Ignoring error while verifying certificate from host %s (exception: %s)", self._hostnameASCII, repr(e))


try:
	MyClientTLSOptions = ClientTLSOptions
except Exception:
	MyClientTLSOptions = _MyClientTLSOptions


class ClientContextFactory(ssl_ClientContextFactory):
	def __init__(self):
		logger.info("...")
		self.method = _SSL.SSLv23_METHOD

	def getContext(self, hostname=None, _port=None):
		logger.info("...")
		ctx = self._contextFactory(self.method)
		ctx.set_options(_SSL.OP_SINGLE_DH_USE | _SSL.OP_NO_SSLv2 | _SSL.OP_NO_SSLv3 | _SSL.OP_ALL)
		ctx.set_session_cache_mode(_SSL.SESS_CACHE_BOTH)
		if hostname:
			MyClientTLSOptions(hostname, ctx)
		return ctx


defaultCiphers = AcceptableCiphers.fromOpenSSLCipherString(
	"TLS13-AES-256-GCM-SHA384:TLS13-CHACHA20-POLY1305-SHA256:"
	"TLS13-AES-128-GCM-SHA256:"
	"ECDH+AESGCM:ECDH+CHACHA20:DH+AESGCM:DH+CHACHA20:ECDH+AES256:DH+AES256:"
	"ECDH+AES128:DH+AES:RSA+AESGCM:RSA+AES:"
	"!aNULL:!MD5:!DSS")


class ClientContextFactory__(BrowserLikePolicyForHTTPS):

	def _getCertificateOptions(self, _hostname, _port):
		logger.info("...")
		return CertificateOptions(verify=False, method=_SSL.SSLv23_METHOD, fixBrokenPeers=True, acceptableCiphers=defaultCiphers, )

	@_requireSSL
	def getContext(self, hostname=None, port=None):
		logger.info("...")
		return self._getCertificateOptions(hostname, port).getContext()

	@_requireSSL
	def creatorForNetloc(self, hostname, port):
		logger.info("...")
		return MyClientTLSOptions(hostname.decode("ascii"), self.getContext(hostname, port))


class MyRedirectAgent(RedirectAgent):
	_redirectResponses = [http.MOVED_PERMANENTLY, http.FOUND]
	_seeOtherResponses = [http.SEE_OTHER]


class mydownloadWithProgress:
	def __init__(self, url, fileOrName, headers=None, *args, **kwargs):
		logger.info("...")
		self.factory = getPagenew(url=url, fileOrName=fileOrName, headers=headers, *args, **kwargs)

	def start(self):
		logger.info("...")
		return self.factory.deferred

	def stop(self):
		logger.info("...")
		self.factory.deferred.cancel()

	def addProgress(self, progress_callback):
		logger.info("...")
		self.factory.progress_callback = progress_callback


def MydownloadPage(url, file=None, method="GET", headers=_headers, postdata=None, contextFactory=ClientContextFactory(), *args, **kwargs):
	logger.info("...")
	return getPagenew(url, file, method, headers, postdata, contextFactory, *args, **kwargs).deferred


def MygetPage(url, fileOrName=None, method="GET", headers=_headers, postdata=None, contextFactory=ClientContextFactory(), *args, **kwargs):
	logger.info("...")
	return getPagenew(url, fileOrName, method, headers, postdata, contextFactory, *args, **kwargs).deferred


@implementer(IBodyProducer)
class StringProducer(object):
	def __init__(self, body):
		logger.info("...")
		self.body = body
		self.length = len(body)

	def startProducing(self, consumer):
		logger.info("...")
		consumer.write(self.body)
		return succeed(None)

	def pauseProducing(self):
		logger.info("...")

	def stopProducing(self):
		logger.info("...")


class ReadBodyProtocol(Protocol):
	def __init__(self, status, message, deferred):
		logger.info("...")
		self.deferred = deferred
		self.status = status
		self.message = message
		self.dataBuffer = []

	def dataReceived(self, data):
		logger.info("...")
		self.dataBuffer.append(data)

	def connectionLost(self, reason):
		logger.info("...")
		if reason.check(ResponseDone):
			self.deferred.callback(b"".join(self.dataBuffer))
		elif reason.check(PotentialDataLoss):
			self.deferred.errback(PartialDownloadError(self.status, self.message, b"".join(self.dataBuffer)))
		else:
			self.deferred.errback(reason)


class ReadBodyURI(Protocol):
	def __init__(self, deferred, response):
		logger.info("...")
		self.deferred = deferred
		self._response = response
		self.dataBuffer = []

	def dataReceived(self, data):
		logger.info("...")
		self.dataBuffer.append(data)

	def connectionLost(self, reason):
		logger.info("...")
		if reason.check(ResponseDone):
			self.deferred.callback((b"".join(self.dataBuffer), self._response.request.absoluteURI))
		elif reason.check(PotentialDataLoss):
			self.deferred.errback(PartialDownloadError(self._response.code, self._response.phrase, b"".join(self.dataBuffer)))
		else:
			self.deferred.errback(reason)


class ReadBody(Protocol):
	def __init__(self, finished, response, fileOrName, progress_callback):
		logger.info("...")
		self.finished = finished
		self._response = response
		self.currentbytes = 0.0
		self.progress_callback = progress_callback
		self.datafile = None
		if isinstance(fileOrName, str):
			self.datafile = open(fileOrName, "wb")
		else:
			self.datafile = fileOrName

	def dataReceived(self, data):
		logger.info("...")
		try:
			if self.finished.called:
				return
			if self.datafile:
				self.datafile.write(data)
			self.currentbytes += len(data)
			if self._response.length and self.progress_callback:
				self.progress_callback(self.currentbytes, self._response.length)
		except IOError:
			self.finished.errback(Failure())

	def connectionLost(self, reason):
		logger.info("...")
		if self.datafile:
			try:
				self.datafile.close()
			except Exception:
				self.finished.errback(Failure())

		if reason.check(ResponseDone):
			self.finished.callback(None)
		elif reason.check(PotentialDataLoss):
			self.finished.errback(Failure())
		else:
			self.finished.errback(reason)


class getPagenew(object):
	progress_callback = None

	def __init__(self, url, fileOrName=None, method="GET", headers=None, postdata=None, contextFactory=ClientContextFactory(), location=None, timeout=10.0, cookies=None, *args, **kwargs):
		logger.info("...")
		body = None
		if postdata:
			body = StringProducer(postdata)
		pool = HTTPConnectionPool(reactor, persistent=True)
		pool.maxPersistentPerHost = 10
		pool.cachedConnectionTimeout = 600
		pool.retryAutomatically = True
		pool._factory.noisy = False

		agent = MyRedirectAgent(Agent(reactor, contextFactory=contextFactory, connectTimeout=timeout, bindAddress=None, pool=pool))
		cookieJar = None
		if cookies:
			cookieJar = CookieJar()
			agent = CookieAgent(agent, cookieJar)

		self.deferred = agent.request(method=method, uri=url, headers=headers, bodyProducer=body)
		self.deferred.addCallback(self.calresponse, fileOrName, location, cookieJar, *args, **kwargs)

	def calresponse(self, response, fileOrName, location, cookieJar, *args, **kwargs):
		def _cancel(_):
			logger.info("...")
			try:
				response._transport._producer.abortConnection()
			except Exception:
				pass

		logger.info("...")
		finished = Deferred(canceller=_cancel)
		if "CallbackResponse" in kwargs:
			kwargs["CallbackResponse"](self, response, fileOrName, location, cookieJar, *args, **kwargs)
		if response.code not in (200, 301, 302, 303):
			raise ResponseFailed("{0} {1}".format(response.code, response.phrase), response)
		gzipdecoder = "gzip" in response.headers.getRawHeaders("Content-Encoding", "none")

		if not location and gzipdecoder:
			response.deliverBody(_GzipProtocol(ReadBodyProtocol(response.code, response.phrase, finished), response))
		elif fileOrName:
			response.deliverBody(ReadBody(finished, response, fileOrName, self.progress_callback))
		elif location:
			if gzipdecoder:
				response.deliverBody(_GzipProtocol(ReadBodyURI(finished, response), response))
			else:
				response.deliverBody(ReadBodyURI(finished, response))
		else:
			response.deliverBody(ReadBodyProtocol(response.code, response.phrase, finished))
		return finished

	def calerr(self, _err):
		logger.info("...")


def writerawheaders(response, *_args, **_kwargs):
	logger.info("...")
	with open("/tmp/rawheaders.json", "w") as fp:
		json.dump(list(response.headers.getAllRawHeaders()), fp, encoding="utf-8", indent=2, sort_keys=True)


def http_failed(failure_instance=None, *_args, **kwargs):
	logger.info("...")
	error_message = str(failure_instance.getErrorMessage())
	if not error_message:
		error_message = str(failure_instance)
	text = _(kwargs.get("title", "Error")) + "\n"
	text += _("Error during download") + "\n\n" + error_message + "\n"
	logger.error("error_message: %s", error_message)
	try:
		if mysession:
			mysession.toastManager.showToast(text, int(kwargs.get("duration", 20)))
	except Exception as e:
		logger.error("exception: %s", e)
