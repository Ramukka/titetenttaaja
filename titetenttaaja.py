import json
import os
import random

# Värikoodit
RED = "\033[91m"
GREEN = "\033[32m"
YELLOW = "\033[93m"
RESET = "\033[0m"


TENTTIKANSIO = "tentit"


def render_progress(answered, total, score, bar_length=30):
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

    percent = int(ratio * 100)
    return f"{bar} {percent:>3}% suoritettu\n{score}/{total} oikein"


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
        print("=" * 50)
        print(naytettava_otsikko.center(50))
        print("=" * 50)
        print(render_progress(answered, question_amount, score))

        options = q["options"][:]
        random.shuffle(options)

        try:
            answer_index = options.index(q["correct"])
        except ValueError:
            print(f"{RED}Kysymyksen oikeaa vastausta ei löytynyt vaihtoehdoista.{RESET}")
            continue

        print(f"\nKysymys {index}/{question_amount}: {q['question']}")
        for opt_index, option in enumerate(options, 1):
            print(f"{opt_index}. {option}")

        max_option = len(options)
        while True:
            try:
                user_input = int(input(f"Valitse vaihtoehto (1-{max_option}): "))
                if 1 <= user_input <= max_option:
                    break
                print(f"Anna luku välillä 1-{max_option}")
            except ValueError:
                print("Anna kokonaisluku")

        if user_input - 1 == answer_index:
            print(f"{GREEN}Oikein!{RESET}")
            score += 1
            user_answers.append((q["question"], True, options[answer_index]))
        else:
            correct_option = options[answer_index]
            print(f"{RED}Väärin! Oikea vastaus: {correct_option}{RESET}")
            user_answers.append((q["question"], False, correct_option))

        answered += 1
        print(render_progress(answered, question_amount, score))

    clear_screen()
    print("=" * 50)
    print(naytettava_otsikko.center(50))
    print("=" * 50)
    print(render_progress(question_amount, question_amount, score))
    print(f"\n{YELLOW}=== Yhteenveto ==={RESET}")
    print(f"Oikein vastattuja: {score}/{question_amount}")
    print("\nYhteenvedon tulokset:")
    for question, correct, answer in user_answers:
        status = f"{GREEN}Oikein{RESET}" if correct else f"{RED}Väärin{RESET}"
        print(f"- {question} → {status} (Oikea vastaus: {answer})")

# --- Pääohjelma ---
def main():
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
            print("Kiitos tenttailusta. Suljetaan...")
            break

if __name__ == "__main__":
    main()
