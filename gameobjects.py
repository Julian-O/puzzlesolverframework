class GameObject(object):

    def __init__(self):
        self.subscribers = set()

    def subscribe(self, callback, cookie):
        """Subscribe another object or view to changes to the game object"""

        # Not exception-safe: callbackFunction may not raise exceptions.
        self.subscribers.add((callback, cookie))

    def unsubscribe(self, callback, cookie):
        """Unsubsccribe another object or view from callback notifications."""

        self.subscribers.discard((callback, cookie))

    def _send_notifications(self):
        """ Tell interested parties a change has happened."""
        for (callback, cookie) in self.subscribers:
            callback(cookie)

    def start(self):
        # Simplify things by making all objects startable.
        pass


class ConstrainedGameObject(GameObject):

    """ A ConstrainedGameObject has a set of constraints that it tries to solve
    by examining neighbouring objects.


    States:
        (Non-Existent)
        Initialised,
            Accept subscribe requests but do not call neighbours.
            Can be "configured" (especially with neighbours) in this period
        Started,
            All neighbours are configured.
        Solved,
        Static

        The difference between Solved and Static is Solved objects may continue
        to convey the flow of information, but are resolved sufficiently that
        the puzzle solution isn't dependent on them any more.
    """

    def __init__(self, command_queue):
        self.is_configured = False
        self.is_started = False
        self.is_solved = False
        self.is_static = False
        self.command_queue = command_queue
        GameObject.__init__(self)

    def start(self):
        assert self.is_configured, "Object started before configuring."
        assert not self.is_started, "Object already started."
        self.is_started = True
        self.accept_notification(None)

    def accept_notification(self, cookie):
        """ Accept message from neighbour that your context has changed and
            constraints should be re-evaluated."""
        # Must return quickly. Must not raise an exception.

        # Cookie is ignored! Method must be overridden if it is required.

        if self.is_static:
            return

        if self.is_started:
            # Push apply_constraints onto the command queue.
            self.command_queue.push(self.apply_constraints, cookie, 50)
                # 50 is neutral priority.

    def apply_constraints(self, cookie):
        # Performs the actual logic of the constraints held by object.
        # Do not override.

        assert self.is_started

        # Needs to be repeated in overrides.
        if not self.is_static:
            self._apply_dynamic_constraints(cookie)

    def _apply_dynamic_constraints(self, cookie):
        # Performs the actual logic of the constraints held by object.
        # Must be overridden.
        raise NotImplementedError()
