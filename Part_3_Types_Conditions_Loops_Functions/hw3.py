#!/usr/bin/env python

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
OP_SUCCESS_MSG = "Added"

MONTH_PROFIT_PREFIX = "В этом месяце прибыль составила"  # noqa: RUF001
MONTH_LOSS_PREFIX = "В этом месяце убыток составил"  # noqa: RUF001

FEBRUARY = 2
DATE_PARTS_COUNT = 3
DAY_LEN = 2
MONTH_LEN = 2
YEAR_LEN = 4
INCOME_PARTS_COUNT = 3
COST_PARTS_COUNT = 4
STATS_PARTS_COUNT = 2
MAX_MONTH = 12

Types = tuple[float, int, int, int]
IncomsState = list[Types]
CostsState = dict[str, list[Types]]


def output(message: str = "") -> None:
    print(message)


def is_leap_year(year: int) -> bool:
    """
    Для заданного года определяет: високосный (True) или невисокосный (False).

    :param int year: Проверяемый год
    :return: Значение високосности.
    :rtype: bool
    """
    if year % 4 == 0 and year % 100 != 0:
        return True
    if year % 100 == 0:
        return year % 400 == 0
    return False


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    """
    Парсит дату формата DD-MM-YYYY из строки.

    :param str maybe_dt: Проверяемая строка
    :return: tuple формата (день, месяц, год) или None, если дата неправильная.
    :rtype: tuple[int, int, int] | None
    """
    date = maybe_dt.split("-")
    if len(date) != DATE_PARTS_COUNT:
        return None

    day_text, month_text, year_text = date
    if not (day_text.isdigit() and month_text.isdigit() and year_text.isdigit()):
        return None
    if len(day_text) != DAY_LEN or len(month_text) != MONTH_LEN or len(year_text) != YEAR_LEN:
        return None

    day = int(day_text)
    month = int(month_text)
    year = int(year_text)

    if month < 1 or month > MAX_MONTH:
        return None
    in_month = days_in_month(month, year)
    if day < 1 or day > in_month:
        return None

    return day, month, year


def income_handler(amount: float, income_date: str) -> str:
    return f"{OP_SUCCESS_MSG} {amount=} {income_date=}"


def days_in_month(month: int, year: int) -> int:
    if month == FEBRUARY:
        if is_leap_year(year):
            return 29
        return 28
    if month in (1, 3, 5, 7, 8, 10, 12):
        return 31
    return 30


def check_amount(amount: str) -> bool:
    amount = amount.replace(",", ".")

    if amount.count(".") > 1:
        return False
    amount = amount.removeprefix("-")
    if amount == "":
        return False
    if "." not in amount:
        return amount.isdigit()

    left, right = amount.split(".", 1)
    return left.isdigit() and right.isdigit()


def is_valid_category(category: str) -> bool:
    return category != "" and "." not in category and "," not in category


def input_lines() -> list[str]:
    with open(0) as stdin:
        return stdin.readlines()


def income_request(command: list[str], incomes: IncomsState) -> None:
    if len(command) != INCOME_PARTS_COUNT:
        output(UNKNOWN_COMMAND_MSG)
        return

    amount_text = command[1].replace(",", ".")
    if not check_amount(amount_text):
        output(UNKNOWN_COMMAND_MSG)
        return

    amount = float(amount_text)
    if amount <= 0:
        output(NONPOSITIVE_VALUE_MSG)
        return

    date = extract_date(command[2])
    if date is None:
        output(INCORRECT_DATE_MSG)
        return

    incomes.append((amount, date[0], date[1], date[2]))
    output(OP_SUCCESS_MSG)


def cost_request(command: list[str], costs: CostsState) -> None:
    if len(command) != COST_PARTS_COUNT:
        output(UNKNOWN_COMMAND_MSG)
        return

    category = command[1]
    if not is_valid_category(category):
        output(UNKNOWN_COMMAND_MSG)
        return

    amount_text = command[2].replace(",", ".")
    if not check_amount(amount_text):
        output(UNKNOWN_COMMAND_MSG)
        return

    amount = float(amount_text)
    if amount <= 0:
        output(NONPOSITIVE_VALUE_MSG)
        return

    date = extract_date(command[3])
    if date is None:
        output(INCORRECT_DATE_MSG)
        return

    if category not in costs:
        costs[category] = []
    costs[category].append((amount, date[0], date[1], date[2]))
    output(OP_SUCCESS_MSG)


def stats_request(command: list[str], incomes: IncomsState, costs: CostsState) -> None:
    if len(command) != STATS_PARTS_COUNT:
        output(UNKNOWN_COMMAND_MSG)
        return

    date = extract_date(command[1])
    if date is None:
        output(INCORRECT_DATE_MSG)
        return

    all_incomes = incomes_total(date, incomes)
    all_costs = costs_total(date, costs)
    incomes_in_this_month = incomes_in_month(date, incomes)
    costs_in_this_month = costs_in_month(date, costs)
    dict_of_costs = amount_on_categories(date, costs)

    print_stats(
        command[1],
        all_incomes - all_costs,
        incomes_in_this_month,
        costs_in_this_month,
        dict_of_costs,
    )


def print_stats(
    date: str,
    total_capital: float,
    incomes_in_this_month: float,
    costs_in_this_month: float,
    dict_of_costs: dict[str, float],
) -> None:
    output(f"Ваша статистика по состоянию на {date}:")
    output(f"Суммарный капитал: {total_capital:.2f} рублей")
    if incomes_in_this_month >= costs_in_this_month:
        profit = incomes_in_this_month - costs_in_this_month
        output(f"{MONTH_PROFIT_PREFIX} {profit:.2f} рублей")
    else:
        loss = costs_in_this_month - incomes_in_this_month
        output(f"{MONTH_LOSS_PREFIX} {loss:.2f} рублей")
    output(f"Доходы: {incomes_in_this_month:.2f} рублей")
    output(f"Расходы: {costs_in_this_month:.2f} рублей")
    output()
    output("Детализация (категория: сумма):")
    for count, category in enumerate(sorted(dict_of_costs), start=1):
        output(f"{count}. {category}: {change_format(dict_of_costs[category])}")


def change_format(amount: float) -> str:
    if amount.is_integer():
        return str(int(amount))
    return f"{amount:.2f}"


def amount_on_categories(date: tuple[int, int, int], costs: CostsState) -> dict[str, float]:
    dict_of_costs = {}
    for category, operations in costs.items():
        summa_category = 0
        for operation in operations:
            if this_month_or_not(operation[1], operation[2], operation[3], date):
                summa_category += operation[0]
        if summa_category > 0:
            dict_of_costs[category] = summa_category
    return dict_of_costs


def incomes_total(date: tuple[int, int, int], incomes: IncomsState) -> float:
    total = 0
    for operation in incomes:
        if before_date_or_not(operation[1], operation[2], operation[3], date):
            total += operation[0]
    return total


def incomes_in_month(date: tuple[int, int, int], incomes: IncomsState) -> float:
    total = 0
    for operation in incomes:
        if this_month_or_not(operation[1], operation[2], operation[3], date):
            total += operation[0]
    return total


def costs_total(date: tuple[int, int, int], costs: CostsState) -> float:
    total = 0
    for operations in costs.values():
        for operation in operations:
            if before_date_or_not(operation[1], operation[2], operation[3], date):
                total += operation[0]
    return total


def costs_in_month(date: tuple[int, int, int], costs: CostsState) -> float:
    total = 0
    for operations in costs.values():
        for operation in operations:
            if this_month_or_not(operation[1], operation[2], operation[3], date):
                total += operation[0]
    return total


def before_date_or_not(day: int, month: int, year: int, date: tuple[int, int, int]) -> bool:
    return (year, month, day) <= (date[2], date[1], date[0])


def this_month_or_not(day: int, month: int, year: int, date: tuple[int, int, int]) -> bool:
    return year == date[2] and month == date[1] and day <= date[0]


def input_request(request: str, incomes: IncomsState, costs: CostsState) -> None:
    command = request.split()
    if not command:
        output(UNKNOWN_COMMAND_MSG)
        return

    command_name = command[0]

    if command_name == "income":
        income_request(command, incomes)
    elif command_name == "cost":
        cost_request(command, costs)
    elif command_name == "stats":
        stats_request(command, incomes, costs)
    else:
        output(UNKNOWN_COMMAND_MSG)


def main() -> None:
    """Ваш код здесь"""
    incomes: IncomsState = []
    costs: CostsState = {}

    for request in input_lines():
        input_request(request, incomes, costs)


if __name__ == "__main__":
    main()
