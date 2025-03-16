import uuid
import datetime as dt
from typing import List, Dict, Any, Optional
from src.repositories.relationship_repository import RelationshipRepository
from src.models.relationship import Relationship

class RelationshipService:
    def __init__(self):
        self.relationship_repository: RelationshipRepository = RelationshipRepository()

    def get_relationship(self, relationship_id: str) -> Optional[Relationship]:
        """
        Retrieves a relationship by relationship_id

        :param relationship_id: The ID of the relationship to retrieve
        :return: The Relationship object if found, else None
        """
        relationship_data = self.relationship_repository.get_relationship(relationship_id)

        if relationship_data:
            return Relationship(**relationship_data)
        return None
    
    def get_relationships_for_coach(self, coach_id: str, status: Optional[str] = None) -> List[Relationship]:
        """
        Retrieves all relationships for a specific coach

        :param coach_id: The ID of the coach
        :param status: Optional status filter for the relationships
        :return: A list of Relationship objects
        """
        relationships_data = self.relationship_repository.get_relationships_for_coach(coach_id, status)
        return [Relationship(**relationship_data) for relationship_data in relationships_data]
    
    def get_active_relationship(self, coach_id: str, athlete_id: str) -> Optional[Relationship]:
        """
        Retrieves active relationship between coach and athlete if exists

        :param coach_id: The ID of the coach
        :param athlete_id: The ID of the athlete
        :return: The Relationship object if found, else None
        """
        relationship_data = self.relationship_repository.get_active_relationship(coach_id, athlete_id)
        if relationship_data:
            return Relationship(**relationship_data)
        return None
    
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
            status="pending", # Athlete must accept the relationship
            created_at=dt.datetime.now().isoformat()
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
        Ends a relationship

        :param relationship_id: The ID of the relationship to end
        :return: The updated Relationship object if found, else None
        """
        relationship = self.get_relationship(relationship_id)
        if not relationship or relationship.status not in ["pending", "active"]:
            return None
        
        return self.update_relationship(relationship_id, {"status": "ended"})
    
    def update_relationship(self, relationship_id: str, update_data: Dict[str, Any]) -> Optional[Relationship]:
        """
        Updates a relationship

        :param relationship_id: The ID of the relationship to update
        :param update_data: The data to update the relationship with
        :return: The updated Relationship object if found, else None
        """
        self.relationship_repository.update_relationship(relationship_id, update_data)
        return self.get_relationship(relationship_id)
    