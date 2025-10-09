import random
import json
import os

# Värikoodit
RED = "\033[91m"
GREEN = "\033[32m"
YELLOW = "\033[93m"
RESET = "\033[0m"


TENTTIKANSIO = "tentit"

# Etsii tenttikansiosta json-tiedostot.
def hae_tentit():
    return [f for f in os.listdir(TENTTIKANSIO) if f.endswith(".json")]

# Lukee kysymykset jsonista
def lue_kysymykset(tiedosto):
    with open(os.path.join(TENTTIKANSIO, tiedosto), "r", encoding="utf-8") as f:
        return json.load(f)

# Tentin suoritus
def suorita_tentti(questions):
    # Satunnaistaa vaihtoehdot ja oikean vastauksen indeksin.
    for q in questions:
        correct = q["options"][0]
        random.shuffle(q["options"])
        q["answer"] = q["options"].index(correct)

    score = 0
    user_answers = []

    while True:
        try:
            # kysytään käyttäjältä tentattavien kysymysten määrä.
            question_amount = int(input(f"Montako kysymystä kysytään? (kysymyksiä yht. {len(questions)}): "))
            if 1 <= question_amount <= len(questions):
                break
            else:
                print(f"{RED}Annettu numero ei ole kysymysten määrän sisällä.{RESET}")
        except ValueError:
            print(f"{RED}Syöte ei ollut numero.{RESET}")

    quiz_questions = random.sample(questions, k=question_amount)

    for i, q in enumerate(quiz_questions, 1):
        print(f"\nKysymys {i}/{question_amount}: {q['question']}")
        for idx, option in enumerate(q["options"]):
            print(f"{idx + 1}. {option}")

        while True:
            try:
                user_input = int(input("Valitse vaihtoehto (1-4): "))
                if 1 <= user_input <= 4:
                    break
                else:
                    print("Anna luku välillä 1–4")
            except ValueError:
                print(f"{RED}Numero ei ollut väliltä 1–4{RESET}")

        if user_input - 1 == q["answer"]:
            print(f"{GREEN}Oikein!{RESET}")
            score += 1
            user_answers.append((q["question"], True, q["options"][q["answer"]]))
        else:
            print(f"{RED}Väärin! Oikea vastaus: {q['options'][q['answer']]}{RESET}")
            user_answers.append((q["question"], False, q["options"][q["answer"]]))

    print(f"\n{YELLOW}=== Tentti valmis! ==={RESET}")
    print(f"Sait oikein {score}/{len(quiz_questions)} kysymystä.\n")

    print("Yhteenvedon tulokset:")
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

        kysymykset = lue_kysymykset(valittu_tentti)
        suorita_tentti(kysymykset)

        # kysytään käyttäjältä tentataanko vielä
        uudestaan = input("\nHaluatko tehdä toisen tentin? (k/e): ").strip().lower()
        if uudestaan != "k":
            print("Kiitos tenttailusta. Suljetaan...")
            break

if __name__ == "__main__":
    main()