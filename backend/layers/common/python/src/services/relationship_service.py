import uuid
import datetime as dt
from datetime import timedelta
import random
import string
import time
from typing import List, Dict, Any, Optional
from src.repositories.relationship_repository import RelationshipRepository
from src.models.relationship import Relationship
from src.config.relationship_config import RelationshipConfig


class RelationshipService:
    def __init__(self):
        self.relationship_repository: RelationshipRepository = RelationshipRepository()

    def get_relationship(self, relationship_id: str) -> Optional[Relationship]:
        """
        Retrieves a relationship by relationship_id

        :param relationship_id: The ID of the relationship to retrieve
        :return: The Relationship object if found, else None
        """
        relationship_data = self.relationship_repository.get_relationship(
            relationship_id
        )

        if relationship_data:
            return Relationship(**relationship_data)
        return None

    def get_relationships_for_coach(
        self, coach_id: str, status: Optional[str] = None
    ) -> List[Relationship]:
        """
        Retrieves all relationships for a specific coach

        :param coach_id: The ID of the coach
        :param status: Optional status filter for the relationships
        :return: A list of Relationship objects
        """
        relationships_data = self.relationship_repository.get_relationships_for_coach(
            coach_id, status
        )
        return [
            Relationship(**relationship_data)
            for relationship_data in relationships_data
        ]

    def get_relationships_for_athlete(
        self, athlete_id: str, status: Optional[str] = None
    ) -> List[Relationship]:
        """
        Retrieves all relationships for a specific athlete

        :param athlete_id: The ID of the athlete
        :param status: Optional status filter for the relationships
        :return: A list of Relationship objects
        """
        relationships_data = self.relationship_repository.get_relationships_for_athlete(
            athlete_id, status
        )
        return [
            Relationship(**relationship_data)
            for relationship_data in relationships_data
        ]

    def get_active_relationship(
        self, coach_id: str, athlete_id: str
    ) -> Optional[Relationship]:
        """
        Retrieves active relationship between coach and athlete if exists

        :param coach_id: The ID of the coach
        :param athlete_id: The ID of the athlete
        :return: The Relationship object if found, else None
        """
        relationship_data = self.relationship_repository.get_active_relationship(
            coach_id, athlete_id
        )
        if relationship_data:
            return Relationship(**relationship_data)
        return None

    def generate_invitation_code(self, coach_id: str) -> Relationship:
        """
        Generates a unique invitation code for a coach to invite an athlete

        :param coach_id: The ID of the coach
        :return: The created Relationship object with invitation code
        """
        # Generate random alphanumeric code (6 characters)
        code = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

        # Calculate TTL for 24 hours from now (Unix timestamp)
        ttl_timestamp = int((dt.datetime.now() + timedelta(hours=24)).timestamp())

        # Create a pending relationship with the code
        relationship = Relationship(
            relationship_id=str(uuid.uuid4()),
            coach_id=coach_id,
            status="pending",
            invitation_code=code,
            ttl=ttl_timestamp,  # DynamoDB TTL field
        )

        self.relationship_repository.create_relationship(relationship.to_dict())
        return relationship

    def validate_invitation_code(
        self, invitation_code: str, athlete_id: str
    ) -> Optional[Relationship]:
        """
        Validates an invitation code and converts it to an active relationship

        :param invitation_code: The invitation code to validate
        :param athlete_id: The ID of the athlete accepting the invitation
        :return: The accepted Relationship object if valid, None otherwise
        """
        # Check if athlete already has an active relationship
        existing = self.relationship_repository.get_active_relationship_for_athlete(
            athlete_id
        )
        if existing:
            raise ValueError("Athlete already has an active coach relationship")

        # Find the relationship by code
        relationship_data = self.relationship_repository.get_relationship_by_code(
            invitation_code
        )

        if not relationship_data:
            raise ValueError("INVALID_CODE")

        # Check if code is expired (manual check before DynamoDB TTL cleanup)
        current_time = int(time.time())
        ttl_time = relationship_data.get("ttl", 0)

        if ttl_time < current_time:
            raise ValueError("EXPIRED_CODE")

        # Update the relationship to active (removes TTL and invitation code)
        update_data = {
            "athlete_id": athlete_id,
            "status": "active",
            "invitation_code": None,  # Clear the code once used
            "ttl": None,  # Remove TTL for active relationships
        }

        relationship_id = relationship_data["relationship_id"]
        updated = self.update_relationship(relationship_id, update_data)

        return updated

    def create_relationship(self, coach_id: str, athlete_id: str) -> Relationship:
        """
        Creates a new relationship

        :param coach_id: The ID of the coach
        :param athlete_id: The ID of the athlete
        :return: The created Relationship object
        """
        # Check if there's an active relationship
        existing = self.get_active_relationship(coach_id, athlete_id)

        if existing:
            return existing

        # Create new relationship
        relationship = Relationship(
            relationship_id=str(uuid.uuid4()),
            coach_id=coach_id,
            athlete_id=athlete_id,
            status="pending",  # Athlete must accept the relationship
            created_at=dt.datetime.now().isoformat(),
        )

        self.relationship_repository.create_relationship(relationship.to_dict())
        return relationship

    def accept_relationship(self, relationship_id: str) -> Optional[Relationship]:
        """
        Accepts a relationship

        :param relationship_id: The ID of the relationship to accept
        :return: The updated Relationship object if found, else None
        """
        relationship = self.get_relationship(relationship_id)
        if not relationship or relationship.status != "pending":
            return None

        return self.update_relationship(relationship_id, {"status": "active"})

    def end_relationship(self, relationship_id: str) -> Optional[Relationship]:
        """
        Ends a relationship and sets TTL for 60-day cleanup

        :param relationship_id: The ID of the relationship to end
        :return: The updated Relationship object if found, else None
        """
        relationship = self.get_relationship(relationship_id)
        if not relationship or relationship.status not in ["pending", "active"]:
            return None

        # Calculate TTL for 60 days from now (Unix timestamp)
        ttl_timestamp = int((dt.datetime.now() + timedelta(days=60)).timestamp())

        return self.update_relationship(
            relationship_id,
            {"status": "ended", "ttl": ttl_timestamp},  # Set TTL for automatic cleanup
        )

    def update_relationship(
        self, relationship_id: str, update_data: Dict[str, Any]
    ) -> Optional[Relationship]:
        """
        Updates a relationship

        :param relationship_id: The ID of the relationship to update
        :param update_data: The data to update the relationship with
        :return: The updated Relationship object if found, else None
        """
        self.relationship_repository.update_relationship(relationship_id, update_data)
        return self.get_relationship(relationship_id)
