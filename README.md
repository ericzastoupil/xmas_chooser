# 🎄 THE MAGNIFICENT XMAS CHOOSER 🎄
### *Being a True and Faithful Account of the Most Important Computer Program Ever Written (This Household, This Month)*

---

## 📜 HEAR YE, HEAR YE

Gather 'round the glow of the screen, dear family, and behold!

For too long our people have drawn names from a hat. A *hat*. Like *peasants*. Names were peeked at. Slips were "accidentally" put back. Someone drew their own name three times running and had to pretend it was fine. Dark days, my friends. Dark days.

No more.

The **Magnificent Xmas Chooser** is a gleaming engine of holiday justice, forged in the fires of the family laptop. It decides, with cold mathematical precision and a warm festive heart, **who buys a present for whom.** Its rulings are final. Its wisdom is absolute. Its feelings cannot be hurt, so please stop yelling at it.

---

## ✨ WHAT SORCERY IS THIS?

You give the Chooser a list of everyone taking part. It shuffles them like a Vegas card dealer who has had *exactly* the right amount of eggnog, and every person is given **one** lucky recipient to shower with gifts.

Everyone gives exactly one present. Everyone gets exactly one present. Nobody is left out. Nobody gets two. It's beautiful. Somebody fetch a tissue.

---

## ⚖️ THE SACRED LAWS OF THE CHOOSER

The Chooser is bound by ancient and unbreakable rules:

**🚫 LAW THE FIRST: Thou Shalt Not Gift Thyself.**
No one will ever draw their own name. Yes, we know you'd pick something great for yourself. That is precisely the problem.

**💍 LAW THE SECOND: Thou Shalt Not Gift Thy Spouse.**
Married couples already buy each other gifts, and have done so for years, with varying degrees of success. Drawing your own spouse would be like winning a raffle for something you already own. The Chooser keeps husbands and wives apart like a very polite reindeer. Grown-up brothers and sisters, however, are fair game, so start paying attention to what your siblings have been hinting about.

**🧒 LAW THE SECOND-AND-A-HALF: Thou Shalt Not Gift Thy Brother Or Sister (Kids Only).**
In the Kids' Draw, brothers and sisters are kept apart. They already know exactly what the others want, because they've been fighting over it since October. Peace on Earth begins at home. Or at least in the back seat.

**🔁 LAW THE THIRD: Thou Shalt Not Repeat Thyself.**
Did you get Aunt Somebody last year and buy her *that candle*? Fear not! The Chooser **remembers last year** and will *never* hand you the same person two years in a row. Fresh victims. I mean recipients. Fresh recipients.

**⭕ LAW THE FOURTH: The Great Gift Circle Shall Be Unbroken.**
The Chooser does not merely pair people off. Oh no. It seats the entire family around one **magnificent, unbroken Circle of Giving**: you give to the person beside you, who gives to the person beside *them*, and so on, all the way around until the last person gives to the first. One glorious ring of generosity, like a wreath, or a very festive conga line.

This means there will be **no backroom gift swaps.** You will never draw someone who has *also* drawn you, so there's no "I'll get yours, you get mine, let's agree on twenty bucks" collusion. The Chooser sees all. The Chooser forbids it.

**🧮 LAW THE FIFTH: The Chooser Does Not Give Up Easily.**
If the rules are tricky, the Chooser will shuffle and re-shuffle up to **one hundred thousand times** in its quest for the perfect circle. That's more effort than most of us put into wrapping. If even a hundred thousand attempts can't satisfy everyone's rules, it will politely announce that the rules are impossible, rather than spinning forever like a sad, confused Roomba.

---

## 🔐 ON THE MATTER OF SECRECY

The Chooser is fully capable of sending each of you a private email revealing your assignment, so that no one but you and the Chooser ever knows. Nobody else will see it. Not your spouse. Not the dog. Not even the Elf on the Shelf, who frankly has been watching quite enough.

This year, however, the Keeper of the Laptop will simply **look at the screen.** This means the Keeper of the Laptop *knows everything*. Bribes may be submitted in the form of cookies. The Keeper makes no promises, but will accept the cookies.

---

## 📚 THE RECORDS OF THE AGES

Each year's pairings are inscribed into a sacred scroll (a text file, but let us not ruin the moment), safely stored on the Keeper's computer. Next year, the Chooser consults this scroll to avoid repeating itself.

These scrolls, and the list of family members, are **never** posted to the internet. What happens in the family stays in the family. Like the time with the gravy.

---

## ❓ FREQUENTLY ASKED QUESTIONS

**Q: I don't like who I got. Can I trade?**
A: The Chooser has spoken. Take it up with the Chooser. The Chooser is a computer and does not have a phone number.

**Q: Is it *truly* random?**
A: As random as a computer can manage, which is far more random than Uncle Whoever's "totally fair" hat shuffle.

**Q: What if I want to be left out this year?**
A: Tell the Keeper of the Laptop, who will remove you from the list. The Chooser will not take it personally. (The Chooser takes nothing personally. It has no person.)

**Q: Will this program also buy the gift for me?**
A: Regrettably, no. Version 2.0 is under consideration. Funding has not been secured.

**Q: Who made this?**
A: A visionary. A genius. A humble servant of the holidays. You may express your gratitude in baked goods.

---

## 🎁 IN CONCLUSION

May your gifts be thoughtful, your budgets respected, your wrapping paper plentiful, and your recipient *not* the person who's impossible to shop for.

**Merry Christmas from the Magnificent Xmas Chooser!** 🎅

<br>

---
---

<br>

## 🛠️ APPENDIX: INSTRUCTIONS FOR THE KEEPER OF THE LAPTOP
*(Family members may stop reading here. It's all boring from this point on. We promise.)*

### Running it

Print this year's pairings, avoid last year's, and save this year's for next time:

    python3 xmas_chooser.py -p -f adults_participants.jsonl -l adults_pairings_2025.txt -o adults_pairings_2026.txt
    python3 xmas_chooser.py -p -f kids_participants.jsonl -l kids_pairings_2025.txt -o kids_pairings_2026.txt

Leave off `-l` if there's no record of last year. Try it out on the example file:

    python3 xmas_chooser.py -p -f participants.jsonl

### Options

```
usage: xmas chooser [-h] (-p | -e) -f FILE [-l LAST_YEAR] [-o OUTPUT] [-c CONFIG] [-r]

Assigns secret (or not secret) gift pairings

options:
  -h, --help            show this help message and exit
  -p, --print           print assignments to console. not a secret
  -e, --email           email assignments. keeps things a secret. email settings come from the -c
                        file
  -f, --file FILE       participant file (.jsonl): one JSON object per line with name, email,
                        dont_gift (required)
  -l, --last-year LAST_YEAR
                        last year's pairings, in the 'X gets a gift for Y' format that -p prints.
                        those pairings won't be repeated
  -o, --output OUTPUT   save pairings to this file (won't overwrite an existing file). pass it to
                        -l next year
  -c, --config CONFIG   email settings file (default: config.ini). copy config.example.ini to make
                        one
  -r, --real            with -e: email each person their own assignment. without -r, every email
                        goes to the sender's own address as a test
```

A mistyped file name gives a one-line `[-] Can't open ...` message rather than a Python traceback.

### How pairings are made: one gift circle

Everyone is shuffled into a single circle, and each person gives to the next person around it; the last person gives to the first. The shuffle repeats until every giver-to-receiver step obeys the rules (not yourself, nobody on your `dont_gift` list, nobody you had last year), up to 100,000 attempts.

Because it's one circle, no two people ever simply swap gifts with each other (A gives to B and B gives to A), and you can't split into small closed groups. The one exception is a two-person draw, where a swap is unavoidable. Following the printed pairings from any person leads through everyone and back.

A single circle is a slightly stricter requirement than "everyone gets someone valid", but with this family's lists and last year's pairings added, a valid circle turns up within about 50 shuffles on average.

### Participant file (`-f`)

JSON Lines (`.jsonl`): one participant per line. `dont_gift` lists other participants this person must not be assigned. See `participants.jsonl`:

    {"name": "name1", "email": "email1", "dont_gift": ["name2"]}
    {"name": "name2", "email": "email2", "dont_gift": ["name1"]}

The file is checked before any pairings are made. Bad JSON, missing fields, duplicate names, and `dont_gift` names that don't match a participant are all reported together. If the rules make a pairing impossible, the script says so instead of running forever.

### Last year's pairings (`-l`) and saving this year's (`-o`)

The `-l` file has one `X gets a gift for Y` line per pairing, which is exactly what `-o` writes and `-p` prints. Blank lines are ignored. Malformed lines and a giver listed twice are errors. Names not in this year's participant file are skipped with a warning, so people who've dropped out don't cause problems.

`-o` won't overwrite an existing file, and it saves the pairings before printing or emailing them.

### Keeping names out of the repo

Files named `*_participants.jsonl` and `*_pairings_*.txt` are git-ignored, so real participant lists and saved pairings stay out of the repo. So is `config.ini`, which holds the email password.

### Email

1. Copy `config.example.ini` to `config.ini` and fill in the SMTP server, port, sender address and password. (`config.ini` is git-ignored. Use `-c` to point at a different file.)
2. Do a test run. Without `-r`, every email goes to the sender's own address, each with a `[TEST for <name>]` subject, so you can check they look right. (This does show you everyone's pairing.)

       python3 xmas_chooser.py -e -f adults_participants.jsonl

3. Send for real. `-r` emails each person their own assignment, and requires `-o` so the pairings are saved before anything is sent:

       python3 xmas_chooser.py -e -r -f adults_participants.jsonl -l adults_pairings_2025.txt -o adults_pairings_2026.txt

All emails go over one connection. The config file is checked before the shuffle, so a missing file or setting fails straight away. If sending fails partway, the script lists who was and wasn't emailed. **Don't just rerun it**, because that would reshuffle and give people conflicting assignments. The full pairings are in the `-o` file, so tell the remaining people their assignments from there.

### Tests

    python3 -m unittest -v

The tests cover the gift-giving rules, the single circle (no swaps), file checking, last year's pairings, saving with `-o`, and email (with the mail server faked, so nothing is sent).
