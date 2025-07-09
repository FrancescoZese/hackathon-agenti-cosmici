import json

class GalacticMarketplace:
    def __init__(self, galaxy_state):
        self.marketplace = galaxy_state["marketplace"]
        self.client = galaxy_state["client"]

    def find_item(self, item_name):
        return [ (id_, item) for id_, item in self.marketplace.items() if item_name.lower() in item["name"].lower() ]

    def purchase_item(self, item_id):
        item = self.marketplace.get(item_id)
        if not item:
            return "Item not found."
        price = item["price"]
        if price > self.client["balance"]:
            return "Insufficient balance."
        self.client["balance"] -= price
        self.client["inventory"].append(item)
        return f"Purchased {item['name']} for {price} credits."


class GalaxyNavigator:
    def __init__(self, galaxy_state):
        self.droids = galaxy_state["droids"]
        self.ships = galaxy_state["ships"]
        self.travel_costs = galaxy_state["travel_costs"]
        self.client = galaxy_state["client"]

    def get_droid_location(self, droid_name):
        return self.droids.get(droid_name, {}).get("location")

    def list_available_ships(self, from_planet):
        return {
            name: ship for name, ship in self.ships.items()
            if ship["available"] and ship["location"] == from_planet
        }

    def travel(self, from_planet, to_planet, ship_name):
        key = f"{from_planet}-{to_planet}"
        cost = self.travel_costs.get(key)
        if not cost:
            return "Invalid route."
        if cost > self.client["balance"]:
            return "Not enough credits for travel."
        ship = self.ships.get(ship_name)
        if not ship or not ship["available"] or ship["location"] != from_planet:
            return "Ship not available at the specified location."
        ship["location"] = to_planet
        self.client["balance"] -= cost
        return f"Traveled from {from_planet} to {to_planet} using {ship_name} for {cost} credits."


class InfoSphere:
    def __init__(self, galaxy_state):
        self.infosphere = galaxy_state["infosphere"]

    def get_info(self, name):
        return self.infosphere.get(name, "No data available.")
