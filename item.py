from dataclasses import dataclass

from positions import Knight_Item_Positions


@dataclass
class Item:
    name: str
    priority: int  # A,M,D,H -> 4,3,2,1
    pos: Knight_Item_Positions
    attack: int
    defence: int
