#!/usr/bin/env python3
import io
import unittest

from sparebank1_homebank import Sparebank1Entry, parse_sparebank1_csv


class TestHomeBankConversion(unittest.TestCase):

    def test_sparebank1(self) -> None:
        input_filecontent = """Dato;Beskrivelse;Rentedato;Inn;Ut;Til konto;Fra konto;
"03.02.2025";"Sense AS";;;"-429,00";;"11122333444";
"27.01.2025";"APPLE.COM/BILL";;;"-129,00";;"11122333444";
"05.02.2025";"Vipps Mottakelse";;"100,00";;"11122333444";"55566777888";
"""
        input_file = io.StringIO(input_filecontent)

        transactions: list[Sparebank1Entry] = parse_sparebank1_csv(input_file)
        transactions_homebank: list[list] = [
            x.to_homebank_record() for x in transactions
        ]

        expected_results = [
            ["03-02-2025", 0, None, "Sense AS", None, -429.0, None, None],
            ["27-01-2025", 0, None, "APPLE.COM/BILL", None, -129, None, None],
            ["05-02-2025", 0, None, "Vipps Mottakelse", None, 100, None, None],
        ]
        self.assertCountEqual(transactions_homebank, expected_results)
