from typeguard import typechecked
import enum
import sys


@typechecked()
def get_max_state_from_number(
        condition_states: list[str],
        max_states: list[str] | None,
        level: int,
        min_number: int,
        max_number: int
) -> int | None:
    if max_states is None:
        return None
    if len(max_states) <= level:
        return None
    if not (condition_states == max_states[:level]):
        return None

    max_state_string = max_states[level]
    try:
        max_state_number = int(max_state_string)
    except ValueError:
        print(f"ERROR: max-state string '{max_state_string}' is not a number. Expected a number between "
              f"{min_number} and {max_number}.")
        sys.exit(-1)

    if max_state_number > max_number or max_state_number < min_number:
        print(f"ERROR: max-state number {max_state_number} is out of range. Must be between "
              f"{min_number} and {max_number}.")
        sys.exit(-1)

    return max_state_number


@typechecked()
def get_max_state(condition_states: list[str], max_states: list[str] | None, level: int, StateType):
    if max_states is None:
        return None
    if len(max_states) <= level:
        return None
    if not (condition_states == max_states[:level]):
        return None

    max_state_name = max_states[level].lower()
    try:
        max_state = StateType(max_state_name)
    except ValueError:
        print(f"ERROR: state '{max_state_name}' is unknown in fsm-level {level}.")
        print(f"Allowed states are: {', '.join([s.lower() for s in StateType])}.")
        sys.exit(-1)
    return max_state


@typechecked()
def is_max_state(max_state: enum.StrEnum | int | None, last_state: enum.StrEnum | int) -> bool:
    if max_state is None:
        return False

    if isinstance(max_state, int):
        if last_state > max_state:
            print(f"Abort FSM: Maximum state '{max_state}' reached.")
            return True

    else:
        if max_state == last_state:
            print(f"Abort FSM: Maximum state '{max_state}' reached.")
            return True

    return False
