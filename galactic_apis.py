import json

class GalacticMarketplace:
    def __init__(self, galaxy_state):
        self.__marketplace = galaxy_state["marketplace"]
        self.__client = galaxy_state["client"]

    def find_item(self, item_name):
        return [ (id_, item) for id_, item in self.__marketplace.items() if item_name.lower() in item["name"].lower() ]

    def purchase_item(self, item_id):
        item = self.__marketplace.get(item_id)
        if not item:
            return "Item not found."
        price = item["price"]
        if price > self.__client["balance"]:
            return "Insufficient balance."
        self.__client["balance"] -= price
        self.__client["inventory"].append(item["name"])
        return f"Purchased {item['name']} for {price} credits."

class GalaxyNavigator:
    """
    Gestisce la navigazione di droidi e navi. Ogni viaggio sposta sia la nave che il droide specificato.
    """
    def __init__(self, galaxy_state):
        self.__droids = galaxy_state["droids"]
        self.__ships = galaxy_state["ships"]
        self.__travel_costs = galaxy_state["travel_costs"]
        self.__client = galaxy_state["client"]

    def get_droid_location(self, droid_name):
        return self.__droids.get(droid_name, {}).get("location")

    def list_available_ships(self, from_planet):
        return {
            name: ship for name, ship in self.__ships.items()
            if ship["available"] and ship["location"] == from_planet
        }

    def travel(self, droid_name, to_planet, ship_name):
        """
        Sposta il droide specificato e la nave scelta verso il pianeta di destinazione, se possibile.
        Scala i crediti dal client. Aggiorna la posizione sia della nave che del droide.
        """
        # Verifica esistenza droide e nave
        droid = self.__droids.get(droid_name)
        ship = self.__ships.get(ship_name)
        if not droid:
            return f"Droid {droid_name} not found."
        if not ship:
            return f"Ship {ship_name} not found."
        from_planet = droid["location"]
        if ship["location"] != from_planet or not ship["available"]:
            return f"Ship {ship_name} is not available at {from_planet}."
        key = f"{from_planet}-{to_planet}"
        cost = self.__travel_costs.get(key)
        if not cost:
            return "Invalid route."
        if cost > self.__client["balance"]:
            return "Not enough credits for travel."
        # Aggiorna posizioni
        ship["location"] = to_planet
        droid["location"] = to_planet
        self.__client["balance"] -= cost
        return f"{droid_name} e la nave {ship_name} sono stati spostati da {from_planet} a {to_planet} per {cost} crediti."

class InfoSphere:
    def __init__(self, galaxy_state):
        self.__infosphere = galaxy_state["infosphere"]

    def get_info(self, name):
        return self.__infosphere.get(name, "No data available.")
