from __future__ import annotations
from dataclasses import dataclass, field
from math import floor

@dataclass
class StatBlock:
    strength: int
    dexterity: int
    constitution: int
    intelligence: int
    wisdom : int
    charisma: int
    strength_modifier: int = field(init=False)
    dexterity_modifier: int = field(init=False)
    constitution_modifier: int = field(init=False)
    intelligence_modifier: int = field(init=False)
    wisdom_modifier: int = field(init=False)
    charisma_modifier: int = field(init=False)

    def __post_init__(self):
        self.strength_modifier = self.__calculate_modifier(self.strength)
        self.dexterity_modifier = self.__calculate_modifier(self.dexterity)
        self.constitution_modifier = self.__calculate_modifier(self.constitution)
        self.intelligence_modifier = self.__calculate_modifier(self.intelligence)
        self.wisdom_modifier = self.__calculate_modifier(self.wisdom)
        self.charisma_modifier = self.__calculate_modifier(self.charisma)

    def __calculate_modifier(self, value: int) -> int:
        return ((value - 10) // 2)

@dataclass
class BaseEntity:
    name: str
    hit_points: int
    stat_block: StatBlock
    speeds: dict[str, int]
    alignment: str
    ac: int
    natural_armor: bool
    size: str
    languages: list[str]
    passive_perception: int # called passive in json
    damage_resistances: list[str]
    damage_immunities: list[str]
    damage_vulnerabilities: list[str]
    condition_immunities: list[str]
    #proficiency_bonus: int = field(init=False)

@dataclass
class Item:
    name: str
    description: str
    sub_items: list[Item]

    def has_subitems(self) -> bool:
        return (self.sub_items) and (len(self.sub_items) > 0)

@dataclass
class ActionsBlock():
    items: list[Item]

@dataclass
class VariantBlock(Item):
    sub_items: list[Item]

    def has_subitems(self) -> bool:
        return (self.sub_items) and (len(self.sub_items) > 0)

@dataclass
class LairActionsBlock:
    source: str
    description: str
    actions: list[Item] | list[str]

@dataclass
class LairActions:
    source: str
    description: str
    actions: dict

@dataclass
class RegionalEffectsBlock:
    source: str
    description: str
    effects: list[Item | str]

@dataclass
class SpellcastingBlock:
    ability: str

@dataclass
class Monster(BaseEntity):
    primary_source: str
    page: int
    _type: str
    hp_formula: str
    environments: list[str]
    saves: dict[str, int]
    skills: dict[str, int]
    senses: list[str]
    challenge_rating: float
    lair_challenge_rating: float | None
    traits: dict[str, str]
    #spellcasting: SpellcastingBlock
    actions: ActionsBlock | None
    legendary_actions: ActionsBlock | None
    legendary_group_name: str | None
    lair_actions: list[LairActionsBlock] | None
    regional_effects: RegionalEffectsBlock | dict | None
    variant: VariantBlock | dict | None

    #def __post_init__(self):
    #    self.proficiency_bonus = max(floor((self.challenge_rating -1)/4), 0) + 2
