from dataclasses import dataclass


@dataclass
class Participant:
    name: str
    email: str
    dont_gift: list[str]
