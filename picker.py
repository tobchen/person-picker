# Person Picker
# Copyright (C) 2023  Tobias Heukäufer
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from typing import Dict, Optional, List, Tuple, Any, Set
import random
import sys
import json
import os


class Person(object):
    def __init__(self, name: str, times_unproposed: int, times_rejected: int):
        self._name = name
        self._times_unproposed = max(0, times_unproposed)
        self._times_rejected = max(0, times_rejected)
        self._active = True
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def times_unproposed(self) -> int:
        return self._times_unproposed

    @property
    def times_rejected(self) -> int:
        return self._times_rejected
    
    @property
    def active(self) -> bool:
        return self._active

    def increase_times_unproposed(self):
        self._times_unproposed += 1
    
    def increase_times_rejected(self):
        self._times_rejected += 1
    
    def reset(self):
        self._times_unproposed = 0
        self._times_rejected = 0
    
    def deactivate(self):
        self._active = False
    
    def to_json(self) -> Dict[str, Any]:
        return {
            "name": self._name,
            "timesUnproposed": self._times_unproposed,
            "timesRejected": self._times_rejected
        }
    

class Model(object):
    @staticmethod
    def from_json(json_obj: Any) -> "Model":
        if not isinstance(json_obj, dict):
            raise ValueError("Settings must be a JSON object!")
        
        model = Model(json_obj.get("unproposedFactor", 0.5), json_obj.get("rejectedFactor", 0.2))

        persons = json_obj.get("persons", list())
        if not isinstance(persons, list):
            raise ValueError("Person list must be a JSON array!")
        
        for person in persons:
            if not isinstance(person, dict):
                raise ValueError("Person must be a JSON object!")
            
            if "name" not in person:
                raise ValueError("Person must have a name!")
            
            model.add_person(person["name"], person.get("timesUnproposed", 0), person.get("timesRejected", 0))

        return model

    def __init__(self, unproposed_factor: float, rejected_factor: float):
        self._persons: Dict[str, Person] = dict()
        self._unproposed_factor = max(0.0, unproposed_factor)
        self._rejected_factor = max(0.0, rejected_factor)
    
    def add_person(self, name: str, times_unproposed: int = 0, times_rejected: int = 0):
        self._persons[name] = Person(name, times_unproposed, times_rejected)
    
    def reject_name(self, name: str):
        person: Optional[Person] = self._persons.get(name, None)
        if person is not None:
            person.increase_times_rejected()
    
    def pick_name(self, name: str):
        person: Optional[Person] = self._persons.get(name, None)
        if person is not None:
            person.reset()
    
    def deactivate_name(self, name: str):
        person: Optional[Person] = self._persons.get(name, None)
        if person is not None:
            person.deactivate()
    
    def get_active_names(self) -> Set[str]:
        return { person.name for person in self._persons.values() if person.active }
    
    def get_random_name(self) -> Optional[str]:
        maximum = 0.0
        weights: List[Tuple[float, str]] = list()
        for person in self._persons.values():
            if person.active:
                weights.append((maximum, person.name))
                maximum += 1.0 + person.times_unproposed * self._unproposed_factor \
                        + person.times_rejected * self._rejected_factor
        
        choice = random.random() * maximum

        name: Optional[str] = None
        for weight in weights:
            if weight[0] < choice:
                name = weight[1]
        
        return name

    def propose_name(self) -> Optional[str]:
        name = self.get_random_name()
        
        for person in self._persons.values():
            if person.active and person.name != name:
                person.increase_times_unproposed()

        return name

    def to_json(self) -> Dict[str, Any]:
        return {
            "unproposedFactor": self._unproposed_factor,
            "rejectedFactor": self._rejected_factor,
            "persons": [ person.to_json() for person in self._persons.values() ]
        }


def read_model(path: str) -> Model:
    json_obj = dict()
    try:
        with open(path, "r") as file:
            json_obj = json.load(file)
    except OSError as e:
        print(f"Couldn't open settings: {e}", file=sys.stderr)
        exit(1)
    except json.JSONDecodeError as e:
        print(f"Couldn't deserialize settings: {e}", file=sys.stderr)
        exit(1)
    
    try:
        model = Model.from_json(json_obj)
    except (ValueError, TypeError) as e:
        print(f"Couldn't create model: {e}", file=sys.stderr)
        exit(1)

    return model


def write_model(model: Model, path: str):
    i = 0
    while True:
        tmp_path = f"{path}_{i}"
        if not os.path.exists(tmp_path):
            break

    with open(tmp_path, "w") as file:
        json.dump(model.to_json(), file, indent=4)
    
    os.replace(tmp_path, path)


def do_deactivation(model: Model):
    while True:
        active_names = model.get_active_names()
        if len(active_names) == 0:
            return

        choice = { number + 1: name for (number, name) in enumerate(sorted(active_names)) }

        print("")
        for (number, name) in choice.items():
            print(f"{number}: {name}")
        
        numbers = input("Deactivate (comma-separated list of numbers or empty): ")
        if len(numbers.strip()) == 0:
            return
        
        for number in numbers.split(","):
            try:
                name = choice.get(int(number), None)
            except ValueError:
                print(f"Invalid input: {number.strip()}", file=sys.stderr)
                continue

            if name is not None:
                model.deactivate_name(name)


def do_pick_or_reject(model: Model, path: str):
    while True:
        name = model.propose_name()
        if name is None:
            return
        
        print("")
        answer = input(f"Pick {name} (y/n)? ")

        if answer.strip().lower() == "y":
            model.pick_name(name)
            write_model(model, path)
            return
        else:
            model.reject_name(name)
            write_model(model, path)


def main():
    random.seed()

    path = "settings.json" if len(sys.argv) < 2 else sys.argv[1]

    model = read_model(path)

    print("Person Picker  Copyright (C) 2023  Tobias Heukäufer")
    print("This program comes with ABSOLUTELY NO WARRANTY.")
    print("This is free software, and you are welcome to redistribute it")
    print("under certain conditions.")

    do_deactivation(model)
    do_pick_or_reject(model, path)


if __name__ == "__main__":
    main()
