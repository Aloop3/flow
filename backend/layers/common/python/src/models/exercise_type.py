from enum import Enum
from typing import Dict, List, Optional


class ExerciseCategory(Enum):
    """
    Category of exercises
    """

    BARBELL = "barbell"
    DUMBBELL = "dumbbell"
    BODYWEIGHT = "bodyweight"
    MACHINE = "machine"
    CABLE = "cable"
    CUSTOM = "custom"


class ExerciseType:
    """
    Represents a type of exercise with standardized name and category

    Allows for both predefined exercise types and custom user-defined exercise types to coexist
    """

    PREDEFINED_EXERCISES: Dict[ExerciseCategory, List[str]] = {
        ExerciseCategory.BARBELL: [
            "Bench Press",
            "Squat",
            "Deadlift",
            "Low Bar Squat",
            "High Bar Squat",
            "Close Grip Bench Press",
            "Romanian Deadlift",
            "Hip Thrust",
            "Shoulder Press",
            "Bent Over Row",
            "Incline Bench Press",
            "Front Squat",
            "Military Press",
            "EZ Bar Curl",
            "Seated Shoulder Press",
            "Decline Bench Press",
        ],
        ExerciseCategory.DUMBBELL: [
            "Dumbbell Bench Press",
            "Dumbbell Lateral Raise",
            "Dumbbell Bicep Curl",
            "Seated Dumbbell Shoulder Press",
            "Dumbbell Shoulder Press",
            "Incline Dumbbell Bench Press",
            "Dumbbell Row",
            "Hammer Curl",
            "Dumbbell Bulgarian Split Squat",
            "Goblet Squat",
            "Dumbbell Fly",
            "Dumbbell Shrug",
            "Dumbbell Lunge",
            "Dumbbell Tricep Extension",
        ],
        ExerciseCategory.BODYWEIGHT: [
            "Pull Ups",
            "Push Ups",
            "Dips",
            "Chin Ups",
            "Planks",
            "Side Planks",
        ],
        ExerciseCategory.MACHINE: [
            "T Bar Row",
            "Leg Extension",
            "Iso-Lateral Chest Press",
            "Hack Squat",
            "Seated Leg Curl",
            "Machine Chest Fly",
            "Machine Shoulder Press",
            "Lying Leg Curl",
            "Machine Calf Raise",
            "Machine Low Row",
        ],
        ExerciseCategory.CABLE: [
            "Lat Pulldown",
            "Tricep Pushdown",
            "Seated Cable Row",
            "Tricep Rope Pushdown",
            "Cable Bicep Curl",
        ],
    }

    # Flat list of all predefined exercise names for quick lookup
    _ALL_PREDEFINED_NAMES = []

    for category_exercises in PREDEFINED_EXERCISES.values():
        for exercise in category_exercises:
            _ALL_PREDEFINED_NAMES.append(exercise)

    def __init__(self, name: str, category: Optional[ExerciseCategory] = None):
        """
        Initialize an exercise type with a name and optional category

        :param name: Name of the exercise
        :param category: Optional category for custom exercises
        """
        # Clean up leading and trailing whitespace
        self.name = name.strip()

        # Track if we found a match
        found_match = False

        # Find matching predefined exercise (case-insensitive)
        normalized_name = self.name.lower()
        for predefined_name in self._ALL_PREDEFINED_NAMES:
            if normalized_name == predefined_name.lower():
                # Use the correcly cased predefined name
                self.name = predefined_name

                # Find the category of this predefined exercise
                for (
                    exercise_category,
                    exercise_list,
                ) in self.PREDEFINED_EXERCISES.items():
                    if predefined_name in exercise_list:
                        self.category = exercise_category
                        found_match = True
                        break

                if found_match:
                    break

        if found_match:
            self.is_predefined = True
        else:
            # Custom exercise
            self.category = category or ExerciseCategory.CUSTOM
            self.is_predefined = False

    @classmethod
    def get_all_predefined(cls) -> List[str]:
        """
        Get a list of all predefined exercise names
        """
        return cls._ALL_PREDEFINED_NAMES.copy()  # prevent external modification

    @classmethod
    def get_by_category(cls, category: ExerciseCategory) -> List[str]:
        """
        Get all predefined exercises in a specific category

        :param category: Category to filter exercises by
        """
        return cls.PREDEFINED_EXERCISES.get(
            category, []
        ).copy()  # prevent external modification

    @classmethod
    def is_valid_predefined(cls, name: str) -> bool:
        """
        Check if a name is a valid predefined exercise

        :param name: Name to check
        """
        normalized_name = name.strip().lower()
        return any(
            predefined.lower() == normalized_name
            for predefined in cls._ALL_PREDEFINED_NAMES
        )

    @staticmethod
    def get_categories() -> List[ExerciseCategory]:
        """
        Get all available exercise categories
        """
        return list(ExerciseCategory)

    def __str__(self) -> str:
        """
        String representation of the exercise type
        """
        return self.name

    def __eq__(self, other) -> bool:
        """
        Two ExerciseType objects are equal if their names match (case-insensitive).
        Compares the ExerciseType's name with a string or another ExerciseType object.

        :param other: Other ExerciseType object or string to compare with
        """
        if isinstance(other, ExerciseType):
            return self.name.lower() == other.name.lower()
        elif isinstance(other, str):
            return self.name.lower() == other.lower()
        return False
