from datetime import datetime, timedelta
from collections import UserDict

"""Tools for working with functions and callable objects"""
from functools import wraps
from dataclasses import dataclass
from dateutil import relativedelta
import pickle


def name_validation(func):
    """name_validation Decorator that validates the format of a name before calling the decorated function.

    :param func: The function to be decorated.
    :type func: callable
    :return: The decorated function.
    :rtype: callable
    """  # name can only contain letters

    @wraps(func)
    def inner(self, entered_name: str):
        if not entered_name.isalpha():
            print("The provided name is in incorrect format and cannot be accepted")
        return func(self, entered_name)

    return inner


def phone_validation(func):
    """phone_validation Decorator that validates the format of phone numbers before calling the decorated function.

    :param func: The function to be decorated.
    :type func: callable
    :return: The return value of the decorated function.
    :rtype: callable
    """  # phone can only contain numbers and must be 10 charaters long

    @wraps(func)
    def inner(self, *args):
        for arg in args:
            if not (arg.isdigit() and len(arg) == 10):
                print(f"{arg} is in incorrect format")
                return None
        return func(self, *args)

    return inner


def input_error(func):
    """input_error Decorator to handle input errors.
    This decorator wraps a function and catches any `ValueError`
    that may occur during its execution. If a `ValueError` is caught,
    it returns the message "Give me name and phone please."
    :param func:  The function to decorate.
    :type func: callable
    :return:  The decorated function.
    :rtype: callable
    """

    @wraps(func)
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Give me name and phone please."
        except IndexError:
            return "No contacts saved. First you need to add at least one contact"
        except KeyError:
            return "No person unders such name/nickname"

    return inner


def parse_input(user_input: str) -> tuple[str, *tuple[str, ...]]:
    """parse_input Parses the user input and extracts the command and arguments.
    :param  user_input: The user input string.
    :type args: tuple
    :return: A tuple containing the command and arguments.
    :rtype: tuple[str, *tuple[str, ...]]
    """
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args


class Field:
    """Represents a base class for fields."""

    # defining base class
    def __init__(self, value: str) -> None:
        self.value = value

    def __str__(self) -> str:
        return str(self.value)


class Name(Field):
    """Name Represents a field for storing and validating names."""

    @name_validation
    def __init__(self, entered_name: str) -> None:
        super().__init__(entered_name)

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, key: str) -> bool:
        return str(self) == key


@dataclass
class Phone(Field):
    """Validates and stores a phone number."""

    value: str

    def __str__(self):
        return str(self.value)

    def __eq__(self, other):
        return str(self) == other


class Birthday(Field):
    """Represents a field for storing and validating birthdays."""

    def __init__(self, value: str) -> None:
        try:
            super().__init__(datetime.strptime(value, "%d.%m.%Y"))
        except ValueError as e:
            raise ValueError("Invalid date format. Use DD.MM.YYYY") from e

    def __str__(self) -> str:
        return self.value.strftime("%d.%m.%Y")


class Record:
    """Represents a record for storing contact information."""

    def __init__(self, name: str) -> None:
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    @phone_validation
    def add_phone(self, phone) -> None:
        self.phones.append(Phone(phone))

    @phone_validation
    def find_phone(self, phone: str):
        try:
            found = self.phones.index(phone)
            return self.phones[found]
        except ValueError:
            print("No such phone here, wanna add it?")

    @phone_validation
    def edit_phone(self, old_phone, new_phone):
        if old_phone in self.phones:
            index = self.phones.index(old_phone)
            self.phones[index] = Phone(new_phone)
            print("Number edited")
        else:
            return True

    @phone_validation
    def delete_phone(self, phone):
        try:
            self.phones.remove(phone)
            print("Success, phone removed")
        except ValueError:
            print("No such phone found in the record")

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"

    def add_birthday(self, value):
        self.birthday = Birthday(value)


class AddressBook(UserDict):
    """Represents an address book for storing and managing contact records."""

    def add_record(self, record: Record):
        self.data[record.name] = record

    def find(self, entered_name):
        if entered_name in self.data.keys():
            print(f"Fetching {entered_name}...")
            return self.data.get(entered_name)
        else:
            print(f"Who is this {entered_name}?")

    def delete(self, name):
        if name in self.data:
            print(f"Deleting {name}...")
            del self.data[name]

        else:
            print(f"{name} does not exist")

    def __str__(self):
        return "".join(f"{self.data[key]}\n" for key in self.data.keys())


@input_error
def add_contact(args: tuple, book: AddressBook) -> str:
    """add_contact This code defines a function called add_contact that takes two
    arguments: args and book. The function adds a new contact to the AddressBook object

    :param args:  A tuple containing the name and phone number.
    :type args: tuple
    :param book: AddressBook object where the contact will be added.
    :type book: AddressBook
    :return: A success message indicating that the contact has been added.
    :rtype: str
    """
    name, phone = args
    if name not in book.keys():
        name = Record(name)

        name.add_phone(phone)
        book.add_record(name)
        if name.phones:
            return "Contact added."
        return "Command completed with errors (see above), awaiting input..."
    return "This contact exists."


@input_error
def change_contact(args: tuple, book: AddressBook) -> str:
    """change_contact Change the contact phone number in the book record.

     :param args:  A tuple containing the name and new phone number.
     :type args: tuple
     :param contacts: AddressBook object of contacts where the phone number will be updated.
    :type contacts: AddressBook
     :return: A success message indicating that the contact has been changed.
     :rtype: str
    """
    name, old_phone, new_phone = args
    if book.find(name).edit_phone(old_phone, new_phone):
        return "Error, check the input"
    return "Success! Contact changed"


@input_error
def add_birthday(args, book: AddressBook) -> str:
    """
    Adds a birthday for a contact in the address book.

    """
    name, birthdate = args
    if record := book.find(name):
        record.add_birthday(birthdate)
        return f"Birthday added for {name}"
    else:
        return "Contact not found in the address book"


@input_error
def show_birthday(args, book: AddressBook) -> str:
    """
    Show birthday for the specified contact.

    """
    name = args[0]
    if not (record := book.find(name)):
        return f"No contact found with the name {name}"
    if record.birthday:
        return f"The birthday of {name} is {record.birthday}"
    else:
        return f"No birthday information found for {name}"


def get_upcoming_birthdays(book: AddressBook) -> list[dict]:
    """Get upcoming birthdays
    :param book: AddressBook - the address book containing contact information.
    :result: list[dict] - list of dictionaries of contacts that need to be congratulated
    in the next 7 days including today (birthdays on weekends are moved to the next Monday)
    """
    today = datetime.now().date()
    intermediate = []

    def weekend_adjuster(congratulation_date: datetime) -> datetime:
        """Weekend adjuster
        :param congratulation_date: datetime - date on which colleague
        receives congratulations
        :result: datetime - congratulation date with adjustment
        made for weekends (moved to nearest Monday)
        Function checks if the congratulation date is a weekday or a weekend.
        For weekends, date is moved to Monday, for weekdays,
        date is returned without changes.
        """
        if congratulation_date.weekday() < 5:
            return congratulation_date
        elif congratulation_date.weekday() == 5:
            return congratulation_date + timedelta(days=2)
        else:
            return congratulation_date + timedelta(days=1)

    for value in book.values():
        user = {"name": value.name.value, "birthday": value.birthday.value}
        user["birthday"] = user["birthday"].date()
        user["congratulation_date"] = user["birthday"].replace(year=today.year)
        if user["congratulation_date"] < today:
            if (
                user["congratulation_date"] + relativedelta(years=1) - today
            ) <= timedelta(days=6):
                intermediate.append(
                    {
                        "name": user["name"],
                        "congratulation_date": weekend_adjuster(
                            (user["congratulation_date"] + relativedelta(years=1))
                        ),
                    }
                )
            # else do nothing
        elif user["congratulation_date"] - today <= timedelta(days=6):
            intermediate.append(
                {
                    "name": user["name"],
                    "congratulation_date": weekend_adjuster(
                        (user["congratulation_date"])
                    ),
                }
            )
    for user in intermediate.copy():
        if user["congratulation_date"] - today > timedelta(days=6):
            intermediate.remove(user)
        elif today - user["congratulation_date"] < timedelta(days=-6):
            intermediate.remove(user)
        user["congratulation_date"] = user["congratulation_date"].strftime("%Y.%m.%d")
    return intermediate

def save_data(book: AddressBook, filename:str ="addressbook.pkl") -> None:
    """save_data Save data to a file using pickle serialization.

    :param book: The data to be saved.
    :type book: AddressBook
    :param filename: The name of the file to save to. Defaults to "addressbook.pkl".
    :type filename: str, optional
    """    
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename:str ="addressbook.pkl") -> AddressBook:
    """load_data Load data from a file using pickle deserialization.

    :param filename: The name of the file to load from. Defaults to "addressbook.pkl".
    :type filename: str, optional
    :return: The loaded data, or an empty AddressBook if the file is not found.
    :rtype: AddressBook
    """    
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  
def main():
    """main This code defines a main function that serves as the entry point of a program.
    It creates an empty contacts dictionary and then enters a loop to interact with the user.
    The user can enter different commands, and the program responds accordingly."""
    book = AddressBook()
    print("Welcome to the assistant bot!")
    book = load_data()
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        match command:
            case "close" | "exit":
                print("Goodbye!")
                save_data(book)
                break

            case "hello":
                print("How can I help you?")
            case "add":
                print(add_contact(args, book))

            case "change":
                # cmd in format change name old phone new phone (otherwise there no certainty which number we change for contact)
                print(change_contact(args, book))

            case "phone":

                print(book.find(args[0]))
            case "all":
                if not book:
                    print("There are no contacts, wanna add some?")
                else:
                    print(book)
            case "add-birthday":
                print(add_birthday(args, book))
            case "show-birthday":
                print(show_birthday(args, book))
            case "birthdays":
                upcoming_dates = get_upcoming_birthdays(book)
                for item in upcoming_dates:
                    print(
                        f"Name {item["name"]} should be congratulated on {item["congratulation_date"]}"
                    )
            case _:
                print("Invalid command.")


if __name__ == "__main__":
    main()
