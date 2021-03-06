import json

from klein import Klein
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks, returnValue

from paradrop.base import pdutils
from paradrop.base.output import out
from . import cors


class ChangeApi(object):
    routes = Klein()

    def __init__(self, update_manager):
        self.update_manager = update_manager

    @routes.route('/', methods=['GET'])
    def get_changes(self, request):
        """
        Get list of active and queued changes.

        Note: we use the term "change" even though, internally, the objects are
        referred to as "updates". The word "update" has become so overloaded it
        causes much confusion. A "change" is an atomic and self-contained
        alteration to the running state of the system. A "change" could install
        a chute, remove a chute, change the host configuration, etc.
        """
        cors.config_cors(request)
        request.setHeader('Content-Type', 'application/json')

        changes = []

        update = self.update_manager.active_change
        if update is not None:
            changes.append({
                'id': update.change_id,
                'updateClass': update.updateClass,
                'updateType': update.updateType,
                'name': getattr(update, 'name', None),
                'version': getattr(update, 'version', None),
                'status': 'processing'
            })

        for update in self.update_manager.updateQueue:
            changes.append({
                'id': update.change_id,
                'updateClass': update.updateClass,
                'updateType': update.updateType,
                'name': getattr(update, 'name', None),
                'version': getattr(update, 'version', None),
                'status': 'queued'
            })

        return json.dumps(changes)
