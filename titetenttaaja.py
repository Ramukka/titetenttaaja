import json
import os
import random

# Värikoodit
RED = "\033[91m"
GREEN = "\033[32m"
YELLOW = "\033[93m"
RESET = "\033[0m"


TENTTIKANSIO = "tentit"

try:
    from rich.align import Align
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
except ImportError:  # Rich ei ole pakollinen, pidetään taaksepäin yhteensopivuus
    Align = None
    Console = None
    Panel = None
    Table = None
    Text = None

console = Console() if Console else None
RICH_AVAILABLE = console is not None


def get_panel_width():
    if not console:
        return None
    usable = console.width - 4
    return max(40, usable)


def render_progress(answered, total, score, bar_length=50):
    ratio = answered / total if total else 0
    filled = int(bar_length * ratio)
    filled_part = "|" * filled
    empty_part = "." * (bar_length - filled)

    bar = "["
    if filled_part:
        bar += f"{GREEN}{filled_part}{RESET}"
    if empty_part:
        bar += f"{RED}{empty_part}{RESET}"
    bar += "]"

    if console:
        rich_filled = f"[green]{filled_part}[/]" if filled_part else ""
        rich_empty = f"[red]{empty_part}[/]" if empty_part else ""
        bar = f"[bold][{rich_filled}{rich_empty}][/]"

    percent = int(ratio * 100)
    return f"{bar} {percent:>3}% suoritettu\n{score}/{total} oikein"


def print_progress(answered, total, score):
    progress_text = render_progress(answered, total, score)
    if console and Panel and Text:
        width = get_panel_width()
        text = Text.from_markup(progress_text)
        text.justify = "center"
        aligned = Align.left(text, width=width)
        console.print(aligned)
    else:
        print(progress_text)


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


# Etsii tenttikansiosta json-tiedostot.
def hae_tentit():
    return [f for f in os.listdir(TENTTIKANSIO) if f.endswith(".json")]


# Lukee kysymykset jsonista
def lue_kysymykset(tiedosto):
    with open(os.path.join(TENTTIKANSIO, tiedosto), "r", encoding="utf-8") as f:
        data = json.load(f)

    otsikko = hae_tenttiotsikko(data)
    if isinstance(data, list):
        return data, otsikko
    if isinstance(data, dict):
        questions = data.get("questions")
        if isinstance(questions, list):
            return questions, otsikko
    return [], otsikko


def hae_tenttiotsikko(lahde):
    if isinstance(lahde, str):
        polku = os.path.join(TENTTIKANSIO, lahde)
        try:
            with open(polku, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError):
            return None
    else:
        data = lahde

    def _etsi_title(obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key.upper() == "TITLE" and isinstance(value, str):
                    otsikko = value.strip()
                    if otsikko:
                        return otsikko
            for value in obj.values():
                loytynyt = _etsi_title(value)
                if loytynyt:
                    return loytynyt
        elif isinstance(obj, list):
            for item in obj:
                loytynyt = _etsi_title(item)
                if loytynyt:
                    return loytynyt
        return None

    return _etsi_title(data)


# Tentin suoritus
def suorita_tentti(questions, otsikko=None):
    valid_questions = []
    invalid_questions = []

    for q in questions:
        options = list(q.get("options", []))
        correct = q.get("correct")
        if not options or correct not in options:
            invalid_questions.append(q.get("question", "(tuntematon kysymys)"))
            continue
        valid_questions.append(
            {
                "question": q["question"],
                "options": options,
                "correct": correct,
            }
        )

    if invalid_questions:
        print(f"{YELLOW}Huom: seuraavilta kysymyksiltä puuttui kelvollinen oikea vastaus:{RESET}")
        for name in invalid_questions:
            print(f"- {name}")

    if not valid_questions:
        print(f"{RED}Tentistä puuttuu kelvollisia kysymyksiä.{RESET}")
        return

    while True:
        try:
            question_amount = int(
                input(
                    f"Montako kysymystä kysytään? (kysymyksiä yht. {len(valid_questions)}): "
                )
            )
            if 1 <= question_amount <= len(valid_questions):
                break
            print(f"{RED}Annettu numero ei ole kysymysten määrän sisällä.{RESET}")
        except ValueError:
            print(f"{RED}Syöte ei ollut numero.{RESET}")

    quiz_questions = random.sample(valid_questions, k=question_amount)

    score = 0
    perus_otsikko = "TiTentti"
    naytettava_otsikko = f"{perus_otsikko} : {otsikko}" if otsikko else perus_otsikko
    answered = 0
    user_answers = []

    for index, q in enumerate(quiz_questions, 1):
        clear_screen()
        panel_width = get_panel_width()
        if console and Text:
            header = Text.assemble(
                (naytettava_otsikko, "bold cyan"),
                ("    "),
                (f"Kysymys {index}/{question_amount}", "bold yellow"),
            )
            console.rule(header)
        else:
            print("=" * 50)
            print(f"{naytettava_otsikko}  |  Kysymys {index}/{question_amount}")
            print("=" * 50)

        options = q["options"][:]
        random.shuffle(options)

        try:
            answer_index = options.index(q["correct"])
        except ValueError:
            print(f"{RED}Kysymyksen oikeaa vastausta ei löytynyt vaihtoehdoista.{RESET}")
            continue

        question_header = f"Kysymys {index}/{question_amount}"
        question_body = q["question"]
        if console and Panel and Text:
            title_text = Text("Kysymys", style="bold yellow")
            body_text = Text(question_body)
            question_panel = Panel(
                body_text,
                title=title_text,
                border_style="cyan",
                padding=(1, 2),
                width=panel_width,
            )
            console.print(question_panel)
        else:
            print(f"\n{question_header}: {question_body}")

        if console and Table:
            option_table = Table(box=None, show_header=False, padding=(0, 1))
            option_table.add_column(" ", justify="right", style="bold")
            option_table.add_column("Vaihtoehto", overflow="fold")
            for opt_index, option in enumerate(options, 1):
                option_table.add_row(str(opt_index), option)
            console.print(
                Panel(
                    option_table,
                    title=Text("Vaihtoehdot", style="bold magenta"),
                    border_style="magenta",
                    padding=(0, 2),
                    width=panel_width,
                )
            )
        else:
            for opt_index, option in enumerate(options, 1):
                print(f"{opt_index}. {option}")

        if console:
            console.print()
        print_progress(answered, question_amount, score)

        max_option = len(options)
        prompt_message = f"Valitse vaihtoehto (1-{max_option}): "
        if console and Text:
            console.print(Text(prompt_message, style="bold magenta"))
        while True:
            try:
                raw_input = input("> " if console else prompt_message)
                user_input = int(raw_input)
                if 1 <= user_input <= max_option:
                    break
                message = f"Anna luku välillä 1-{max_option}"
                if console:
                    console.print(f"[yellow]{message}[/]")
                else:
                    print(message)
            except ValueError:
                message = "Anna kokonaisluku"
                if console:
                    console.print(f"[yellow]{message}[/]")
                else:
                    print(message)

        if user_input - 1 == answer_index:
            if console:
                console.print("[green]Oikein![/]")
            else:
                print(f"{GREEN}Oikein!{RESET}")
            score += 1
            user_answers.append(
                (q["question"], True, options[answer_index], options[user_input - 1])
            )
        else:
            correct_option = options[answer_index]
            if console:
                console.print(f"[red]Väärin![/] Oikea vastaus: {correct_option}")
            else:
                print(f"{RED}Väärin! Oikea vastaus: {correct_option}{RESET}")
            user_answers.append(
                (q["question"], False, correct_option, options[user_input - 1])
            )

        answered += 1
        if console:
            console.print()
        print_progress(answered, question_amount, score)

    clear_screen()
    if console and Text:
        console.rule(Text(naytettava_otsikko, style="bold cyan"))
        console.print(f"\n[bold yellow]=== Yhteenveto ===[/]")
        console.print(f"Oikein vastattuja: {score}/{question_amount}")
        console.print("\nYhteenvedon tulokset:")
        for question, correct, answer, user_ans in user_answers:
            if correct:
                status = "[green]Oikein[/]"
                console.print(f"- {question} → {status} (Vastaus: {answer})")
            else:
                console.print(
                    f"- {question} → [red]Väärin[/] (Oikea: {answer}, Sinun vastaus: {user_ans})"
                )
    else:
        print("=" * 50)
        print(naytettava_otsikko.center(50))
        print("=" * 50)
        print(f"\n{YELLOW}=== Yhteenveto ==={RESET}")
        print(f"Oikein vastattuja: {score}/{question_amount}")
        print("\nYhteenvedon tulokset:")
        for question, correct, answer, user_ans in user_answers:
            if correct:
                status = f"{GREEN}Oikein{RESET}"
                print(f"- {question} → {status} (Vastaus: {answer})")
            else:
                print(
                    f"- {question} → {RED}Väärin{RESET} (Oikea: {answer}, Sinun vastaus: {user_ans})"
                )

    if console:
        console.print()
    print_progress(question_amount, question_amount, score)

# --- Pääohjelma ---
def main():
    if not RICH_AVAILABLE:
        print(
            f"{YELLOW}Huom:{RESET} Rich ei ole asennettuna. "
            "Saat parannetun käyttöliittymän komennolla: "
            "py -m pip install rich"
        )

    while True: #pääsilmukka
        print(f"{YELLOW}=== TiTeTenttaaja ==={RESET}")

        tentit = hae_tentit()
        if not tentit:
            print(f"{RED}Virhe: kansiossa '{TENTTIKANSIO}' ei ole yhtään JSON-tenttitiedostoa.{RESET}")
            return

        # Listataan tentit tenttikansiosta.
        print("\nSaatavilla olevat tentit:")
        for i, nimi in enumerate(tentit, 1):
            print(f"{i}. {nimi.replace('.json', '').capitalize()}")

        # kysytään tenttitiedostoa.
        while True:
            try:
                valinta = int(input("Valitse tentti (numero): "))
                if 1 <= valinta <= len(tentit):
                    break
                else:
                    print(f"{RED}Syötettyä numeroa ei ole listassa.{RESET}")
            except ValueError:
                print(f"{RED}Syöte ei ollut numero.{RESET}")

        valittu_tentti = tentit[valinta - 1]
        print(f"\n{YELLOW}Valitsit tentin: {valittu_tentti.replace('.json', '').capitalize()}{RESET}")

        kysymykset, tentti_otsikko = lue_kysymykset(valittu_tentti)
        suorita_tentti(kysymykset, otsikko=tentti_otsikko)

        # kysytään käyttäjältä tentataanko vielä
        uudestaan = input("\nHaluatko tehdä toisen tentin? (k/e): ").strip().lower()
        if uudestaan != "k":
            clear_screen()
            print("Kiitos tenttailusta. Suljetaan...")
            break

if __name__ == "__main__":
    main()
