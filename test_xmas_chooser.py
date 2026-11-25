"""Tests for xmas_chooser. Run with: python3 -m unittest -v"""

import os
import smtplib
import tempfile
import unittest
from unittest import mock

import xmas_chooser
from participant import Participant


def make_people():
    #Two couples and two singles
    return [
        Participant("A", "a@x", ["B"]),
        Participant("B", "b@x", ["A"]),
        Participant("C", "c@x", ["D"]),
        Participant("D", "d@x", ["C"]),
        Participant("E", "e@x", []),
        Participant("F", "f@x", []),
    ]


def write_temp(test, text, suffix=".txt"):
    fd, path = tempfile.mkstemp(suffix=suffix)
    with os.fdopen(fd, "w") as f:
        f.write(text)
    test.addCleanup(os.remove, path)
    return path


class CreateAssignmentsTests(unittest.TestCase):
    RUNS = 300

    def test_rules_respected(self):
        people = make_people()
        for _ in range(self.RUNS):
            receivers = xmas_chooser.create_assignments(people)
            for giver, receiver in zip(people, receivers):
                self.assertNotEqual(giver.name, receiver.name)
                self.assertNotIn(receiver.name, giver.dont_gift)

    def test_everyone_gives_and_receives_once(self):
        people = make_people()
        for _ in range(self.RUNS):
            receivers = xmas_chooser.create_assignments(people)
            self.assertEqual(sorted(r.name for r in receivers), sorted(p.name for p in people))

    def test_single_circle_and_no_mutual_pairs(self):
        people = make_people()
        for _ in range(self.RUNS):
            receivers = xmas_chooser.create_assignments(people)
            gives_to = {g.name: r.name for g, r in zip(people, receivers)}

            #Following the chain from anyone visits everyone before returning
            seen, current = [], "A"
            while current not in seen:
                seen.append(current)
                current = gives_to[current]
            self.assertEqual(len(seen), len(people))

            for giver, receiver in gives_to.items():
                self.assertNotEqual(gives_to[receiver], giver, f"{giver} and {receiver} swap gifts")

    def test_impossible_rules_raise(self):
        people = [Participant("A", "", ["B"]), Participant("B", "", ["A"])]
        with mock.patch.object(xmas_chooser, "MAX_ATTEMPTS", 50):
            with self.assertRaises(RuntimeError):
                xmas_chooser.create_assignments(people)


class CreateListTests(unittest.TestCase):
    def test_valid_file_with_blank_lines(self):
        path = write_temp(self, '{"name": "A", "email": "a", "dont_gift": ["B"]}\n\n'
                                '{"name": "B", "email": "b", "dont_gift": []}\n', ".jsonl")
        people = xmas_chooser.create_list(path)
        self.assertEqual([p.name for p in people], ["A", "B"])

    def test_all_problems_reported(self):
        path = write_temp(self, '{"name": "A", "email": "a", "dont_gift": ["Typo"]}\n'
                                '{"name": "B", "email": "b"}\n'
                                '{"name": "C", "email": "c", "dont_gift": "A"}\n'
                                '{"name": "A", "email": "a2", "dont_gift": []}\n'
                                '{not json}\n', ".jsonl")
        with self.assertRaises(ValueError) as ctx:
            xmas_chooser.create_list(path)
        message = str(ctx.exception)
        for expected in ("line 2: missing dont_gift", "line 3: dont_gift must be a list",
                         "line 5: invalid JSON", "duplicate name: A", "unknown name: 'Typo'"):
            self.assertIn(expected, message)


class LastYearTests(unittest.TestCase):
    def test_last_year_added_to_dont_gift(self):
        people = make_people()
        path = write_temp(self, "A gets a gift for C\n\nE gets a gift for F\n")
        xmas_chooser.apply_last_year(path, people)
        self.assertIn("C", people[0].dont_gift)
        self.assertIn("F", people[4].dont_gift)

    def test_never_repeats_last_year(self):
        people = make_people()
        last = xmas_chooser.create_assignments(people)
        path = write_temp(self, "".join(xmas_chooser.format_pairing(g, r) + "\n" for g, r in zip(people, last)))
        xmas_chooser.apply_last_year(path, people)
        last_pairs = {(g.name, r.name) for g, r in zip(people, last)}
        for _ in range(200):
            now = xmas_chooser.create_assignments(people)
            self.assertFalse(last_pairs & {(g.name, r.name) for g, r in zip(people, now)})

    def test_unknown_names_ignored(self):
        people = make_people()
        path = write_temp(self, "Grandpa gets a gift for A\nA gets a gift for Grandma\n")
        with mock.patch("sys.stderr"):
            xmas_chooser.apply_last_year(path, people)
        self.assertEqual(people[0].dont_gift, ["B"])

    def test_bad_lines_raise(self):
        path = write_temp(self, "A gets a gift for C\nA gets a gift for D\nnonsense\n")
        with self.assertRaises(ValueError) as ctx:
            xmas_chooser.apply_last_year(path, make_people())
        self.assertIn("more than once", str(ctx.exception))
        self.assertIn("nonsense", str(ctx.exception))


class SaveResultsTests(unittest.TestCase):
    def test_round_trip_and_no_overwrite(self):
        people = make_people()
        receivers = xmas_chooser.create_assignments(people)
        path = os.path.join(tempfile.mkdtemp(), "pairings.txt")
        self.addCleanup(os.remove, path)

        with mock.patch("sys.stderr"):
            xmas_chooser.save_results(path, people, receivers)
            with self.assertRaises(FileExistsError):
                xmas_chooser.save_results(path, people, receivers)

        #The saved file can be read back as last year's pairings
        fresh = make_people()
        xmas_chooser.apply_last_year(path, fresh)
        for giver, receiver in zip(fresh, receivers):
            self.assertIn(receiver.name, giver.dont_gift)


class EmailTests(unittest.TestCase):
    SETTINGS = {"port": 465, "server": "smtp.example.com", "sender": "santa@example.com", "password": "pw"}

    def send(self, real, smtp):
        people = make_people()[:2]
        receivers = list(reversed(people))
        with mock.patch("smtplib.SMTP_SSL", return_value=smtp), mock.patch("builtins.print"):
            xmas_chooser.email_results(self.SETTINGS, people, receivers, real)
        return [c.args[0] for c in smtp.__enter__.return_value.send_message.call_args_list]

    def make_smtp(self):
        #The object used inside 'with smtplib.SMTP_SSL(...) as s' is smtp.__enter__.return_value
        return mock.MagicMock()

    def test_message_headers_and_body(self):
        giver, receiver = make_people()[:2]
        msg = xmas_chooser.build_message("santa@example.com", "a@x", giver, receiver, real=True)
        self.assertEqual(msg["Subject"], "Your secret santa selection")
        self.assertEqual(msg["From"], "santa@example.com")
        self.assertEqual(msg["To"], "a@x")
        self.assertIn("You will give a gift to B", msg.get_content())

    def test_real_mode_emails_each_giver_with_one_login(self):
        smtp = self.make_smtp()
        messages = self.send(True, smtp)
        self.assertEqual([m["To"] for m in messages], ["a@x", "b@x"])
        smtp.__enter__.return_value.login.assert_called_once()

    def test_test_mode_emails_sender_only(self):
        messages = self.send(False, self.make_smtp())
        self.assertEqual([m["To"] for m in messages], ["santa@example.com"] * 2)
        self.assertTrue(all(m["Subject"].startswith("[TEST for ") for m in messages))

    def test_failure_reports_who_was_sent(self):
        smtp = self.make_smtp()
        smtp.__enter__.return_value.send_message.side_effect = [None, smtplib.SMTPException("boom")]
        with self.assertRaises(RuntimeError) as ctx:
            self.send(True, smtp)
        self.assertIn("Sent: A", str(ctx.exception))
        self.assertIn("Not sent: B", str(ctx.exception))

    def test_config_problems(self):
        with self.assertRaises(ValueError):
            xmas_chooser.load_email_config("/nonexistent/config.ini")
        path = write_temp(self, "[DEFAULT]\nSSL_PORT = 465\n", ".ini")
        with self.assertRaises(ValueError) as ctx:
            xmas_chooser.load_email_config(path)
        self.assertIn("SMTP_SERVER", str(ctx.exception))

    def test_example_config_loads(self):
        here = os.path.dirname(os.path.abspath(__file__))
        settings = xmas_chooser.load_email_config(os.path.join(here, "config.example.ini"))
        self.assertEqual(settings["port"], 465)


class CommandLineTests(unittest.TestCase):
    def test_real_email_requires_output(self):
        with mock.patch("sys.stderr"), self.assertRaises(SystemExit):
            xmas_chooser.parse_command_line(["-e", "-r", "-f", "x.jsonl"])

    def test_missing_file_gives_clean_error(self):
        with self.assertRaises(SystemExit) as ctx:
            xmas_chooser.main(["-p", "-f", "/nonexistent/people.jsonl"])
        self.assertIn("[-] Can't open /nonexistent/people.jsonl", str(ctx.exception.code))


if __name__ == "__main__":
    unittest.main()
