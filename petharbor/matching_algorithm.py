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
            'last_seen': 0,
            'species': 0,
            'breed': 30,
            'color': 20,
            'gender': 35,
            'age': 10,
            'name': 5,
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
        breed_match = self.match(
            self.lost_pet['breed'], item['breed'], breed=True)

        # compare the color
        main_color = self.get_transformed_color(item['main_color'])
        color_match = self.match(
            main_color, self.lost_pet['primary_color'], color=True)

        # compare the gender
        gender_match = self.match(
            self.lost_pet['sex'], item['gender'], gender=True)

        # compare the pet name
        if self.match(self.lost_pet['name'], item['name']):
            name_match = 1
        else:
            name_match = self.similar(self.lost_pet['name'], item['name'])

        # compare the pet age
        age_match = self.match_age(self.lost_pet['age'], item['age'])

        # calculate the final score
        final_score = criteria['last_seen'] * last_seen_match + \
            criteria['species'] * species_match +\
            criteria['breed'] * breed_match + \
            criteria['color'] * color_match +\
            criteria['gender'] * gender_match +\
            criteria['name'] * name_match +\
            criteria['age'] * age_match

        return int(final_score)

    def similar(self, a, b):
        return SequenceMatcher(None, a, b).ratio()

    def match(self, a, b, gender=False, breed=False, color=False):
        if gender:
            # special case of gender
            if 'female' in a.lower() and 'female' in b.lower():
                return 1
            elif (
                'male' in a.lower() and 'female' not in a.lower() and
                'male' in b.lower() and 'female' not in b.lower()
            ):
                return 1
            elif 'male' in a.lower() and 'female' in b.lower():
                return 0
            elif 'female' in a.lower() and 'male' in b.lower():
                return 0
            else:
                # unknown gender
                return 0.8
        if breed:
            a = a.lower().replace(" ", "")
            b = b.lower().replace(" ", "")
            if a == b:
                return 1
            elif a in b or b in a:
                return 1
            else:
                return 0
        if color:
            # match each words in color
            color_score = 0
            colors = a.split(' ')
            for c in colors:
                if c.lower() in b.lower():
                    color_score += 1.0 / len(colors)
            return color_score
        if (
            a.lower() in b.lower() or
            b.lower() in a.lower()
        ):
            return 1
        else:
            return 0

    def match_age(self, pet_age, pharbor_age):
        """
        Fuzzy logic to match age
        """
        if pet_age.lower() == 'less than 1 year':
            pet_age = 0
        elif pet_age.lower() == '+10 Years':
            pet_age = 10
        else:
            try:
                pet_age = int(pet_age)
            except:
                pet_age = -1

        # parse age from pet harbor to integers
        try:
            pharbor_age = int(pharbor_age.replace("Years", "").strip())
        except:
            pharbor_age = -1

        if pet_age == -1 and pharbor_age == -1:
            return 0.8
        elif pet_age == -1:
            return 0.8
        elif pharbor_age == -1:
            return 0.8
        elif pet_age == pharbor_age:
            return 1
        else:
            difference = abs(pet_age - pharbor_age)
            score = 0.6 / (difference + 1) + 1.0 / (difference + 1)
            return score

    def get_transformed_color(self, main_color):
        main_color = main_color.lower()
        main_color = main_color.replace('org', 'orange')
        main_color = main_color.replace('brn', 'brown')
        return main_color

if __name__ == '__main__':
    m = GetMatchPercentage('')
    # per = m.match('Male', "Gender Unknown", gender=True)
    # print(per)
    # print(m.match('Domestic Short Hair', 'Domestic Shorthair', breed=True))
    # main_color = m.get_transformed_color('Brn Tabby')
    # print(main_color)
    # print(m.match(main_color, 'Effy is a brown cat', color=True))
    print(m.match_age('sfd', 'Age Unknown'))
