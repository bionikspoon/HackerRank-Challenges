from collections import Counter
from fileinput import input


def parse_input(data):
    inventory = Counter(map(int, data[1].split(' ')))
    number_of_customers = int(data[2])
    customers = [map(int, customer.split(' ')) for customer in data[3:3 + number_of_customers]]
    return inventory, customers


def main():
    # get input
    inventory, customers = parse_input([line for line in input()])

    # re run sales history
    revenue = 0

    for size, price in customers:
        if inventory.get(size, 0) <= 0:  # guard, size unavailable
            continue

        revenue += price
        inventory.subtract((size,))

    print(revenue)


if __name__ == '__main__':
    main()
