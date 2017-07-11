# import csv
from datetime import datetime
from difflib import SequenceMatcher


class GetMatchPercentage(object):
    """
    This module compares the traits of the
    lost pet with the scraped results and
    asigns a percentage (0 to 100).
    """
    def __init__(self, lost_pet):
        super(GetMatchPercentage, self).__init__()
        self.lost_pet = lost_pet

    def get_match_percent(self, item):
        """
        Method to assign a match percentage.
        Matching Algorithm:

        Last Seen: 10
        Species: 10
        breed: 20
        color: 30
        gender: 20
        name: 10
        """
        # Criteria for the matching
        criteria = {
            'last_seen': 10,
            'species': 10,
            'breed': 20,
            'color': 30,
            'gender': 20,
            'name': 10,
        }

        # convert last seen date and brought to shelter dates
        # to date object
        last_seen = datetime.strptime(
            self.lost_pet['last_seen'], "%m/%d/%Y")
        brought_to_shelter = datetime.strptime(
            item['brought_to_shelter'], "%Y.%m.%d"
        )

        # If the dates do not match, return matching score as 0
        last_seen_match = 1
        species_match = 1
        if brought_to_shelter < last_seen:
            return 0

        # If the animal species do not match, return matching score as 0
        if self.lost_pet['species'].lower() != item['animal_type']:
            return 0

        # compare the breed
        if self.match(self.lost_pet['breed'], item['breed']):
            breed_match = 1
        else:
            breed_match = self.similar(self.lost_pet['breed'], item['breed'])
        # print("breed_match = {}".format(breed_match))

        # compare the color
        color_match = self.match(
            item['main_color'], self.lost_pet['description'])
        # print("color_match = {}".format(color_match))

        if self.match(self.lost_pet['sex'], item['gender']):
            gender_match = 1
        else:
            gender_match = self.similar(self.lost_pet['sex'], item['gender'])
        # print("gender_match = {}".format(gender_match))

        if self.match(self.lost_pet['name'], item['name']):
            name_match = 1
        else:
            name_match = self.similar(self.lost_pet['name'], item['name'])
        # print("name_match = {}".format(name_match))

        final_score = criteria['last_seen'] * last_seen_match + \
            criteria['species'] * species_match +\
            criteria['breed'] * breed_match + \
            criteria['color'] * color_match +\
            criteria['gender'] * gender_match + criteria['name'] * name_match

        return int(final_score)

    def similar(self, a, b):
        return SequenceMatcher(None, a, b).ratio()

    def match(self, a, b):
        if (
            a.lower() in b.lower() or
            b.lower() in a.lower()
        ):
            return 1
        else:
            return 0

if __name__ == '__main__':
    m = GetMatchPercentage()
    m.process('data.csv')
