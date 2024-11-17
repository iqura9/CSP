from collections import defaultdict
import copy
from typing import List, Callable, Dict, Optional


class Constraint:
    def __init__(self, variables: List[str], is_satisfied: Callable[[Dict[str, int]], bool]):
        self.variables = variables
        self.is_satisfied = is_satisfied

    def check(self, assignment: Dict[str, int]) -> bool:
        # Перевіряємо, чи всі змінні в обмеженні мають присвоєні значення
        if all(var in assignment for var in self.variables):
            # Якщо так, перевіряємо, чи задовольняється обмеження
            return self.is_satisfied(assignment)
        # Якщо ні, обмеження не порушено
        return True

    def __repr__(self):
        return f"Constraint({self.variables}, {self.is_satisfied})"


class CSP:
    def __init__(
        self,
        variables: List[str],
        domains: Dict[str, List[int]],
        variable_heuristic: Optional[str] = None,
        intermediate_assignment_hook: Optional[Callable[[Dict[str, int]], None]] = None,
    ):
        self.variables = variables
        self.domains = domains
        self.constraints: Dict[str, List[Constraint]] = defaultdict(list)
        self.variable_heuristic = variable_heuristic
        self.intermediate_assignment_hook = intermediate_assignment_hook

        # Ініціалізуємо поточні домени для forward checking
        self.current_domains = copy.deepcopy(domains)

    def add_constraint(self, constraint: Constraint):
        # Додаємо обмеження до кожної змінної
        for variable in constraint.variables:
            self.constraints[variable].append(constraint)

    def is_consistent(self, var: str, value: int, assignment: Dict[str, int]) -> bool:
        # Перевіряємо, чи присвоєння значення змінній не порушує обмежень
        local_assignment = assignment.copy()
        local_assignment[var] = value
        for constraint in self.constraints[var]:
            if not constraint.check(local_assignment):
                return False
        return True

    def get_unassigned_variables(self, assignment: Dict[str, int]) -> List[str]:
        # Отримуємо список неприсвоєних змінних
        return [v for v in self.variables if v not in assignment]

    def select_unassigned_variable(self, assignment: Dict[str, int]) -> str:
        # Вибираємо неприсвоєну змінну згідно з евристикою
        unassigned_vars = self.get_unassigned_variables(assignment)

        if self.variable_heuristic == "mrv":
            # Евристика мінімальної кількості решти значень (Minimum Remaining Values)
            return min(
                unassigned_vars,
                key=lambda var: len(self.current_domains[var]),
            )
        elif self.variable_heuristic == "degree":
            # Ступенева евристика (Degree Heuristic)
            return max(
                unassigned_vars,
                key=lambda var: len(self.constraints[var]),
            )
        else:
            # Без евристики - вибираємо першу неприсвоєну змінну
            return unassigned_vars[0]

    def order_domain_values(self, var: str, assignment: Dict[str, int]) -> List[int]:
        # Порядок значень домену змінної з використанням евристики найменш обмежувального значення (LCV)
        if len(self.current_domains[var]) == 1:
            return self.current_domains[var]

        def count_conflicts(value):
            count = 0
            for constraint in self.constraints[var]:
                for neighbor in constraint.variables:
                    if neighbor != var and neighbor not in assignment:
                        if value in self.current_domains[neighbor]:
                            count += 1
            return count

        return sorted(self.current_domains[var], key=count_conflicts)

    def forward_check(self, var: str, value: int, assignment: Dict[str, int], removals: Dict[str, List[int]], depth: int) -> bool:
        # Пряма перевірка (forward checking)
        for constraint in self.constraints[var]:
            for neighbor in constraint.variables:
                if neighbor != var and neighbor not in assignment:
                    for neighbor_value in self.current_domains[neighbor][:]:
                        local_assignment = assignment.copy()
                        local_assignment[neighbor] = neighbor_value
                        local_assignment[var] = value
                        if not constraint.check(local_assignment):
                            self.current_domains[neighbor].remove(neighbor_value)
                            removals.setdefault(neighbor, []).append(neighbor_value)
                    if not self.current_domains[neighbor]:
                        log(f"Failure: Domain wiped out for {neighbor}", depth)
                        return False
        return True

    def restore_domains(self, removals: Dict[str, List[int]]):
        # Відновлюємо домени після повернення
        for var, values in removals.items():
            self.current_domains[var].extend(values)

    def backtrack(self, assignment: Dict[str, int], depth: int = 0) -> Optional[Dict[str, int]]:
        # Алгоритм пошуку з поверненням
        if len(assignment) == len(self.variables):
            # Якщо всі змінні присвоєні, повертаємо розв'язок
            return assignment.copy()

        var = self.select_unassigned_variable(assignment)
        log(f"Selecting variable {var}", depth)
        for value in self.order_domain_values(var, assignment):
            log(f"Trying {var}={value}", depth)
            if self.is_consistent(var, value, assignment):
                # Створюємо копію присвоєння
                local_assignment = assignment.copy()
                local_assignment[var] = value
                removals = {}
                # Зберігаємо копію доменів
                saved_domains = copy.deepcopy(self.current_domains)
                self.current_domains[var] = [value]

                if self.forward_check(var, value, local_assignment, removals, depth):
                    if self.intermediate_assignment_hook:
                        self.intermediate_assignment_hook(local_assignment)
                    result = self.backtrack(local_assignment, depth + 1)
                    if result:
                        return result

                # Відновлюємо домени
                self.current_domains = saved_domains
                # Відновлюємо присвоєння
                # (local_assignment відкидається автоматично при поверненні)
            else:
                log(f"{var}={value} is inconsistent", depth)
        log(f"Backtracking from variable {var}", depth)
        return None


def not_equal_constraint(var1: str, var2: str) -> Callable[[Dict[str, int]], bool]:
    # Функція-предикат для обмеження "не дорівнює"
    return lambda assignment: assignment.get(var1) != assignment.get(var2)


def add_row_constraints(csp: CSP):
    # Додаємо обмеження для рядків
    for row in range(1, 5):
        row_vars = [f"X{row}{col}" for col in range(1, 5)]
        for i in range(4):
            for j in range(i + 1, 4):
                csp.add_constraint(
                    Constraint(
                        [row_vars[i], row_vars[j]],
                        not_equal_constraint(row_vars[i], row_vars[j]),
                    )
                )


def add_column_constraints(csp: CSP):
    # Додаємо обмеження для стовпців
    for col in range(1, 5):
        col_vars = [f"X{row}{col}" for row in range(1, 5)]
        for i in range(4):
            for j in range(i + 1, 4):
                csp.add_constraint(
                    Constraint(
                        [col_vars[i], col_vars[j]],
                        not_equal_constraint(col_vars[i], col_vars[j]),
                    )
                )


def add_subgrid_constraints(csp: CSP):
    # Додаємо обмеження для підгридів (підсіток)
    subgrid_starts = [(1, 1), (1, 3), (3, 1), (3, 3)]
    for start_row, start_col in subgrid_starts:
        subgrid_vars = [
            f"X{start_row + i}{start_col + j}" for i in range(2) for j in range(2)
        ]
        for i in range(4):
            for j in range(i + 1, 4):
                csp.add_constraint(
                    Constraint(
                        [subgrid_vars[i], subgrid_vars[j]],
                        not_equal_constraint(subgrid_vars[i], subgrid_vars[j]),
                    )
                )


def print_sudoku_solution(solution: Dict[str, int]):
    for row in range(1, 5):
        print(
            " ".join(
                str(solution.get(f"X{row}{col}", "_")) for col in range(1, 5)
            )
        )
    print()


def log(message: str, depth: int):
    indent = "    " * depth
    print(f"{indent}{message}")


def main():
    # Визначаємо змінні та домени
    variables = [f"X{i}{j}" for i in range(1, 5) for j in range(1, 5)]
    domains = {var: [1, 2, 3, 4] for var in variables}

    # Створюємо CSP
    csp = CSP(
        variables,
        domains,
        variable_heuristic="mrv",  # Використовуємо евристику MRV
        intermediate_assignment_hook=None,
    )

    # Додаємо обмеження
    add_row_constraints(csp)
    add_column_constraints(csp)
    add_subgrid_constraints(csp)

    # Початковий стан судоку
    initial_map = [
        [0, 3, 0, 0],
        [4, 0, 0, 0],
        [0, 0, 3, 2],
        [0, 0, 0, 0],
    ]

    # Початкове присвоєння
    initial_assignment = {
        f"X{row+1}{col+1}": initial_map[row][col]
        for row in range(4)
        for col in range(4)
        if initial_map[row][col] != 0
    }

    # Оновлюємо домени відповідно до початкового присвоєння
    for var, value in initial_assignment.items():
        csp.current_domains[var] = [value]

    print("Initial Assignment:")
    print_sudoku_solution(initial_assignment)

    # Розв'язуємо судоку
    solution = csp.backtrack(initial_assignment)

    print("Solution:")
    if solution:
        print_sudoku_solution(solution)
    else:
        print("No solution found.")


if __name__ == "__main__":
    main()
