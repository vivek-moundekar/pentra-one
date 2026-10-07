from django.core.management.base import BaseCommand
from agriculture.models import Crop


class Command(BaseCommand):

    help = "Add starter crop information for Udaan Agriculture"


    def handle(self, *args, **kwargs):

        crops = [

            {
                "name": "Wheat",
                "scientific_name": "Triticum aestivum",
                "description": (
                    "Wheat is an important food grain crop commonly "
                    "grown during the winter season."
                ),
                "season": "Rabi",
                "soil": (
                    "Well-drained loamy soil with good fertility. "
                    "Avoid waterlogged fields."
                ),
                "water_requirement": (
                    "Moderate irrigation is required. "
                    "Important stages include crown root development, "
                    "flowering and grain filling."
                ),
                "sowing_time": (
                    "Usually October to December, depending on the region."
                ),
                "harvesting_time": (
                    "Usually March to April, depending on the variety "
                    "and growing region."
                ),
            },

            {
                "name": "Rice",
                "scientific_name": "Oryza sativa",
                "description": (
                    "Rice is a major food crop that grows well in warm "
                    "conditions with adequate water."
                ),
                "season": "Kharif",
                "soil": (
                    "Clayey or clay-loam soil with good water-holding capacity "
                    "is generally suitable."
                ),
                "water_requirement": (
                    "Requires regular water availability, especially during "
                    "establishment and reproductive stages."
                ),
                "sowing_time": (
                    "Usually June to July for the main Kharif crop."
                ),
                "harvesting_time": (
                    "Generally September to November depending on variety "
                    "and region."
                ),
            },

            {
                "name": "Cotton",
                "scientific_name": "Gossypium spp.",
                "description": (
                    "Cotton is an important fibre crop grown in warm "
                    "conditions and is widely cultivated in India."
                ),
                "season": "Kharif",
                "soil": (
                    "Deep, fertile and well-drained black soil is generally "
                    "suitable for cotton."
                ),
                "water_requirement": (
                    "Needs adequate moisture but does not perform well "
                    "under prolonged waterlogging."
                ),
                "sowing_time": (
                    "Usually June to July, depending on monsoon conditions."
                ),
                "harvesting_time": (
                    "Usually starts several months after sowing and may "
                    "continue through the dry season."
                ),
            },

            {
                "name": "Soybean",
                "scientific_name": "Glycine max",
                "description": (
                    "Soybean is an important oilseed and pulse crop "
                    "commonly grown during the monsoon season."
                ),
                "season": "Kharif",
                "soil": (
                    "Well-drained fertile soil with good moisture retention "
                    "is suitable."
                ),
                "water_requirement": (
                    "Needs adequate soil moisture, especially during "
                    "flowering and pod development."
                ),
                "sowing_time": (
                    "Usually June to July with the onset of monsoon."
                ),
                "harvesting_time": (
                    "Generally September to October depending on the variety."
                ),
            },

            {
                "name": "Maize",
                "scientific_name": "Zea mays",
                "description": (
                    "Maize is a versatile cereal crop used for food, "
                    "feed and industrial purposes."
                ),
                "season": "Kharif / Rabi / Summer",
                "soil": (
                    "Fertile, well-drained loamy soil with good organic matter "
                    "is generally preferred."
                ),
                "water_requirement": (
                    "Requires regular moisture. Water stress during flowering "
                    "and grain formation can reduce yield."
                ),
                "sowing_time": (
                    "Depends on season and region; commonly June to July "
                    "for Kharif maize."
                ),
                "harvesting_time": (
                    "Usually around 3 to 4 months after sowing, depending "
                    "on variety and purpose."
                ),
            },

            {
                "name": "Chickpea",
                "scientific_name": "Cicer arietinum",
                "description": (
                    "Chickpea is a major pulse crop commonly cultivated "
                    "during the cool dry season."
                ),
                "season": "Rabi",
                "soil": (
                    "Well-drained loam to black soil with moderate fertility "
                    "is generally suitable."
                ),
                "water_requirement": (
                    "Requires limited irrigation. Excess water can be harmful."
                ),
                "sowing_time": (
                    "Usually October to November."
                ),
                "harvesting_time": (
                    "Generally February to March depending on region."
                ),
            },

            {
                "name": "Tomato",
                "scientific_name": "Solanum lycopersicum",
                "description": (
                    "Tomato is a widely grown vegetable crop used fresh "
                    "and in processed food products."
                ),
                "season": "Rabi / Kharif / Summer",
                "soil": (
                    "Well-drained fertile sandy loam to loam soil with "
                    "good organic matter is suitable."
                ),
                "water_requirement": (
                    "Needs regular and balanced irrigation. Avoid sudden "
                    "changes in soil moisture."
                ),
                "sowing_time": (
                    "Varies by region and season."
                ),
                "harvesting_time": (
                    "Fruits are harvested when they reach the required "
                    "stage of maturity."
                ),
            },

            {
                "name": "Onion",
                "scientific_name": "Allium cepa",
                "description": (
                    "Onion is an important vegetable and commercial crop "
                    "grown in several parts of India."
                ),
                "season": "Rabi / Kharif",
                "soil": (
                    "Loose, fertile and well-drained soil is preferred."
                ),
                "water_requirement": (
                    "Requires regular but controlled irrigation. "
                    "Stop irrigation before harvest as appropriate."
                ),
                "sowing_time": (
                    "Varies according to Kharif, late Kharif and Rabi seasons."
                ),
                "harvesting_time": (
                    "Harvest when bulbs mature and the tops begin to fall."
                ),
            },

            {
                "name": "Sugarcane",
                "scientific_name": "Saccharum officinarum",
                "description": (
                    "Sugarcane is a long-duration commercial crop used "
                    "mainly for sugar production."
                ),
                "season": "Annual / Seasonal",
                "soil": (
                    "Deep fertile loamy soil with good drainage and "
                    "water-holding capacity is suitable."
                ),
                "water_requirement": (
                    "Requires substantial water throughout the growing "
                    "period, with irrigation adjusted to weather and soil."
                ),
                "sowing_time": (
                    "Varies by region and planting season."
                ),
                "harvesting_time": (
                    "Usually harvested after the crop reaches suitable "
                    "maturity, often around 10 to 18 months depending on region."
                ),
            },

            {
                "name": "Groundnut",
                "scientific_name": "Arachis hypogaea",
                "description": (
                    "Groundnut is an important oilseed crop that grows "
                    "well in warm conditions."
                ),
                "season": "Kharif / Summer",
                "soil": (
                    "Loose, well-drained sandy loam to loam soil is ideal "
                    "because pods develop underground."
                ),
                "water_requirement": (
                    "Needs adequate moisture during establishment, flowering "
                    "and pod development while avoiding waterlogging."
                ),
                "sowing_time": (
                    "Usually June to July for Kharif cultivation."
                ),
                "harvesting_time": (
                    "Generally harvested when pods are mature and the "
                    "inner shell develops properly."
                ),
            },

        ]


        created_count = 0
        updated_count = 0


        for data in crops:

            crop, created = Crop.objects.update_or_create(
                name=data["name"],
                defaults={
                    "scientific_name": data["scientific_name"],
                    "description": data["description"],
                    "season": data["season"],
                    "soil": data["soil"],
                    "water_requirement": data["water_requirement"],
                    "sowing_time": data["sowing_time"],
                    "harvesting_time": data["harvesting_time"],
                    "is_active": True,
                }
            )


            if created:

                created_count += 1

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Added: {crop.name}"
                    )
                )

            else:

                updated_count += 1

                self.stdout.write(
                    self.style.WARNING(
                        f"Updated: {crop.name}"
                    )
                )


        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"Done! Added {created_count} crops "
                f"and updated {updated_count} crops."
            )
        )