'''
Communication with the server
'''

import getpass

from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet import reactor

from pdtools.coms import general
from pdtools.coms.client import RpcClient
from pdtools.lib.store import store
from pdtools.lib import riffle, names
from pdtools.lib.output import out
from pdtools.lib.exceptions import *


###############################################################################
# Crossbar
###############################################################################

class BaseSession(ApplicationSession):

    """ Temporary base class for crossbar implementation """

    def __init__(self, config=None):
        ApplicationSession.__init__(self)
        self.config = config

    def onDisconnect(self):
        # print "disconnected"
        reactor.stop()


class ListSession(BaseSession):

    @inlineCallbacks
    def onJoin(self, details):
        ret = yield self.call(u'pd._list', *self.config.extra)

        store.saveConfig('chutes', ret['chutes'])
        store.saveConfig('routers', ret['routers'])
        store.saveConfig('instances', ret['instances'])

        printOwned()

        self.leave()


# @general.failureCallbacks
@inlineCallbacks
def list(r):
    ''' Return the resources this user owns. '''

    args = ['pd.damouse']

    runner = ApplicationRunner("ws://127.0.0.1:8080/ws", u"crossbardemo", extra=args)
    d = yield runner.run(ListSession, start_reactor=False)

    returnValue(d)
    # d.fund

    # reactor.run()

    # yield

    # avatar = yield riffle.portal.connect()
    # ret = yield avatar.list()

    # I don't think this is necesary anymore, but keeping it here for now
    # Have to hit the server every call anyway, so whats the point of saving these
    # simple lists? User will not be able to do anything offline anyway.
    # store.saveConfig('chutes', ret['chutes'])
    # store.saveConfig('routers', ret['routers'])
    # store.saveConfig('instances', ret['instances'])

    # printOwned()

    # returnValue(ret)

###############################################################################
# Riffle Implementation
###############################################################################


class ServerPerspective(riffle.RifflePerspective):

    def perspective_logs(self, logs):
        ''' New logs coming in from the server '''
        for x in logs:
            print out.messageToString(x)


@general.failureCallbacks
@inlineCallbacks
def list2(r):
    ''' Return the resources this us4er owns. '''

    avatar = yield riffle.portal.connect()
    ret = yield avatar.list()

    # I don't think this is necesary anymore, but keeping it here for now
    # Have to hit the server every call anyway, so whats the point of saving these
    # simple lists? User will not be able to do anything offline anyway.
    store.saveConfig('chutes', ret['chutes'])
    store.saveConfig('routers', ret['routers'])
    store.saveConfig('instances', ret['instances'])

    printOwned()

    returnValue(ret)


# Merge this with provision!
@general.failureCallbacks
@inlineCallbacks
def createRouter(r, name):
    '''
    Create a new router on the server-- do not provision it yet. 

    Like so many other things, this is a temporary method.
    '''

    avatar = yield riffle.portal.connect()
    ret = yield avatar.provisionRouter(name)

    # Save that router's keys
    store.saveKey(ret['keys'], ret['_id'] + '.client.pem')

    ret = yield avatar.list()

    store.saveConfig('chutes', ret['chutes'])
    store.saveConfig('routers', ret['routers'])
    store.saveConfig('instances', ret['instances'])

    print 'New router successfully created'
    printOwned()

    returnValue("Done")


@inlineCallbacks
def logs(r, pdid):
    '''
    Query the server for all logs that the given pdid has access to. Must be a fully qualified name.

    NOTE: this method is in progress. For now, just pass the name of one of your routers.
    '''

    # Let the validation occur serverside (or skip it for now)
    pdid = store.getConfig('pdid') + '.' + pdid
    print 'Asking for logs for ' + pdid

    avatar = yield riffle.portal.connect()
    ret = yield avatar.logs(pdid)


@general.defaultCallbacks
@inlineCallbacks
def test(r):
    ''' Should be able to receive a model when prompted '''
    avatar = yield riffle.portal.connect(host='localhost')
    ret = yield avatar.test()

    # print ret.__dict__
    name = yield ret.callRemote('data')
    print 'Result from call: ' + name

###############################################################################
# Authentication
###############################################################################


def authCallbacks(f):
    def w(*args, **kwargs):
        return f(*args, **kwargs).addCallbacks(authSuccess, general.printFailure)

    return w


def authSuccess(r):
    store.saveConfig('pdid', r['_id'])
    store.saveKey(r['keys'], 'client.pem')
    store.saveKey(r['ca'], 'ca.pem')

    print 'You have been successfully logged in.'


@authCallbacks
@inlineCallbacks
def login(reactor, host, port):
    name, password = None, None

    name = raw_input("Username: ")
    password = getpass.getpass()

    client = RpcClient(host, port, '')
    ret = yield client.login(name, password)
    returnValue(ret)


@authCallbacks
@inlineCallbacks
def register(reactor, host, port):
    name, email, pw, pw2 = raw_input("Username: "), raw_input("Email: "), getpass.getpass(), getpass.getpass(prompt='Reenter Password:')

    if pw != pw2:
        raise InvalidCredentials('Your passwords do not match.')

    client = RpcClient(host, port, '')
    ret = yield client.register(name, email, pw)
    print('By using this software you agree to our Privacy Policy as well as our Terms and Conditions.')
    print('  Privacy Policy:        https://paradrop.io/privacy-policy')
    print('  Terms and Conditions:  https://paradrop.io/terms-and-conditions')
    returnValue(ret)


###############################################################################
# Utils
###############################################################################

def printOwned():
    chutes = store.getConfig('chutes')
    routers = store.getConfig('routers')

    def pprint(d):
        print '\t' + d['_id']

    print 'routers'
    [pprint(x) for x in routers]

    print 'chutes'
    [pprint(x) for x in chutes]
