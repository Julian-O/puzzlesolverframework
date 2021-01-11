class View(object):
    _viewRegistry = {}

    @classmethod
    def register(cls, renderable_classes, cookie=None):
        """Called by subclasses of the View class, to register themselves as
           available to render a class."""
        # The cookie is to distinguish between multiple possible views of the
        # same object.
        for rcls in renderable_classes:
            View._viewRegistry[(rcls, cookie)] = cls

    @staticmethod
    def view_cls(object_to_render, cookie=None):
        """Called by factories trying to make View objects
           that best correspond to a given instance."""
        return View._viewRegistry[object_to_render.__class__, cookie]


class GameBoardView(View):

    def __init__(self, gameboard, controller):
        self.gameboard = gameboard

    def resize(self, dimensions):
        """Inform game window of initial, or changed, size of the window"""

        # Calc pixel size, and inform all the subpanels.
        raise NotImplementedError()

    def solve(self, max_count=None, max_period=None):
        self.gameboard.solve(max_count, max_period)


class GamePanelView(View):

    def set_surface(self, surface):
        raise NotImplementedError()


class GameObjectView(View):

    def __init__(self, game_object, cookie=None):
        self.gameObject = game_object
        game_object.subscribe(self.notify, cookie)

    def set_surface(self, surface):
        raise NotImplementedError()

    def notify(self, cookie):
        raise NotImplementedError()


class Controller(object):

    def __init__(self):
        self.bounding_boxes = dict()
        self.callback_map = dict()

    def register(self, surface, callback, cookie):
        """Register for clicks on this surface
           If a click occurs on this surface, you will be called back with
           the parameters: button number, offset from left corner, cookie.
           Surface must be a subsurface of the _game_board_view's surface.
           Will automatically remove any existing subscriptions with the
           same callback and cookie.
           Behaviour for overlapping registrations is not defined."""

        top_left_corner = surface.get_abs_offset()
        size = surface.get_size()
        bounding_box = (
            top_left_corner[0], top_left_corner[1],
            top_left_corner[0] + size[0], top_left_corner[1] + size[1])

        # print bounding_box
        callback_key = (callback, cookie)
        if callback_key in self.callback_map:
            del self.bounding_boxes[self.callback_map[callback_key]]
        self.bounding_boxes[bounding_box] = callback_key
        self.callback_map[callback_key] = bounding_box

    def deregister(self, callback, cookie):
        callback_key = (callback, cookie)

        if callback_key in self.callback_map:
            del self.bounding_boxes[self.callback_map[callback_key]]
            del self.callback_map[callback_key]

    def _find_and_notify_subscriber(self, button, offset):
        for (bounding_box, callback_key) in self.bounding_boxes.items():
            if (
                    bounding_box[0] < offset[0] and
                    bounding_box[1] < offset[1] and
                    bounding_box[2] > offset[0] and
                    bounding_box[3] > offset[1]):

                # print offset, " is in ",bounding_box
                (callback, cookie) = callback_key
                callback(
                    button,
                    (offset[0] - bounding_box[0],
                     offset[1] - bounding_box[1]),
                    cookie)

try:
    import pygamesilent as pygame

    class PyGameController(Controller):

        """Implements a basic solver for PyGame based solutions."""

        def __init__(self):
            Controller.__init__(self)
            self._game_board_view = None  # Needs to be set by subclass.

        def default_solver(
                self,
                work_cycle_len=500, sleep_cycle_len=250,
                keyboard_callback=None):
            """ Implements a simple solver that iteratively solves a little
            piece of the puzzle, and sleeps to keep the CPU low. It
            automatically handles quitting and windows resize. It also passes
            Mouse Button Down events to the appropriate subscribers.
            It can callback on keyboard input (keydown).
            """

            # work_cycle_len (milliseconds) is how to spend processing before
            # returning for input.

            # sleep_cycle_len (milliseconds) is the maximum amount of time to
            # spend waiting quietly for input before processing again.

            # Both of these figures are rough; button clicking will make it
            # spend more CPU than expected.

            # Solved problems will make it spend less CPU time than expected.

            assert self._game_board_view, "Gameboard view not set by subclass."

            pygame.time.set_timer(
                pygame.USEREVENT + 1, work_cycle_len + sleep_cycle_len)
                                  # Wake up and process more every n
                                  # milliseconds.
            while(1):
                event = pygame.event.wait()
                if event.type == pygame.QUIT:
                    break

                if event.type == pygame.VIDEORESIZE:
                    self._game_board_view.resize(event.size)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    self._find_and_notify_subscriber(event.button, event.pos)
                    
                if keyboard_callback and event.type == pygame.KEYDOWN:
                    keyboard_callback(event.key)

                self._game_board_view.solve(None, work_cycle_len / 1000.0)

except ImportError:
    print("WARNING: pygame not installed.")
    print("PyGameController not defined in " + __name__)
