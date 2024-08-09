class PromptException(Exception):
    pass

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
    def bool(prompt: str='Yes or no', indent: int=0, strict: bool=False, default: bool|None=True, allow_blank: bool=False) -> bool:
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
            return True if choice == Prompts.YES else False if choice == Prompts.NO else None

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
    def choice(prompt: str='Options', choices=[], indent: int=0, allow_blank: bool=False) -> int:
        if not choices:
            raise Exception
        
        max_cols = len(str(len(choices)))
        
        choice_strs = []
        for (i, choice) in enumerate(choices):
            choice_strs.append(f'{str(i + 1).ljust(max_cols)}: {choice}')
        prompt = f'{prompt}:\n\n' + '\n'.join(choice_strs) + '\n\nChoice'
        
        return Prompts.int(prompt, indent=indent, lower=1, upper=len(choices), allow_blank=allow_blank)

class PromptFormatting:

    @staticmethod
    def float(f: float) -> str:
        truncated = f'{f:.1f}'
        rounded = f'{round(f, 1)}'
        return truncated if truncated == rounded else f'{truncated} or {rounded}'

class PromptFlows:

    @staticmethod
    def until_quit(routine: callable, args: list=[], kwargs: dict={}, do_while: bool=True, between: callable=None, continue_trigger: str='Enter', quit_trigger: str='Q', continue_string: str='continue', quit_string: str='quit', indent: int=0):
        """
        # TODO Clarify purpose; how is this different from loop?
        # TODO Idea: make a looping class that has a core loop, but builders that incorporate both these methods' many functions, rather than two methods with huge numbers of kwargs
        """

        def sub() -> None:
            routine(*args, **kwargs)
        
        if (continue_trigger == quit_trigger):
            raise PromptException(f'Continue and quit triggers must not be the same: {continue_trigger} and {quit_trigger}')

        if not continue_trigger:
            continue_trigger = 'Enter'

        if not quit_trigger:
            quit_trigger = 'Q'

        if do_while:
            sub()

        prompt = f'Hit {continue_trigger} to {continue_string} or {quit_trigger} to {quit_string}'

        while True:
            choice = PromptIndents.input(prompt, indent).upper().strip()
            if between:
                between()

            if ((not choice) and (continue_trigger == 'Enter')) or (choice == continue_trigger):
                sub()

            elif (((not choice) and (quit_trigger == 'Enter')) or (choice == quit_trigger)):
                break

    @staticmethod
    def loop(routine: callable, args: list=[], kwargs: dict={}, do_while: bool=True, between: callable=None, ask_continue: bool=True, count: bool=False):
        """
        Repeat the given routine, passing it the given args and kwargs, and return a list of responses to it.

        between is a routine (no args) to be run between each pair of routines.

        Iff do_while is False, the user is asked to start the loop.

        Iff ask_continue is True, the user is asked to continue after each iteration.

        Iff count is True, the iteration number is printed before the routine.

        By default, it asks to continue each time. If ask_continue is False, a response of None from the routine
        will instead be interpreted as the command to stop.
        """
        def sub() -> bool:

            if count:
                print(f'{len(responses) + 1}')

            response = routine(*args, **kwargs)

            if ask_continue:
                responses.append(response)
                keep_going = Prompts.bool('Continue')

            else:
                if response is None:
                    return False
                else:
                    responses.append(response)
                    keep_going = True

            if keep_going and between:
                between()

            return keep_going

        responses = []

        if do_while:
            go = sub()
        else:
            go = Prompts.bool('Start')

        while go:
            go = sub()

        return responses
