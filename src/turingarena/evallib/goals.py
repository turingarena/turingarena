import logging
import re
from typing import MutableMapping

from turingarena.evallib.evaluation import send_data
from turingarena.evallib.metadata import load_metadata


class Goals(MutableMapping):
    PATTERN = re.compile("[a-z][a-z0-9_]*")

    def __init__(self):
        self._assigned_goals = {}

    @property
    def _declared_goals(self):
        return load_metadata().get("scoring", {}).get("goals", [])

    def check_goal(self, goal, checker):
        """
        Check the specify goal:
            - if the goal was already assigned to False, skip check
            - if not, call the function checker():
                * if it returns False, then set the goal as failed
                * if it returns True,  do nothing
        :param goal: the name of the goal to check
        :param checker: a function to invoke to check the goal
        :return: the boolean returned by checker if it was invoked, None if it was skipped (goal already failed)
        :raise: RuntimeError if the goal that you are testing was already set to true
        """
        if goal in self._assigned_goals:
            if self._assigned_goals[goal]:
                raise RuntimeError(f"the goal {goal} was already assigned!")
            else:
                logging.info(f"Skipping goal {goal} because it was already failed")
        else:
            result = checker()
            assert isinstance(result, bool), "Checker function must return a boolean"
            if not result:
                self._assigned_goals[goal] = False
            return result

    def __getitem__(self, item):
        return self._assigned_goals[item]

    def __setitem__(self, key, value):
        assert isinstance(key, str)
        assert self.PATTERN.match(key)
        assert value in (True, False)
        if key not in self._declared_goals:
            logging.error(f"goal '{key}' is not declared in turingarena.toml!\n"
                            "This goal will not be registered by the web interface!")
        try:
            assert self._assigned_goals[key] == value, (
                f"goal {key} was already assigned to {self._assigned_goals[key]}"
            )
        except KeyError:
            self._assigned_goals[key] = value
            send_data(dict(type="goal_result", goal=key, result=value))

    def __delitem__(self, key):
        raise NotImplementedError

    def __iter__(self):
        return iter(self._assigned_goals)

    def __len__(self):
        return len(self._assigned_goals)

    def __str__(self):
        return f"Goals({dict(self)})"

