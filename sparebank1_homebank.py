#!/usr/bin/env python3
import argparse
import csv
import datetime
import pathlib
from dataclasses import dataclass
from typing import IO, Optional


@dataclass
class Sparebank1Entry:
    date: datetime.date
    description: str
    rent_date: datetime.date
    amount: float
    account_to: str
    account_from: str

    @staticmethod
    def from_csv(record: list):
        # correct dates
        record[0] = Sparebank1Entry._sanitize_date(record[0])
        record[2] = Sparebank1Entry._sanitize_date(record[2])

        # Sparebank1 lists "in" and "out" values as two seperate columns, but
        # we just want to know the +/- for the current account.
        amount_in = record[3]
        amount_out = record[4]
        amount = amount_out if amount_out != "" else amount_in

        return Sparebank1Entry(
            date=record[0],
            description=record[1],
            rent_date=record[2],
            amount=float(amount.replace(",", ".")),
            account_to=record[5],
            account_from=record[6],
        )

    @staticmethod
    def _sanitize_date(date: str) -> Optional[datetime.date]:
        if date == "":
            return None
        return datetime.datetime.strptime(date, "%d.%m.%Y")

    def to_homebank_record(self) -> list:
        date = self.date.strftime("%d-%m-%Y")
        return [date, 0, None, self.description, None, self.amount, None, None]


def parse_sparebank1_csv(file: IO[str]) -> list[Sparebank1Entry]:
    output: list[Sparebank1Entry] = []
    file.readline()  # skip parsing header line
    csv_reader = csv.reader(file, delimiter=";")
    for record in csv_reader:
        output.append(Sparebank1Entry.from_csv(record))
    return output


def generate_homebank_csv(sparebank1_csv_path: pathlib.Path) -> None:
    with sparebank1_csv_path.open(encoding="UTF-8") as file:
        transaction_entries: list[Sparebank1Entry] = parse_sparebank1_csv(file)

    destination = pathlib.Path(f"{sparebank1_csv_path.parent}/{sparebank1_csv_path.stem}_homebank.csv")
    with destination.open("w", newline="", encoding="UTF-8") as file:
        csv_writer = csv.writer(file, delimiter=";")
        for transaction in transaction_entries:
            csv_writer.writerow(transaction.to_homebank_record())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Sparebank1HomeBankConverter",
        description="Converts exported Sparebank1 transaction histories (CSV),"
        " to a HomeBank-friendly CSV format.",
    )
    parser.add_argument(
        "input", type=pathlib.Path, help="The Sparebank1 CSV file to convert."
    )
    args = parser.parse_args()

    if not args.input.exists():
        raise FileNotFoundError("Input CSV file not found.")
    generate_homebank_csv(args.input.absolute())
