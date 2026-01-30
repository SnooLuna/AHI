from customtkinter import * # type: ignore
from customtkinter import BooleanVar, StringVar, CTk, CTkFrame, set_default_color_theme,CTkLabel, CTkEntry, CTkCheckBox, CTkButton # type: ignore
import json
from random import choice, sample

class Deck:
    def __init__(self, name):
        with open(name, "r") as file:
            cards = json.load(file)
        self.questions = cards["Questions"]
        self.name = cards["Name"]

    def check(self, answer):
        match self._involvement_level:
            case 1:
                self._check1(answer)

class DeckDisplay(CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        label = CTkLabel(self, text="hi")
        label.pack(pady=10, padx=10)
        self._screen = [label]
        


class System(CTk):
    def __init__(self, title):
        super().__init__()

        self._decks = [Deck('cards.json'), Deck('cards.json')]
        self._current_deck = None

        with open("home.json", "r") as file:
            home = json.load(file)
        self._home = home

        self._currentQ = None
        self._answer = StringVar()
        self._accept_typos = BooleanVar()

        self.title(title)
        self.geometry("750x600")
        self._screen = []
        self._frame = CTkFrame(self)
        self._frame.pack(pady=20, padx=20, fill="x")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        set_default_color_theme("dark-blue")

        self._start_screen()

    def _make_label(self, text=None, wraplength=700, pady=10, padx=0, fontsize=18):
        label = CTkLabel(self._frame, text=text, wraplength=wraplength, font=("Arial", fontsize))
        label.pack(pady=pady, padx=padx)
        self._screen.append(label)
        return label

    def _make_button(self, text=None, command=None, pady=10, padx=0):
        button = CTkButton(self._frame, text=text, command=command, font=("Arial", 16))
        button.pack(pady=pady, padx=padx, ipadx=15, ipady=5)
        self._screen.append(button)
        return button

    def _make_check(self, text=None, command=None, var=None, on=None, off=None, pady=40, padx=40):
        check = CTkCheckBox(self._frame, text=text, command=command, variable=var, onvalue=on, offvalue=off,
                            border_width=2, font=("Arial", 14))
        check.pack(pady=pady, padx=padx, anchor="w")
        self._screen.append(check)
        return check
    
    def _make_entry(self, textvar, fontname="Arial", fontsize=18, pady=10, padx=40):
        entry = CTkEntry(self._frame, textvariable=textvar, font=(fontname, fontsize))
        entry.pack(pady=pady, padx=padx, anchor="w")
        self._screen.append(entry)
        return entry

    def _clear_screen(self):
        for widget in self._screen:      # Clear all widgets on the screen
            widget.destroy()
        self._screen = []                # Return it to be an empty list

    def _start_screen(self):
        self._make_label("Start your learning journey!", pady=20, fontsize=25)
        self._make_label(self._home["Text"], pady=20)
        self._display_decks()
        for d in self._decks:
            self._make_button(d.name, lambda d=d: self._choose_deck(d))

    def _start_deck(self, deck):
        self._clear_screen()
        self._current_deck = deck
        self._make_label("hi")

    def _display_decks(self):
        for i, deck in enumerate(self._decks):
            self._screen.append(DeckDisplay(self))

    def _choose_deck(self, deck):
        self._current_deck = deck
        self._next_question()

    def _next_question(self, event=None):
        self._answer = StringVar()           # reset the answer variable
        self._currentQ = choice(self._current_deck.questions)
        self._display(self._currentQ)        # Display the chosen question to the user


    def _display(self, question):
        self._clear_screen()                 # clear anything previously on screen

        self._make_label(question["question"], 700, pady=50)
        self._make_entry(textvar=self._answer).focus()
        self.bind('<Return>', self._submit)
    
    def _submit(self, event):
        self._make_label(f"{self._answer.get()} is {"correct!" if self._correct() else "incorrect."}")
        
        self.bind('<Return>', self._next_question)

    def _correct(self):
        if self._accept_typos:
            pass
        else:
            return self._answer.get().upper() == self._currentQ["answer"].upper()
            
            


if __name__ == "__main__":
    sys = System("Learning words ig")
    sys.mainloop()