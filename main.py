from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class MustToLearn:
    group: str
    subject: str


@dataclass
class Lesson:
    group: str
    subject: str
    teacher: str | None = None
    day: str | None = None
    lesson_num: int | None = None
    auditorium: str | None = None


@dataclass
class Constraint:
    variables: list[str]
    condition: Callable[[dict[str, str]], bool]

    def is_satisfied(self, assignment: dict[str, str]) -> bool:
        return self.condition(assignment)


class CSP:
    def __init__(self, variables, domains):
        self.variables = variables
        self.domains = domains

    def solve(self):
        i = 0
        assignment = {}
        assignment, i = self.backtrack(assignment, i)
        return assignment or None, i

    def backtrack(self, assignment, i):
        i+=1
        if len(assignment) == len(csp.variables):
            return assignment, i

        var = self.select_unassigned_variable(assignment)

        for value in self.domains[var]:
            if self.is_consistent(var, value, assignment):
                assignment[var] = value

                result, i = self.backtrack(assignment, i)
                if result is not None:
                    return result, i

                del assignment[var]
        return None, i

    def is_consistent(self, var, value, assignment):
        assignment[var] = value
        constraints = [teacher_time_conflict_constraint, group_time_conflict_constraint,
                       auditorium_time_conflict_constraint]

        for constraint in constraints:
            if not constraint(assignment):
                del assignment[var]
                return False

        del assignment[var]
        return True

    def select_unassigned_variable(self, assignment):
        unassigned = [v for v in self.variables if v not in assignment]
        return min(unassigned, key=lambda var: len(self.domains[var]))


def teacher_time_conflict_constraint(assignment: dict[MustToLearn, Lesson]):
    for lesson in assignment.values():
        if any(lesson.teacher == other_lesson.teacher
               and lesson.day == other_lesson.day
               and lesson.lesson_num == other_lesson.lesson_num
               and (lesson.subject != other_lesson.subject
                    or lesson.group == other_lesson.group
                    or lesson.auditorium != other_lesson.auditorium)
               for other_lesson in assignment.values()
               if other_lesson != lesson):
            return False
    return True


def group_time_conflict_constraint(assignment: dict[MustToLearn, Lesson]):
    for lesson in assignment.values():
        if any(lesson.group == other_lesson.group
               and lesson.day == other_lesson.day
               and lesson.lesson_num == other_lesson.lesson_num
               for other_lesson in assignment.values()
               if other_lesson != lesson):
            return False
    return True


def auditorium_time_conflict_constraint(assignment: dict[MustToLearn, Lesson]):
    for lesson in assignment.values():
        if any(lesson.day == other_lesson.day
               and lesson.lesson_num == other_lesson.lesson_num
               and lesson.auditorium == other_lesson.auditorium
               and (lesson.subject != other_lesson.subject
                    or lesson.teacher != other_lesson.teacher)
               for other_lesson in assignment.values()
               if other_lesson != lesson):
            return False
    return True


if __name__ == "__main__":

    group_subjects_dict = {
        "МІ-41": ["ТПР", "Інформаційні технології", "Нейронні мережі", "Інтелектуальні системи", "Комп'ютерна лінгвістика", "Складність алгоритмів"],
        "МІ-42": ["ТПР", "Інформаційні технології", "Нейронні мережі", "Інтелектуальні системи", "Комп'ютерна лінгвістика", "Складність алгоритмів"],
        "К-14": ["АГ", "Мат аналіз", "Програмування", "Дискретна математика", "Англійська мова", "ВДУС"],
        "К-15": ["АГ", "Мат аналіз", "Програмування", "Дискретна математика", "Англійська мова", "ВДУС"],
        "К-16": ["АГ", "Мат аналіз", "Програмування", "Дискретна математика", "Англійська мова", "ВДУС"],
        "К-17": ["АГ", "Мат аналіз", "Програмування", "Дискретна математика", "Англійська мова", "ВДУС"],
        "Група1": ["Дисципліна1", "Дисципліна2", "Дисципліна3", "Дисципліна4", "Англійська мова", "ВДУС"],
        "Група2": ["Дисципліна1", "Дисципліна3", "Дисципліна5", "Дисципліна4"],
        "Група3": ["Дисципліна2", "Дисципліна3", "Дисципліна4", "Англійська мова"],
        "Група4": ["Дисципліна2", "Дисципліна4", "Дисципліна5", "ВДУС"],
    }

    subject_teachers_dict = {
        "ТПР": ["Мащенко"],
        "Інформаційні технології": ["Ткаченко"],
        "Нейронні мережі": ["Бобиль"],
        "Інтелектуальні системи": ["Мисечко", "Тарануха", "Федорус"],
        "Комп'ютерна лінгвістика": ["Тарануха"],
        "Складність алгоритмів": ["Вергунова"],
        "АГ": ["Маринич"],
        "Мат аналіз": ["Молодцов", "Анікушин"],
        "Програмування": ["Коваль", "Карнаух"],
        "Дискретна математика": ["Коваль", "Веклич"],
        "Англійська мова": ["Паламарчук"],
        "ВДУС": ["Набока"],
        "Дисципліна1": ["Викладач1", "Викладач2"],
        "Дисципліна2": ["Викладач2", "Викладач3"],
        "Дисципліна3": ["Викладач4"],
        "Дисципліна4": ["Викладач2", "Викладач4"],
        "Дисципліна5": ["Викладач4"],
    }

    # day = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    day = ["Monday", "Tuesday"]
    lesson_num = [1, 2, 3]
    auditorium = ["101", "102", "206", "207"]

    X = []
    for group in group_subjects_dict:
        for subject in group_subjects_dict[group]:
            X.append(MustToLearn(group, subject))

    D = {}

    for i, x_comb in enumerate(X):
        group = x_comb.group
        subject = x_comb.subject

        teachers = subject_teachers_dict.get(subject, [])

        possible_values = [
            Lesson(group=group, subject=subject, teacher=teacher, day=d, lesson_num=l, auditorium=a)
            for teacher in teachers
            for d in day
            for l in lesson_num
            for a in auditorium
        ]

        D[x_comb] = possible_values

    csp = CSP(X, D)
    solution, i = csp.solve()

    if solution:
        print("Розклад знайдено:")
        for key, value in solution.items():
            print(f"{key}: {value}")
    else:
        print("Розв'язок не знайдено")
    print("Length:", i)
