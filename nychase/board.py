import enum
from collections import defaultdict
from typing import Dict, List, Set

from PIL import Image, ImageDraw


def read_graph(graph_file: str) -> Dict[int, Set[int]]:
    edges = defaultdict(set)
    with open(graph_file) as fp:
        for line in fp.readlines():
            start, ends = line.split(":")
            edges[int(start)] = set(map(int, ends.split(",")))
    return edges


DATA_ROOT = "data/"
TAXI_GRAPH = read_graph(DATA_ROOT + "taxi.txt")
BUS_GRAPH = read_graph(DATA_ROOT + "bus.txt")
SUBWAY_GRAPH = read_graph(DATA_ROOT + "subway.txt")
BOAT_GRAPH = read_graph(DATA_ROOT + "boat.txt")
MYSTERY_GRAPH = defaultdict(
    set,
    {
        start: TAXI_GRAPH[start]
        .union(BUS_GRAPH[start])
        .union(SUBWAY_GRAPH[start])
        .union(BOAT_GRAPH[start])
        for start in range(1, 200)
    },
)

COORDINATES = {}
with open(DATA_ROOT+"coords.txt") as fp:
    for label, line in enumerate(fp.readlines()):
        x, y = map(int, line.split(","))
        COORDINATES[label+1] = (x, y)

def box(x,y):
	return [(x-50,y-50),(x+50,y+50)]

class Ticket(enum.Enum):
    TAXI = enum.auto()
    BUS = enum.auto()
    SUBWAY = enum.auto()
    MYSTERY = enum.auto()

    def graph(self) -> Dict[int, Set[int]]:
        if self.name == "TAXI":
            return TAXI_GRAPH
        elif self.name == "BUS":
            return BUS_GRAPH
        elif self.name == "SUBWAY":
            return SUBWAY_GRAPH
        elif self.name == "MYSTERY":
            return MYSTERY_GRAPH
        else:
            raise ValueError


class Game:
    def __init__(self, detectives: List[int]):
        self.detectives: List[int] = detectives
        self.barrages: List[int] = []
        self.misterx: Set[int] = set()

    def update_detectives(self, detectives: List[int]) -> None:
        assert len(detectives) == len(self.detectives)
        self.detectives = detectives
        self.misterx.difference_update(self.detectives)

    def update_barrages(self, barrages: List[int]) -> None:
        self.barrages = barrages

    def update_misterx(self, ticket: Ticket) -> None:
        new_possibilities = set()
        graph = ticket.graph()
        for start in self.misterx:
            new_possibilities.update(graph[start])
        new_possibilities.difference_update(self.detectives)
        new_possibilities.difference_update(self.barrages)
        self.misterx = new_possibilities

    def indicate_mister_x(self, label: int) -> None:
        self.misterx = set([label])

    def image(self) -> None:
        img = Image.open(DATA_ROOT+"nychase.jpg").convert("RGBA")
        dot = Image.new("RGBA", img.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(dot)
        for d in self.detectives:
            draw.ellipse(box(*COORDINATES[d]), fill = (0,0,255,128))
        for b in self.barrages:
            draw.ellipse(box(*COORDINATES[b]), fill = (0,255,0,128))
        for x in self.misterx:
            draw.ellipse(box(*COORDINATES[x]), fill = (255,0,0,128))
        out = Image.alpha_composite(img, dot)
        out.save("out.png")






    def __str__(self) -> str:
        return "I can be here: " + ", ".join(map(str, sorted(self.misterx)))


if __name__ == "__main__":
    print("Welcome in the super police computer")
    nb_detective = int(input("Tell us how many policemen you have: "))
    detectives = [int(input(f"Where is detectives {i+1}: ")) for i in range(nb_detective)]
    nb_barrage = int(input("Tell us how many barrages you have: "))
    barrages = [int(input(f"Where is barrage {i+1}: ")) for i in range(nb_barrage)]
    game = Game(detectives)
    game.update_barrages(barrages)
    while True:
        option = input("Chose one option:\n"
              "1) Play mister X round\n"
              "2) Play detectives round\n"
              "3) Reveal mister X\n"
              "4) Update map\n")
        if option == "1":
            while True:
                type_str = input(f"Type of ticket ({', '.join(map(str, Ticket))}): ")
                try:
                    ticket = Ticket[type_str]
                except KeyError:
                    print("Invalid type")
                else:
                    break
            game.update_misterx(ticket)
        elif option == "2":
            detectives = []
            barrages = list(game.barrages)
            for i, detective in enumerate(game.detectives):
                detectives.append(int(input(
                    f"Where is detectives at position {detective} going: ")))
                if input("Want to leave a barrage (yes/no)? ") == "yes":
                    b_to_move = int(input(f"Which one do you want to move {barrages}? "))
                    if b_to_move not in barrages:
                        print("Invalid barrage number!!!!!")
                        break
                    barrages.remove(b_to_move)
                    barrages.append(detective)
            else:
                game.update_detectives(detectives)
                game.update_barrages(barrages)
        elif option == "3":
            game.indicate_mister_x(int(input("Where is Mister X? ")))
        elif option == "4":
            game.image()
        else:
            print("You are stupid")
    game.image()
