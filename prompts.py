from __future__ import annotations
from enum import Enum

class PromptFlags:

    class ReturnFormat(Enum):
        INDEX = 0
        NUMBER = 1
        OBJECT = 2

class PromptIndents:
    INDENT_AMOUNT = 4
    INDENT = ' ' * INDENT_AMOUNT

    @staticmethod
    def print(s: str, indent: int=0):
        print(f'{PromptIndents.INDENT * indent}{s}')

    @staticmethod
    def input(s: str, indent: int=0):
        return input(f'{PromptIndents.INDENT * indent}{s}: ').strip()
    
    @staticmethod
    def invalid(s: str, indent: int=0):
        # TODO ???
        print(f'Invalid: {s}\n', indent)

class PromptValidation:

    NAME_CHARS = (' ', ',', '-', '.')

    @staticmethod
    def nonempty(choice: str) -> bool:
        return choice.strip() != ''

    @staticmethod
    def name(choice: str) -> bool:
        """Return True if the given str is alphabetic besides OKAY characters."""
        sanitized = choice
        for char in PromptValidation.NAME_CHARS:
            sanitized = sanitized.replace(char, '')        
        return sanitized.isalpha()

    @staticmethod
    def str(choice: str, lower: int=1, upper: int=float('inf')) -> bool:
        return lower <= len(choice) <= upper

    @staticmethod
    def number(choice: str, converter: callable, lower: float, upper: float) -> bool:
        try:
            return lower <= converter(choice) <= upper
        except:
            return False

    @staticmethod
    def int(choice: str, lower: int=float('-inf'), upper: int=float('inf')) -> bool:
        return PromptValidation.number(choice, int, lower, upper)

    @staticmethod
    def float(choice: str, lower: int=float('-inf'), upper: int=float('inf')) -> bool:
        return PromptValidation.number(choice, float, lower, upper)

    @staticmethod
    def bool(choice: str, strict: bool=False) -> bool:
        choice = choice.lower()
        return (not strict) or (PromptValidation.nonempty(choice) and (choice in (Prompts.YES, Prompts.NO)))

class Prompts:
    YES = 'y'
    NO = 'n'

    @staticmethod
    def prompt(p: str='Input',  indent: int=0, validators: list=[], inv: str='', allow_blank: bool=False, args: list=[], kwargs: dict={}):

        choice = PromptIndents.input(p, indent)
        while (not (allow_blank and (not choice.strip()))) and (not all(v(choice, *args, **kwargs) for v in validators)):
            PromptIndents.invalid(inv, indent)
            choice = PromptIndents.input(p, indent)
        return choice.strip()

    @staticmethod
    def bool(prompt: str='Yes or no', indent: int=0, strict: bool=False, default: bool=True, allow_blank: bool=False) -> bool:
        """
        Prompt yes/no and return a bool.
        If a default is given, only give the non-default if it's explicitly input.
        In strict mode, only return True/False; None is not possible.
        If not strict and no default, any input besides yes/no returns None.
        """
            
        choice = Prompts.prompt(f'{prompt}? {Prompts.YES}/{Prompts.NO}', indent, [PromptValidation.bool], f'{Prompts.YES} or {Prompts.NO}', [strict])
        choice = choice.lower()

        if allow_blank and (not choice.strip()):
            return default

        if default is True:
            return choice != Prompts.NO
        elif default is False:
            return choice == Prompts.YES
        else:
            return True if choice == YES else False if choice == NO else None

    @staticmethod
    def name(prompt: str='Name', indent: int=0, allow_blank: bool=False) -> str:
        choice = Prompts.prompt(prompt, indent, [PromptValidation.nonempty, PromptValidation.name], f'letters + {PromptValidation.NAME_CHARS}', allow_blank=allow_blank)
        return choice

    @staticmethod
    def str(prompt: str='String', indent: int=0, lower: int=1, upper: int=float('inf'), allow_blank: bool=False) -> str:
        choice = Prompts.prompt(prompt, indent, [PromptValidation.str], f'between {lower} and {upper} characters', allow_blank=allow_blank, args=[lower, upper])
        return choice

    @staticmethod
    def int(prompt: str='Integer', indent: int=0, lower: int=float('-inf'), upper: int=float('inf'), allow_blank: bool=False) -> int:
        inv = f'integer between {lower} and {upper} (inclusive)'
        choice = Prompts.prompt(prompt, indent, [PromptValidation.int], inv, allow_blank=allow_blank, args=[lower, upper])
        return int(choice) if choice else None

    @staticmethod
    def float(prompt: str='Number', indent: int=0, lower: float=float('-inf'), upper: float=float('inf'), allow_blank: bool=False) -> float:
        inv = f'number between {lower} and {upper} (inclusive)'
        choice = Prompts.prompt(prompt, indent, [PromptValidation.float], inv, allow_blank=allow_blank, args=[lower, upper])
        return float(choice) if choice else None

    @staticmethod
    def choice(prompt: str='Options', choices=[], indent: int=0, allow_blank: bool=False, return_format: PromptFlags.ReturnFormat=PromptFlags.ReturnFormat.NUMBER) -> int:
        if not choices:
            raise Exception
        
        max_cols = len(str(len(choices)))
        
        choice_strs = []
        for (i, choice) in enumerate(choices):
            choice_strs.append(f'{str(i + 1).ljust(max_cols)}: {choice}')
        prompt = f'{prompt}:\n\n' + '\n'.join(choice_strs) + '\n\nChoice'
        
        n = Prompts.int(prompt, indent=indent, lower=1, upper=len(choices), allow_blank=allow_blank)

        match return_format:
            case PromptFlags.ReturnFormat.INDEX:
                return n - 1
            case PromptFlags.ReturnFormat.NUMBER:
                return n
            case PromptFlags.ReturnFormat.OBJECT:
                return choices[n - 1]

class PromptFormatting:

    @staticmethod
    def float(f: float) -> str:
        truncated = f'{f:.1f}'
        rounded = f'{round(f, 1)}'
        return truncated if truncated == rounded else f'{truncated} or {rounded}'

class PromptOperations:

    @staticmethod
    def until_quit(action: callable, do_while: True, continue_keyword: str='continue', quit_keyword: str='quit', continue_string: str='', quit_string: str='Q', indent: int=0):
        if do_while:
            action()
        
        if not continue_keyword:
            c_keyword_printable = 'Enter'
        else:
            c_keyword_printable = continue_string

        prompt = f'Hit {c_keyword_printable} to {continue_string} or {quit_keyword} to {quit_string}'
        while True:
            choice = PromptIndents.input(prompt, indent).upper()
            if choice == continue_keyword:
                action()
            elif choice == quit_keyword:
                break

    @staticmethod
    def loop(routine: callable, args: list=[], kwargs: dict={},
            blank_before: bool=True, blank_after: bool=True):
        responses = []
        go = Prompts.bool('Start')
        while go:
            responses.append(routine(*args, **kwargs))
            if blank_before: print()
            go = Prompts.bool('Continue')
            if blank_after: print()
        return responses
