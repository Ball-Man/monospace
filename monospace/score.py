import desper


HIGH_SCORE_GET_QUERY = "SELECT `value` FROM `scores` WHERE `type`='high'"
HIGH_SCORE_UPDATE_QUERY = "UPDATE `scores` SET `value`=? WHERE `type`='high'"
TOT_SCORE_GET_QUERY = "SELECT `value` FROM `scores` WHERE `type`='total'"
TOT_SCORE_ADD_QUERY = ("UPDATE `score` SET `value`=`value` "
                       + " ? WHERE `type`='total'")

temp_score = None


def get_high_score(db):
    """Get current high score."""
    cur = db.cursor()
    return next(cur.execute(HIGH_SCORE_GET_QUERY))[0]


def set_high_score(db, score):
    """Set current highscore."""
    cur = db.cursor()
    cur.execute(HIGH_SCORE_UPDATE_QUERY, score)
    db.commit()


def get_total_score(db):
    """Get current total score."""
    cur = db.cursor()
    return next(cur.execute(HIGH_SCORE_GET_QUERY))[0]


def add_total_score(db, score):
    """Add score to the current total."""
    cur = db.cursor()
    cur.execute(TOT_SCORE_ADD_QUERY, score)
    db.commit()


class DeathScoreManager(desper.OnAttachListener):
    """Component for score management."""

    def on_attach(self, en, world):
        if temp_score is None:
            return

        print('score:', temp_score)
