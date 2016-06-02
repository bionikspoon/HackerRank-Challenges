from collections import OrderedDict
from fileinput import input


def parse_input(data):
    _ = int(data.pop(0))
    sales = list(map(parse_sale, data))
    return sales


def parse_sale(sale):
    product, price = sale.rsplit(' ', 1)
    return product, int(price)


def create_summary(sales):
    summary = OrderedDict()

    for product, price in sales:
        summary[product] = summary.get(product, 0) + price

    return summary


def main():
    sales = parse_input([line.rstrip() for line in input()])
    summary = create_summary(sales)

    for product, revenue in summary.items():
        print(product, revenue)


if __name__ == '__main__':
    main()
