import dsdl
import monospace
import desper
from sdl2 import *
from sdl2.sdlttf import *


HIGH_SCORE_GET_QUERY = "SELECT `value` FROM `scores` WHERE `type`='high'"
HIGH_SCORE_UPDATE_QUERY = "UPDATE `scores` SET `value`=? WHERE `type`='high'"
TOT_SCORE_GET_QUERY = "SELECT `value` FROM `scores` WHERE `type`='total'"
TOT_SCORE_ADD_QUERY = ("UPDATE `scores` SET `value`=`value`+? "
                       + " WHERE `type`='total'")

temp_score = None


def get_high_score(db):
    """Get current high score."""
    cur = db.cursor()
    return next(cur.execute(HIGH_SCORE_GET_QUERY))[0]


def set_high_score(db, score):
    """Set current highscore."""
    cur = db.cursor()
    cur.execute(HIGH_SCORE_UPDATE_QUERY, (score,))
    db.commit()


def get_total_score(db):
    """Get current total score."""
    cur = db.cursor()
    return next(cur.execute(HIGH_SCORE_GET_QUERY))[0]


def add_total_score(db, score):
    """Add score to the current total."""
    cur = db.cursor()
    cur.execute(TOT_SCORE_ADD_QUERY, (score,))
    db.commit()


class DeathScoreManager(desper.OnAttachListener):
    """Component for score management."""

    def on_attach(self, en, world):
        global temp_score

        if temp_score is None:
            return

        res = monospace.model.res
        db = res['db']['current'].get()

        highscore = get_high_score(db)
        print('highscore', highscore)
        print('score', temp_score)

        # Render current score
        score_surf = TTF_RenderUTF8_Blended(
            res['fonts']['timenspace'].get(), str(temp_score).encode(),
            SDL_Color())
        score_texture = SDL_CreateTextureFromSurface(
            monospace.model.renderer, score_surf)
        SDL_FreeSurface(score_surf)

        # Configure deathscreen based on the record(have you beat it?)
        if temp_score <= highscore:    # Not beaten
            # Add current score
            world.create_entity(dsdl.Position(30, 30), score_texture)

            highscore_y = 130

            # Render HIGH SCORE string
            world.create_entity(
                dsdl.Position(30, highscore_y),
                res['str'][monospace.current_lang].get_texture('highscore'))

            hs_surf = TTF_RenderUTF8_Blended(
                res['fonts']['timenspace'].get(),
                str(highscore).encode(), SDL_Color())
            hs_texture = SDL_CreateTextureFromSurface(monospace.model.renderer,
                                                      hs_surf)

            # Render actual highschore
            # If there's no space, shift vertically the score
            if (res['str'][monospace.current_lang].get_texture('highscore').w
                    + hs_surf.contents.w + 2 * 30 >= monospace.LOGICAL_WIDTH):
                highscore_y += 100

            world.create_entity(
                dsdl.Position(
                    monospace.LOGICAL_WIDTH - 30 - hs_surf.contents.w,
                    highscore_y),
                hs_texture)

            SDL_FreeSurface(hs_surf)
        else:       # Beaten
            # Update highscore
            set_high_score(db, int(temp_score))

            # NEW RECORD text
            world.create_entity(
                res['str'][monospace.current_lang].get_texture('newrecord'),
                dsdl.Position(30, 30))

            # Add current score
            world.create_entity(dsdl.Position(30, 130), score_texture)

        # Update total score and reset temp
        add_total_score(db, int(temp_score))
        temp_score = None
