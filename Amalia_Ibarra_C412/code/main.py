import sys
from distributions import exp, normal, uniform


def get_boat():
    x = uniform()
    if x <= 0.25:
        return "small"
    if x <= 0.5:
        return "medium"

    return "large"


def get_loading_time(boat):
    if boat == "small":
        return normal(9, 1)

    if boat == "medium":
        return normal(12, 2)

    return normal(18, 3)


def get_dock(docks):
    if docks[0] is None:
        return 0
    if docks[1] is None:
        return 1
    if docks[2] is None:
        return 2

    return None


class Harbor:
    def __init__(self):
        self.queue = []
        self.docks = [None] * 3
        self.trailer = None
        self.trailer_in_port = True


class Simulation:
    def __init__(self):
        self.time = 0
        self.max_time = 24
        self.harbor = Harbor()
        self.t0 = exp(8)
        self.arrival_time = self.t0
        self.departures_queue = []
        self.dock_departures = [sys.maxsize] * 3
        self.move_to_dock_time = sys.maxsize
        self.start_loading_time = [sys.maxsize] * 3
        self.ship_arrivals = {}
        self.ship_departures = {}
        self.shipCount = 0
        self.ship_leaving_port_time = sys.maxsize

    def get_loaded_ship(self):
        _min = min(self.dock_departures)
        index = self.dock_departures.index(_min)
        return self.harbor.docks[index], index

    def get_min_event_time(self):
        return min(
            [
                self.arrival_time,
                min(self.dock_departures),
                self.move_to_dock_time,
                min(self.start_loading_time),
                self.ship_leaving_port_time,
            ]
        )

    def are_boats_left(self):
        return len(self.ship_arrivals) > len(self.ship_departures)

    def run(self):
        while self.time <= self.max_time or self.are_boats_left():

            # ---evento de arribo---
            if self.arrival_time == self.get_min_event_time():

                if self.arrival_time < self.max_time:
                    self.time = self.arrival_time
                    self.shipCount += 1
                    print("SHIP", self.shipCount, "ARRIVED")

                    self.ship_arrivals[self.shipCount] = self.time

                    boat = get_boat()
                    loading_time = get_loading_time(boat)
                    self.harbor.queue.append((self.shipCount, loading_time))

                    # ---generar nuevo arribo---
                t0 = exp(1 / 8)
                self.arrival_time = self.time + t0

                if self.harbor.trailer is None:
                    print("FREE TRAILER AT ARRIVAL")
                    free_dock = get_dock(self.harbor.docks)
                    print("DOCK", free_dock, "IS FREE")
                    if free_dock is not None and len(self.harbor.queue) > 0:
                        ship, _ = self.harbor.queue.pop(0)
                        self.harbor.trailer = (ship, loading_time, free_dock)
                        if self.harbor.trailer_in_port:
                            self.move_to_dock_time = self.time
                        else:
                            self.move_to_dock_time = self.time + exp(4)

            # ---llevar del puerto al muelle
            elif self.move_to_dock_time == self.get_min_event_time():
                self.time = self.move_to_dock_time
                self.harbor.trailer_in_port = False
                ship, _, free_dock = self.harbor.trailer
                self.harbor.docks[free_dock] = ship
                self.start_loading_time[free_dock] = self.time + exp(1 / 2)
                self.move_to_dock_time = sys.maxsize
                print("---Ship", ship, "going to dock", free_dock)

            # ---empezar a cargar---
            elif min(self.start_loading_time) == self.get_min_event_time():
                self.time = min(self.start_loading_time)
                ship, loading_time, dock = self.harbor.trailer
                print("LOADING Ship", ship)
                self.dock_departures[dock] = self.time + loading_time
                self.start_loading_time[dock] = sys.maxsize
                self.move_to_dock_time = sys.maxsize
                self.ship_leaving_port_time = sys.maxsize
                self.harbor.trailer = None
                self.harbor.docks[dock] = ship

                if len(self.departures_queue) > 0:
                    ship, dock = self.departures_queue.pop(0)
                    print("---TAKING SHIP", ship, "to port")
                    self.harbor.trailer = (ship, None, None)
                    self.ship_leaving_port_time = self.time + exp(1)

            # ---termino de cargar---
            elif min(self.dock_departures) == self.get_min_event_time():
                self.time = min(self.dock_departures)
                ship, dock = self.get_loaded_ship()
                print("---SHIP", ship, "finished loading in dock", dock)

                if self.harbor.trailer is None:
                    print("Trailer is free")
                    if not self.harbor.trailer_in_port:
                        self.ship_leaving_port_time = self.time + exp(1)

                    else:
                        self.ship_leaving_port_time = self.time + exp(1) + exp(4)

                    self.harbor.trailer = (ship, None, None)
                    self.dock_departures[dock] = sys.maxsize
                    self.harbor.docks[dock] = None
                else:
                    print("ADDING SHIP TO DEPARTURES QUEUE")
                    self.departures_queue.append((ship, dock))

                self.dock_departures[dock] = sys.maxsize
                self.harbor.docks[dock] = None

            # ---el barco se va del puerto---
            elif self.ship_leaving_port_time == self.get_min_event_time():
                self.time = self.ship_leaving_port_time
                self.ship_leaving_port_time = sys.maxsize
                ship, _, _ = self.harbor.trailer
                print("SHIP", ship, "is leaving port")
                self.ship_departures[ship] = self.time
                self.harbor.trailer_in_port = True
                self.harbor.trailer = None

                free_dock = get_dock(self.harbor.docks)
                # print("DOCK", free_dock, "IS FREE AFTER LEAVING")
                if free_dock is not None and len(self.harbor.queue) > 0:
                    ship, loading_time = self.harbor.queue.pop(0)
                    self.harbor.trailer = (ship, loading_time, free_dock)
                    self.move_to_dock_time = self.time
                    self.harbor.docks[free_dock] = ship

                elif len(self.departures_queue) > 0 and self.harbor.trailer is None:
                    ship, dock = self.departures_queue.pop(0)
                    print("PICKING UP SHIP", ship, "FROM DEPARTURES QUEUE")

                    self.harbor.trailer = (ship, None, None)
                    if not self.harbor.trailer_in_port:
                        self.ship_leaving_port_time = self.time + exp(1)

                    else:
                        self.ship_leaving_port_time = self.time + exp(1) + exp(4)

        times = []
        for ship in self.ship_arrivals.keys():
            times.append(self.ship_departures[ship] - self.ship_arrivals[ship])
        solve = sum(times) / len(times)
        return solve


def main():
    s = Simulation()
    solve = s.run()

    print("-------------------------------------")
    print("AVERAGE: ", solve)
    print("-------------------------------------")


if __name__ == "__main__":
    main()

