"""
Flow Powerlifting Data Factory

Generates realistic powerlifting training data for Flow app testing.
Matches exact DynamoDB schemas and API structures.

Usage:
    python flow_data_factory.py --output json --weeks 8
    python flow_data_factory.py --output api --env dev --persona complete
"""

import json
import uuid
import datetime as dt
import random
import argparse
import boto3
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum


class AthleteLevel(Enum):
    NOVICE = "novice"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


@dataclass
class AthleteProfile:
    level: AthleteLevel
    name: str
    email: str
    starting_maxes: Dict[str, float]  # squat, bench, deadlift in kg
    progression_rate: Dict[str, float]  # kg per 4-week block
    missed_session_rate: float  # 0.0-1.0
    rpe_accuracy: float  # variance in RPE reporting


class FlowDataFactory:
    """Generates realistic powerlifting training data matching Flow schemas"""

    def __init__(self):
        self.exercise_library = {
            "barbell": [
                "Squat",
                "Bench Press",
                "Deadlift",
                "Overhead Press",
                "Barbell Row",
                "Close Grip Bench Press",
                "Pause Squat",
                "Pause Bench Press",
                "Romanian Deadlift",
                "Front Squat",
            ],
            "dumbbell": [
                "Dumbbell Press",
                "Dumbbell Row",
                "Dumbbell Flyes",
                "Incline Dumbbell Press",
                "Dumbbell Romanian Deadlift",
            ],
            "bodyweight": ["Pull-ups", "Dips", "Push-ups", "Plank"],
            "machine": [
                "Leg Press",
                "Lat Pulldown",
                "Cable Row",
                "Leg Curl",
                "Leg Extension",
                "Tricep Pushdown",
            ],
        }

        self.athlete_profiles = self._create_athlete_profiles()

    def _create_athlete_profiles(self) -> Dict[AthleteLevel, AthleteProfile]:
        """Create predefined athlete personas"""
        return {
            AthleteLevel.NOVICE: AthleteProfile(
                level=AthleteLevel.NOVICE,
                name="Athlete 1",
                email="athlete1@example.com",
                starting_maxes={"squat": 100, "bench": 80, "deadlift": 120},
                progression_rate={"squat": 7.5, "bench": 5, "deadlift": 10},
                missed_session_rate=0.15,
                rpe_accuracy=1.5,
            ),
            AthleteLevel.INTERMEDIATE: AthleteProfile(
                level=AthleteLevel.INTERMEDIATE,
                name="Athlete 2",
                email="athlete2@example.com",
                starting_maxes={"squat": 150, "bench": 110, "deadlift": 180},
                progression_rate={"squat": 3.75, "bench": 2.5, "deadlift": 5},
                missed_session_rate=0.08,
                rpe_accuracy=0.75,
            ),
            AthleteLevel.ADVANCED: AthleteProfile(
                level=AthleteLevel.ADVANCED,
                name="Athlete 2",
                email="athlete2@example.com",
                starting_maxes={"squat": 175, "bench": 112, "deadlift": 190},
                progression_rate={"squat": 1.25, "bench": 1.25, "deadlift": 2.5},
                missed_session_rate=0.05,
                rpe_accuracy=0.25,
            ),
        }

    def generate_demo_scenario(self, weeks: int = 8) -> Dict[str, Any]:
        """Generate complete demo scenario with coach and athletes"""

        # Generate coach
        coach_id = str(uuid.uuid4())
        coach_data = {
            "user_id": coach_id,
            "email": "coach@example.com",
            "name": "Coach Demo",
            "role": "coach",
            "weight_unit_preference": "kg",
        }

        # Generate athletes with coach relationships
        novice_data = self._generate_athlete_journey(
            AthleteLevel.NOVICE, weeks, coach_id
        )
        intermediate_data = self._generate_athlete_journey(
            AthleteLevel.INTERMEDIATE, weeks, coach_id
        )
        advanced_data = self._generate_athlete_journey(
            AthleteLevel.ADVANCED, weeks
        )  # Self-coached

        # Generate relationships
        relationships = []
        for athlete_data in [novice_data, intermediate_data]:
            relationship_id = str(uuid.uuid4())
            relationships.append(
                {
                    "relationship_id": relationship_id,
                    "coach_id": coach_id,
                    "athlete_id": athlete_data["user"]["user_id"],
                    "status": "active",
                    "created_at": (
                        dt.datetime.now() - dt.timedelta(days=weeks * 7)
                    ).isoformat()
                    + "Z",
                }
            )

        # Combine all data
        return {
            "users": [
                coach_data,
                novice_data["user"],
                intermediate_data["user"],
                advanced_data["user"],
            ],
            "relationships": relationships,
            "blocks": novice_data["blocks"]
            + intermediate_data["blocks"]
            + advanced_data["blocks"],
            "weeks": novice_data["weeks"]
            + intermediate_data["weeks"]
            + advanced_data["weeks"],
            "days": novice_data["days"]
            + intermediate_data["days"]
            + advanced_data["days"],
            "workouts": novice_data["workouts"]
            + intermediate_data["workouts"]
            + advanced_data["workouts"],
            "exercises": novice_data["exercises"]
            + intermediate_data["exercises"]
            + advanced_data["exercises"],
            "summary": {
                "total_users": 4,
                "total_relationships": len(relationships),
                "total_blocks": len(novice_data["blocks"])
                + len(intermediate_data["blocks"])
                + len(advanced_data["blocks"]),
                "total_weeks": weeks,
                "total_workouts": len(novice_data["workouts"])
                + len(intermediate_data["workouts"])
                + len(advanced_data["workouts"]),
                "total_exercises": len(novice_data["exercises"])
                + len(intermediate_data["exercises"])
                + len(advanced_data["exercises"]),
            },
        }

    def _generate_athlete_journey(
        self, athlete_level: AthleteLevel, weeks: int, coach_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate complete training journey for an athlete"""

        profile = self.athlete_profiles[athlete_level]
        athlete_id = str(uuid.uuid4())

        # Generate user
        user_data = {
            "user_id": athlete_id,
            "email": profile.email,
            "name": profile.name,
            "role": "athlete",
            "weight_unit_preference": "kg",
        }

        # Generate training data
        start_date = dt.date.today() - dt.timedelta(days=weeks * 7)
        current_maxes = profile.starting_maxes.copy()

        # Calculate 4-week blocks
        num_blocks = max(1, weeks // 4)

        all_blocks = []
        all_weeks = []
        all_days = []
        all_workouts = []
        all_exercises = []

        for block_num in range(num_blocks):
            block_start = start_date + dt.timedelta(days=block_num * 28)
            block_end = block_start + dt.timedelta(days=27)

            # Generate block
            block_id = str(uuid.uuid4())
            block_data = {
                "block_id": block_id,
                "athlete_id": athlete_id,
                "coach_id": coach_id
                if coach_id
                else None,  # Ensure None instead of missing
                "title": f"Block {block_num + 1} - {profile.level.value.title()}",
                "description": f"4-week periodized training block",
                "start_date": block_start.isoformat(),
                "end_date": block_end.isoformat(),
                "status": "completed" if block_num < num_blocks - 1 else "active",
                "number_of_weeks": 4,
            }
            all_blocks.append(block_data)

            # Generate weeks for this block
            (
                block_weeks,
                block_days,
                block_workouts,
                block_exercises,
            ) = self._generate_block_training(
                block_id, athlete_id, block_start, current_maxes, profile
            )

            all_weeks.extend(block_weeks)
            all_days.extend(block_days)
            all_workouts.extend(block_workouts)
            all_exercises.extend(block_exercises)

            # Progress maxes after each block
            for lift in current_maxes:
                current_maxes[lift] += profile.progression_rate[lift]

        return {
            "user": user_data,
            "blocks": all_blocks,
            "weeks": all_weeks,
            "days": all_days,
            "workouts": all_workouts,
            "exercises": all_exercises,
        }

    def _generate_block_training(
        self,
        block_id: str,
        athlete_id: str,
        start_date: dt.date,
        current_maxes: Dict[str, float],
        profile: AthleteProfile,
    ) -> Tuple[List[Dict], List[Dict], List[Dict], List[Dict]]:
        """Generate 4 weeks of training for a block"""

        weeks = []
        days = []
        workouts = []
        exercises = []

        # Week periodization: deload, build, intensify, peak
        week_templates = [
            {"intensity": (0.60, 0.75), "rpe": (5, 6), "reps": (6, 9), "volume": 0.7},
            {"intensity": (0.70, 0.80), "rpe": (6, 7), "reps": (6, 9), "volume": 1.0},
            {"intensity": (0.80, 0.90), "rpe": (7, 8), "reps": (4, 6), "volume": 0.85},
            {"intensity": (0.85, 0.95), "rpe": (8, 9), "reps": (3, 5), "volume": 0.75},
        ]

        for week_num in range(4):
            week_start = start_date + dt.timedelta(days=week_num * 7)
            week_template = week_templates[week_num]

            # Generate week
            week_id = str(uuid.uuid4())
            week_data = {
                "week_id": week_id,
                "block_id": block_id,
                "week_number": week_num + 1,
                "notes": f"Week {week_num + 1} - {['Deload', 'Build', 'Intensify', 'Peak'][week_num]}",
            }
            weeks.append(week_data)

            # Generate 7 days for this week
            for day_num in range(7):
                day_date = week_start + dt.timedelta(days=day_num)
                day_id = str(uuid.uuid4())

                # Training days: Monday, Wednesday, Friday (0, 2, 4)
                training_days = [0, 2, 4]
                focus = ""
                if day_num in training_days:
                    focuses = ["squat", "bench", "deadlift"]
                    focus = focuses[training_days.index(day_num)]

                day_data = {
                    "day_id": day_id,
                    "week_id": week_id,
                    "day_number": day_num + 1,
                    "date": day_date.isoformat(),
                    "focus": focus if focus else None,
                    "notes": f"{focus.title()} Day" if focus else "Rest Day",
                }
                days.append(day_data)

                # Generate workout for training days (if not missed)
                if (
                    day_num in training_days
                    and random.random() > profile.missed_session_rate
                ):
                    workout_data, workout_exercises = self._generate_workout(
                        day_id,
                        athlete_id,
                        day_date,
                        focus,
                        week_template,
                        current_maxes,
                        profile,
                    )
                    workouts.append(workout_data)
                    exercises.extend(workout_exercises)

        return weeks, days, workouts, exercises

    def _generate_workout(
        self,
        day_id: str,
        athlete_id: str,
        date: dt.date,
        focus: str,
        week_template: Dict[str, Any],
        current_maxes: Dict[str, float],
        profile: AthleteProfile,
    ) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """Generate a single workout with exercises"""

        workout_id = str(uuid.uuid4())

        exercises = []
        order = 1

        # Main lift
        if focus in current_maxes:
            main_exercise = self._generate_main_lift(
                workout_id, focus, current_maxes[focus], week_template, profile, order
            )
            exercises.append(main_exercise)
            order += 1

        # Accessory exercises (2-3)
        num_accessories = random.randint(2, 3)
        for _ in range(num_accessories):
            accessory = self._generate_accessory(
                workout_id, focus, week_template, profile, order
            )
            exercises.append(accessory)
            order += 1

        # Calculate workout timing
        duration_minutes = random.randint(45, 90)
        start_time = dt.datetime.combine(date, dt.time(hour=random.randint(6, 20)))
        finish_time = start_time + dt.timedelta(minutes=duration_minutes)

        workout_data = {
            "workout_id": workout_id,
            "athlete_id": athlete_id,
            "day_id": day_id,
            "date": date.isoformat(),
            "notes": f"{focus.title()} focused session",
            "status": "completed",
            "start_time": start_time.isoformat() + "Z",
            "finish_time": finish_time.isoformat() + "Z",
        }

        return workout_data, exercises

    def _generate_main_lift(
        self,
        workout_id: str,
        lift_name: str,
        max_weight: float,
        week_template: Dict[str, Any],
        profile: AthleteProfile,
        order: int,
    ) -> Dict[str, Any]:
        """Generate main powerlifting exercise"""

        exercise_names = {
            "squat": "Squat",
            "bench": "Bench Press",
            "deadlift": "Deadlift",
        }

        # Calculate training parameters
        intensity_min, intensity_max = week_template["intensity"]
        rpe_min, rpe_max = week_template["rpe"]
        rep_min, rep_max = week_template["reps"]

        intensity = random.uniform(intensity_min, intensity_max)
        weight = round(max_weight * intensity / 2.5) * 2.5  # Round to 2.5kg

        reps = random.randint(rep_min, rep_max)
        sets = random.randint(3, 5) if reps <= 5 else random.randint(3, 4)

        # RPE with realistic range and increments
        def generate_realistic_rpe(
            base_min: float, base_max: float, variance: float
        ) -> float:
            """Generate RPE in 0.5 increments within 5.0-8.5 range"""
            base_rpe = random.uniform(base_min, base_max)
            # Add athlete variance
            adjusted_rpe = base_rpe + random.uniform(-variance, variance)
            # Clamp to realistic range
            clamped_rpe = max(5.0, min(8.5, adjusted_rpe))
            # Round to nearest 0.5
            return round(clamped_rpe * 2) / 2

        actual_rpe = generate_realistic_rpe(rpe_min, rpe_max, profile.rpe_accuracy)

        # Generate realistic sets_data for completed exercise
        sets_data = []
        for set_num in range(1, sets + 1):
            # Add some variance to individual sets
            set_weight = weight
            set_reps = reps
            set_rpe = actual_rpe

            # Add realistic variance for later sets (fatigue)
            if set_num > 1:
                # Small chance of weight reduction due to fatigue (round to 2.5kg)
                if random.random() < 0.15:
                    set_weight = round((weight - 2.5) / 2.5) * 2.5
                # Small chance of rep reduction due to fatigue
                if random.random() < 0.1:
                    set_reps = max(1, reps - 1)
                # RPE tends to increase with fatigue (in 0.5 increments)
                if set_num >= 3:
                    fatigue_rpe = actual_rpe + random.choice([0, 0.5])
                    set_rpe = min(8.5, fatigue_rpe)

            sets_data.append(
                {
                    "set_number": set_num,
                    "weight": set_weight,  # Keep as float, will be converted to Decimal later
                    "reps": int(set_reps),
                    "completed": True,
                    "rpe": set_rpe,
                    "timestamp": None,
                }
            )

        return {
            "exercise_id": str(uuid.uuid4()),
            "workout_id": workout_id,
            "exercise_type": exercise_names[lift_name],
            "sets": sets,
            "reps": reps,
            "weight": weight,  # Keep as float for now
            "status": "completed",
            "rpe": actual_rpe,
            "notes": f"Main lift - {intensity:.0%} 1RM",
            "order": order,
            "exercise_category": "barbell",
            "sets_data": sets_data,
        }

    def _generate_accessory(
        self,
        workout_id: str,
        focus: str,
        week_template: Dict[str, Any],
        profile: AthleteProfile,
        order: int,
    ) -> Dict[str, Any]:
        """Generate accessory exercise"""

        accessory_map = {
            "squat": ["Romanian Deadlift", "Leg Press", "Leg Curl", "Pull-ups"],
            "bench": ["Dumbbell Press", "Dumbbell Row", "Tricep Pushdown", "Dips"],
            "deadlift": ["Barbell Row", "Pull-ups", "Romanian Deadlift", "Leg Curl"],
        }

        exercise_options = accessory_map.get(focus, ["Dumbbell Press", "Barbell Row"])
        exercise_name = random.choice(exercise_options)

        # Determine category and realistic weight increments
        def round_weight(weight: float, category: str) -> float:
            """Round weight to realistic increments based on exercise type"""
            if category == "dumbbell":
                # Dumbbells typically in 2.5kg increments
                return round(weight / 2.5) * 2.5
            elif category == "bodyweight":
                return 0  # No weight for bodyweight
            elif category in ["machine", "barbell"]:
                # Plates in 2.5kg or 1.25kg increments
                return round(weight / 1.25) * 1.25
            else:
                return round(weight / 2.5) * 2.5

        if "Dumbbell" in exercise_name:
            category = "dumbbell"
            base_weight = random.uniform(12, 35)
            weight = round_weight(base_weight, category)
        elif exercise_name in ["Pull-ups", "Dips"]:
            category = "bodyweight"
            weight = 0
        elif exercise_name in ["Leg Press", "Tricep Pushdown", "Leg Curl"]:
            category = "machine"
            base_weight = random.uniform(40, 120)
            weight = round_weight(base_weight, category)
        else:
            category = "barbell"
            base_weight = random.uniform(40, 100)
            weight = round_weight(base_weight, category)

        # Accessory parameters - realistic rep ranges
        reps = random.randint(8, 12)  # Fixed to 8-12 range for accessories
        sets = random.randint(3, 4)

        # RPE with realistic range and increments for accessories
        def generate_realistic_rpe(
            base_min: float, base_max: float, variance: float
        ) -> float:
            """Generate RPE in 0.5 increments within 5.0-8.5 range"""
            base_rpe = random.uniform(base_min, base_max)
            adjusted_rpe = base_rpe + random.uniform(-variance, variance)
            clamped_rpe = max(5.0, min(8.5, adjusted_rpe))
            return round(clamped_rpe * 2) / 2

        rpe = generate_realistic_rpe(
            6.0, 7.5, profile.rpe_accuracy / 2
        )  # Accessories slightly easier

        # Generate realistic sets_data for completed accessory exercise
        sets_data = []
        for set_num in range(1, sets + 1):
            # Accessories show more rep variance due to lighter loads
            set_weight = weight
            set_reps = reps
            set_rpe = rpe

            # Add realistic variance for accessory work
            if set_num > 1:
                # More rep variance in accessories (8-12 range maintained)
                if random.random() < 0.25:
                    rep_variance = random.randint(-1, 2)
                    set_reps = max(8, min(12, reps + rep_variance))
                # RPE variance in 0.5 increments
                if set_num >= 3:
                    rpe_change = random.choice([-0.5, 0, 0.5])
                    set_rpe = max(5.0, min(8.5, rpe + rpe_change))

            sets_data.append(
                {
                    "set_number": set_num,
                    "weight": weight,  # Keep as float
                    "reps": int(set_reps),
                    "completed": True,
                    "rpe": set_rpe,
                    "timestamp": None,
                }
            )

        return {
            "exercise_id": str(uuid.uuid4()),
            "workout_id": workout_id,
            "exercise_type": exercise_name,
            "sets": sets,
            "reps": reps,
            "weight": weight,  # Keep as float
            "status": "completed",
            "rpe": rpe,
            "notes": "Accessory movement",
            "order": order,
            "exercise_category": category,
            "sets_data": sets_data,
        }

    def create_cognito_users(
        self, users: List[Dict[str, Any]], environment: str = "dev"
    ) -> Dict[str, bool]:
        """Create Cognito users for demo accounts"""

        cognito = boto3.client("cognito-idp")
        results = {}

        # Get User Pool ID from CloudFormation
        cf = boto3.client("cloudformation")
        try:
            stack_response = cf.describe_stacks(StackName=f"flow-data-{environment}")
            outputs = stack_response["Stacks"][0]["Outputs"]
            user_pool_id = next(
                item["OutputValue"]
                for item in outputs
                if item["OutputKey"] == "UserPoolId"
            )
        except Exception as e:
            print(f"❌ Failed to get User Pool ID: {str(e)}")
            return {}

        for user in users:
            try:
                email = user["email"]
                name = user["name"]
                role = user["role"]

                # Create user in Cognito (without custom:role - will be set in DynamoDB)
                response = cognito.admin_create_user(
                    UserPoolId=user_pool_id,
                    Username=email,
                    UserAttributes=[
                        {"Name": "email", "Value": email},
                        {"Name": "name", "Value": name},
                        {"Name": "email_verified", "Value": "true"},
                    ],
                    TemporaryPassword="Password.1",
                    MessageAction="SUPPRESS",  # Don't send welcome email
                )

                # Set permanent password
                cognito.admin_set_user_password(
                    UserPoolId=user_pool_id,
                    Username=email,
                    Password="Password.1",
                    Permanent=True,
                )

                results[email] = True
                print(f"✅ Created Cognito user: {email}")

            except cognito.exceptions.UsernameExistsException:
                results[email] = True  # User already exists, that's fine
                print(f"ℹ️  Cognito user already exists: {email}")

            except Exception as e:
                results[email] = False
                print(f"❌ Failed to create Cognito user {email}: {str(e)}")

        return results

    def insert_to_dynamodb(
        self, data: Dict[str, Any], environment: str = "dev"
    ) -> Dict[str, bool]:
        """Insert generated data into DynamoDB tables"""

        dynamodb = boto3.resource("dynamodb")
        results = {}

        # Table mapping
        tables = {
            "users": f"flow-{environment}-users",
            "relationships": f"flow-{environment}-relationships",
            "blocks": f"flow-{environment}-blocks",
            "weeks": f"flow-{environment}-weeks",
            "days": f"flow-{environment}-days",
            "workouts": f"flow-{environment}-workouts",
            "exercises": f"flow-{environment}-exercises",
        }

        for data_type, table_name in tables.items():
            if data_type in data and data[data_type]:
                try:
                    table = dynamodb.Table(table_name)

                    # Batch write items
                    items = data[data_type]
                    batch_size = 25  # DynamoDB batch limit

                    for i in range(0, len(items), batch_size):
                        batch = items[i : i + batch_size]

                        with table.batch_writer() as batch_writer:
                            for item in batch:
                                batch_writer.put_item(Item=item)

                    results[data_type] = True
                    print(f"✅ Inserted {len(items)} items into {table_name}")

                except Exception as e:
                    results[data_type] = False
                    print(f"❌ Failed to insert {data_type}: {str(e)}")

        return results


def main():
    parser = argparse.ArgumentParser(description="Generate Flow powerlifting demo data")
    parser.add_argument(
        "--output",
        choices=["json", "dynamodb"],
        default="json",
        help="Output format (default: json)",
    )
    parser.add_argument(
        "--weeks", type=int, default=8, help="Number of weeks to generate (default: 8)"
    )
    parser.add_argument(
        "--persona",
        choices=["novice", "intermediate", "advanced", "complete"],
        default="complete",
        help="Athlete persona (default: complete)",
    )
    parser.add_argument(
        "--env", default="dev", help="Environment for DynamoDB (default: dev)"
    )
    parser.add_argument("--output-file", help="Output file path")

    args = parser.parse_args()

    factory = FlowDataFactory()

    if args.persona == "complete":
        data = factory.generate_demo_scenario(args.weeks)
        filename_suffix = "complete"
    else:
        level = AthleteLevel(args.persona)
        athlete_data = factory._generate_athlete_journey(level, args.weeks)
        data = {
            "users": [athlete_data["user"]],
            "relationships": [],
            "blocks": athlete_data["blocks"],
            "weeks": athlete_data["weeks"],
            "days": athlete_data["days"],
            "workouts": athlete_data["workouts"],
            "exercises": athlete_data["exercises"],
            "summary": {"athlete_level": args.persona, "total_weeks": args.weeks},
        }
        filename_suffix = args.persona

    if args.output == "json":
        output_file = (
            args.output_file or f"flow_demo_data_{filename_suffix}_{args.weeks}w.json"
        )
        with open(output_file, "w") as f:
            json.dump(data, f, indent=2)
        print(f"✅ Generated {output_file}")
        print(f"📊 Summary: {data['summary']}")

    elif args.output == "dynamodb":
        print(
            f"🚀 Creating demo accounts and inserting data into DynamoDB environment: {args.env}"
        )

        # First create Cognito users
        print("\n1. Creating Cognito user accounts...")
        cognito_results = factory.create_cognito_users(data["users"], args.env)

        # Then insert DynamoDB data
        print("\n2. Inserting training data into DynamoDB...")
        db_results = factory.insert_to_dynamodb(data, args.env)

        # Summary
        cognito_success = sum(1 for success in cognito_results.values() if success)
        db_success = sum(1 for success in db_results.values() if success)

        print(f"\n📊 Summary:")
        print(f"   Cognito users: {cognito_success}/{len(data['users'])} created")
        print(f"   DynamoDB tables: {db_success}/{len(db_results)} populated")

        if cognito_success == len(data["users"]) and db_success == len(db_results):
            print("✅ Demo environment ready!")
        else:
            print("⚠️  Some operations failed - check AWS credentials and permissions")


if __name__ == "__main__":
    main()
