import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_all_activities(self, client):
        """Test that all activities are returned"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
        assert len(data) == 9
        
    def test_activity_has_required_fields(self, client):
        """Test that activities contain all required fields"""
        response = client.get("/activities")
        data = response.json()
        
        # Check one activity for all required fields
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_successful_signup(self, client):
        """Test that a student can successfully sign up for an activity"""
        response = client.post(
            "/activities/Chess%20Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        
        # Verify the participant was added
        activities_response = client.get("/activities")
        chess_club = activities_response.json()["Chess Club"]
        assert "newstudent@mergington.edu" in chess_club["participants"]
        
    def test_duplicate_signup_prevented(self, client):
        """Test that a student cannot sign up twice for the same activity"""
        # First signup should succeed
        response1 = client.post(
            "/activities/Chess%20Club/signup",
            params={"email": "test@mergington.edu"}
        )
        assert response1.status_code == 200
        
        # Second signup with same email should fail
        response2 = client.post(
            "/activities/Chess%20Club/signup",
            params={"email": "test@mergington.edu"}
        )
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]
        
    def test_signup_nonexistent_activity(self, client):
        """Test that signup for nonexistent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent%20Activity/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
        
    def test_signup_already_registered_student(self, client):
        """Test that an already registered student cannot sign up again"""
        # michael@mergington.edu is already in Chess Club
        response = client.post(
            "/activities/Chess%20Club/signup",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]


class TestUnregister:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_successful_unregister(self, client):
        """Test that a student can successfully unregister from an activity"""
        # michael@mergington.edu is in Chess Club
        response = client.delete(
            "/activities/Chess%20Club/unregister",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
        
        # Verify the participant was removed
        activities_response = client.get("/activities")
        chess_club = activities_response.json()["Chess Club"]
        assert "michael@mergington.edu" not in chess_club["participants"]
        
    def test_unregister_nonparticipant(self, client):
        """Test that unregistering a non-participant returns 400"""
        response = client.delete(
            "/activities/Chess%20Club/unregister",
            params={"email": "notastudent@mergington.edu"}
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]
        
    def test_unregister_from_nonexistent_activity(self, client):
        """Test that unregistering from nonexistent activity returns 404"""
        response = client.delete(
            "/activities/Nonexistent%20Activity/unregister",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
        
    def test_signup_then_unregister(self, client):
        """Test the full flow of signing up and then unregistering"""
        email = "testuser@mergington.edu"
        
        # Sign up
        signup_response = client.post(
            "/activities/Art%20Club/signup",
            params={"email": email}
        )
        assert signup_response.status_code == 200
        
        # Verify signed up
        activities = client.get("/activities").json()
        assert email in activities["Art Club"]["participants"]
        
        # Unregister
        unregister_response = client.delete(
            "/activities/Art%20Club/unregister",
            params={"email": email}
        )
        assert unregister_response.status_code == 200
        
        # Verify unregistered
        activities = client.get("/activities").json()
        assert email not in activities["Art Club"]["participants"]
