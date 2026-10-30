import csv

count = 0
invalid_band_1 = 0
invalid_band_2 = 0

with open("cleaned_al_si_pixels.csv", newline="") as file:
    reader = csv.DictReader(file)

    for row in reader:
        count += 1

        try:
            float(row["Band_1"])
        except (ValueError, TypeError):
            invalid_band_1 += 1

        try:
            float(row["Band_2"])
        except (ValueError, TypeError):
            invalid_band_2 += 1

print("Total rows:", count)
print("Non-numeric Band_1 values:", invalid_band_1)
print("Non-numeric Band_2 values:", invalid_band_2)