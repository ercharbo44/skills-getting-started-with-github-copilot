"""
Tests for the FastAPI activity management application.
All tests follow the AAA (Arrange-Act-Assert) pattern.
"""
import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client):
        """
        Arrange: No additional setup needed (using default fixtures).
        Act: Make GET request to /activities.
        Assert: Verify response status is 200 and contains expected activities.
        """
        # Arrange
        # (no setup needed)

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        assert "Chess Club" in activities
        assert "Programming Class" in activities

    def test_get_activities_returns_correct_structure(self, client, valid_activity_name):
        """
        Arrange: No additional setup needed.
        Act: Make GET request and inspect activity structure.
        Assert: Verify each activity has required fields.
        """
        # Arrange
        # (no setup needed)

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        activity = activities[valid_activity_name]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)

    def test_get_activities_includes_existing_participants(self, client, valid_activity_name):
        """
        Arrange: Chess Club already has participants from fixtures.
        Act: Fetch activities.
        Assert: Verify participants list is populated.
        """
        # Arrange
        # (fixtures provide pre-populated activities)

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        participants = activities[valid_activity_name]["participants"]
        assert len(participants) > 0
        assert "michael@mergington.edu" in participants


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_success_adds_participant(
        self, client, valid_activity_name, valid_email
    ):
        """
        Arrange: Prepare valid activity name and new email.
        Act: POST signup request.
        Assert: Verify response success and participant added to activity.
        """
        # Arrange
        activity_name = valid_activity_name
        email = valid_email

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert email in result["message"]

        # Verify participant was added by fetching activities
        check_response = client.get("/activities")
        activities = check_response.json()
        assert email in activities[activity_name]["participants"]

    def test_signup_fails_activity_not_found(self, client, valid_email, invalid_activity_name):
        """
        Arrange: Prepare invalid activity name and valid email.
        Act: POST signup request with non-existent activity.
        Assert: Verify 404 error is returned.
        """
        # Arrange
        activity_name = invalid_activity_name
        email = valid_email

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 404
        result = response.json()
        assert "Activity not found" in result["detail"]

    def test_signup_fails_already_signed_up(self, client, valid_activity_name):
        """
        Arrange: Chess Club already has michael@mergington.edu.
        Act: Try to sign up the same email again.
        Assert: Verify 400 error for duplicate signup.
        """
        # Arrange
        activity_name = valid_activity_name
        email = "michael@mergington.edu"  # Already in Chess Club

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 400
        result = response.json()
        assert "already signed up" in result["detail"]

    def test_signup_multiple_students_to_same_activity(
        self, client, valid_activity_name, valid_email, another_email
    ):
        """
        Arrange: Two different new emails.
        Act: Sign up both to the same activity.
        Assert: Verify both are added to participants.
        """
        # Arrange
        activity_name = valid_activity_name

        # Act
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": valid_email},
        )
        response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": another_email},
        )

        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200

        check_response = client.get("/activities")
        activities = check_response.json()
        participants = activities[activity_name]["participants"]
        assert valid_email in participants
        assert another_email in participants


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/participants/{email} endpoint."""

    def test_unregister_success_removes_participant(self, client, valid_activity_name):
        """
        Arrange: Chess Club has michael@mergington.edu.
        Act: DELETE request to remove this participant.
        Assert: Verify response success and participant removed.
        """
        # Arrange
        activity_name = valid_activity_name
        email = "michael@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )

        # Assert
        assert response.status_code == 200
        result = response.json()
        assert email in result["message"]

        # Verify participant was removed
        check_response = client.get("/activities")
        activities = check_response.json()
        assert email not in activities[activity_name]["participants"]

    def test_unregister_fails_activity_not_found(self, client, valid_email, invalid_activity_name):
        """
        Arrange: Invalid activity name.
        Act: DELETE request with non-existent activity.
        Assert: Verify 404 error.
        """
        # Arrange
        activity_name = invalid_activity_name
        email = valid_email

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )

        # Assert
        assert response.status_code == 404
        result = response.json()
        assert "Activity not found" in result["detail"]

    def test_unregister_fails_participant_not_registered(
        self, client, valid_activity_name, valid_email
    ):
        """
        Arrange: valid_email is not registered for valid_activity_name.
        Act: DELETE request to remove non-existent participant.
        Assert: Verify 400 error.
        """
        # Arrange
        activity_name = valid_activity_name
        email = valid_email

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )

        # Assert
        assert response.status_code == 400
        result = response.json()
        assert "not registered" in result["detail"]

    def test_unregister_success_signup_again_after_removal(
        self, client, valid_activity_name, valid_email
    ):
        """
        Arrange: Sign up valid_email, then remove them.
        Act: Try to sign up the same email again.
        Assert: Verify re-signup succeeds (was not blocked by previous registration).
        """
        # Arrange
        activity_name = valid_activity_name

        # Sign up the user
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": valid_email},
        )

        # Remove the user
        client.delete(
            f"/activities/{activity_name}/participants/{valid_email}"
        )

        # Act: Try to sign up again
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": valid_email},
        )

        # Assert
        assert response.status_code == 200

        check_response = client.get("/activities")
        activities = check_response.json()
        assert valid_email in activities[activity_name]["participants"]
