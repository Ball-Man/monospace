import enum
import hashlib
import json
import base64
import requests


class SubmitMode(enum.Enum):
    """Submit modes for gmiscores.

    ALL - insert all the scores in the leaderboard
    HIGHER - update score when a user beats their record
    LOWER - update score when a user beats their record(less is better)
    """
    ALL = 'all'
    HIGHER = 'higher'
    LOWER = 'lower'


class ScoreOrder(enum.Enum):
    """Order types for scores."""
    ASCENDING = 'ASC'
    DESCENDING = 'DESC'


def _json_parsed(fun):
    """Decorator for parsed return values from the API."""
    def decorator(*args, **kwargs):
        return json.loads(fun(*args, **kwargs).text)

    return decorator


class Scores:
    """Class encapsulating ajax requests to a leaderboard service.

    The service documentation can be found at
    https://gmiscores.altervista.org/documentation.php.

    For this class to correctly send requests, a the game secret
    is required(can be obtained from the site above).

    NOTE: private key security is not supported.
    """
    upstream = 'https://gmiscores.altervista.org/api/v1'

    def __init__(self, game_id=-1, secret=''):
        self.secret = secret
        self.game_id = game_id

    def game(self, game_id=None, secret=None):
        """Set the game id and secret for this instance, if given.

        Return the pair current (game_id, secret).
        """
        if game_id is not None:
            self.game_id = game_id

        if secret is not None:
            self.secret = secret

        return self.game_id, self.secret

    def add_raw(self, username, score, mode=SubmitMode.ALL,
                game_id=None, secret=None):
        """Submit a score online.
        Note that this request is synchronous, run it in a separate
        thread when used in real time applications.

        username - The username of the player
        score - The score of the player
        mode - The submit mode (see SubmitMode)
        game_id - The game_id (from https://gmiscores.altervista.org)
                  if not specified, self.game_id will be used
        secret - The game secret (from https://gmiscores.altervista.org)
                 if not specified, self.secret will be used

        A request.model.Response instance. For a parsed result see
        add().
        """
        if game_id is None:
            game_id = self.game_id

        if secret is None:
            secret = self.secret

        # Assemble body
        player = base64.b64encode(username.encode()).decode()
        data = {
            'game': int(game_id),
            'player': player,
            'score': score,
            'insertMode': mode.value,
            'hash': hashlib.sha1(('game={}&score={}&player={}{}')
                .format(int(game_id), score, player, secret).encode())
                .hexdigest()
        }

        return requests.post('{}/add.php'.format(self.upstream),
                             data=data)

    @_json_parsed
    def add(self, username, score, mode=SubmitMode.ALL,
            game_id=None, secret=None):
        """Submit a score online.
        Note that this request is synchronous, run it in a separate
        thread when used in real time applications.

        username - The username of the player
        score - The score of the player
        mode - The submit mode (see SubmitMode)
        game_id - The game_id (from https://gmiscores.altervista.org)
                  if not specified, self.game_id will be used
        secret - The game secret (from https://gmiscores.altervista.org)
                 if not specified, self.secret will be used

        A dictionary containing the response from the server.
        """
        return self.add_raw(username=username, score=score, mode=mode,
                            game_id=game_id, secret=secret)

    def list_raw(self, game_id=None, page=0, perpage=10,
                 order=ScoreOrder.DESCENDING, player=None, start_time=None,
                 end_time=None, include_username=None):
        """Get a list of scores(unparsed).
        Note that this request is synchronous, run it in a separate
        thread when used in real time applications.

        page - The leaderboard page to inspect(only one page at a time)
        perpage - The number of records for page(max 1000)
        order - The score order(ascending, descending, see ScoreOrder)
        player - ID or username of a player. If given, only this
                 player's scores will be returned
        start_time - Filter by date(format 'yyyy-mm-dd [hh:ss:ms]')
        end_time - Filter by date(same format of start_time)
        include_username - name of a player. If given, this player's
                           best score(based on order, start_time,
                           end_time) will be added to the final list.
        game_id - The game_id from https://gmiscores.altervista.org/
                  if not specified self.game_id will be used

        Return a requests.models.Response containing the response of
        the server. For a parsed result see list_parsed().
        Return a dictionary containing the status message returned
        by the server and a list of scores. The format can be seen at
        https://gmiscores.altervista.org/documentation.php.
        """
        if game_id is None:
            game_id = self.game_id

        if type(player) is str:
            player = base64.b64encode(player.encode()).decode()

        if include_username is not None:
            include_username = \
                base64.b64encode(include_username.encode()).decode()

        # Compose query string(payload)
        data = {
            'game': int(game_id),
            'page': int(page),
            'limit': int(perpage),
            'order': order,
            'player': player,
            'startTime': start_time,
            'endTime': end_time,
            'includePlayer': include_username,
        }

        # Removed unspecified ones
        for key, val in list(data.items()):
            if val is None:
                del data[key]

        return requests.get('{}/list.php'.format(self.upstream), params=data)

    @_json_parsed
    def list_parsed(self, game_id=None, page=0, perpage=10,
                    order=ScoreOrder.DESCENDING, player=None, start_time=None,
                    end_time=None, include_username=None):
        """Get a list of scores(parsed).
        Note that this request is synchronous, run it in a separate
        thread when used in real time applications.

        page - The leaderboard page to inspect(only one page at a time)
        perpage - The number of records for page(max 1000)
        order - The score order(ascending, descending, see ScoreOrder)
        player - ID or username of a player. If given, only this
                 player's scores will be returned
        start_time - Filter by date(format 'yyyy-mm-dd [hh:ss:ms]')
        end_time - Filter by date(same format of start_time)
        include_username - name of a player. If given, this player's
                           best score(based on order, start_time,
                           end_time) will be added to the final list.
        game_id - The game_id from https://gmiscores.altervista.org/
                  if not specified self.game_id will be used

        Return a dictionary containing the status message returned
        by the server and a list of scores. The format can be seen at
        https://gmiscores.altervista.org/documentation.php.
        """
        return self.list_raw(
            page=page, perpage=perpage, order=order, player=player,
            start_time=start_time, end_time=end_time,
            include_username=include_username, game_id=game_id)


# Instantiate one client and export methods to module level
_inst = Scores()

game = _inst.game
add_raw = _inst.add_raw
add = _inst.add
list_raw = _inst.list_raw
list_parsed = _inst.list_parsed
