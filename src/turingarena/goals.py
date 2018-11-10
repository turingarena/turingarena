import logging
import re
from typing import MutableMapping


class Goals(MutableMapping):
    PATTERN = re.compile("[a-z][a-z0-9_]*")

    def __init__(self, on_assign_goal, declared_goals):
        self._assigned_goals = {}
        self._on_assign_goal = on_assign_goal
        self._declared_goals = declared_goals

    def __getitem__(self, item):
        return self._assigned_goals[item]

    def __setitem__(self, key, value):
        assert isinstance(key, str)
        assert self.PATTERN.match(key)
        assert value in (True, False)
        if key not in self._declared_goals:
            logging.warning(f"goal '{key}' is not declared in turingarena.toml!\n" 
                            "This goal will not be registered by the web interface!")
        try:
            assert self._assigned_goals[key] == value, (
                f"goal {key} was already assigned to {self._assigned_goals[key]}"
            )
        except KeyError:
            self._assigned_goals[key] = value
            self._on_assign_goal(dict(type="goal_result", goal=key, result=value))

    def __delitem__(self, key):
        raise NotImplementedError

    def __iter__(self):
        return iter(self._assigned_goals)

    def __len__(self):
        return len(self._assigned_goals)
