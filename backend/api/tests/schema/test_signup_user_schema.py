"""
TestSignupUserSchema
"""

import pytest
from pydantic import ValidationError

from api.schema.user_schema import SignupRequestSchema


class TestSignupUserSchema:
    """
    Test signup user schema
    """

    def test_valid_signup_with_phone(self):
        """
        test valid signup with phone
        """
        data = {
            "email": "Johnson@gmail.com",
            "password": "ValidPass1!",
            "confirm_password": "ValidPass1!",
            "phone_number": "+2347064712188",
            "agreed_to_terms": True,
        }
        req = SignupRequestSchema(**data)
        assert req.email == "Johnson@gmail.com"
        assert req.phone_number == "+2347064712188"

    def test_valid_signup_without_phone(self):
        """
        test valid signup without phone
        """
        data = {
            "email": "user@example.com",
            "password": "ValidPass1!",
            "confirm_password": "ValidPass1!",
            "agreed_to_terms": True,
        }
        req = SignupRequestSchema(**data)
        assert req.phone_number is None

    def test_invalid_signup_invalid_phone_number(self):
        """
        test validate schema
        """

        with pytest.raises(ValidationError) as exc:
            SignupRequestSchema(
                password="Johnson1#",
                confirm_password="Johnson1#",
                email="johnson@gmail.com",
                phone_number="07065656565",  # missing +countrycode
                agreed_to_terms=True,
            )

        assert "Phone number must be in valid international format (E.164)" in str(
            exc.value
        )

    def test_password_mismatch(self):
        """
        test password mismatch
        """
        data = {
            "email": "johnson@gmail.com",
            "password": "ValidPass1!",
            "confirm_password": "DifferentPass1!",
            "phone_number": "+2347064712188",
            "agreed_to_terms": True,
        }
        with pytest.raises(ValidationError) as exc:
            SignupRequestSchema(**data)

        assert "password and confirm_password must match" in str(exc.value)

    def test_password_missing_lowercase(self):
        """
        test password missing lowercase
        """
        data = {
            "email": "johnson@gmail.com",
            "password": "VALIDPASSP1!",
            "confirm_password": "VALIDPASSP1!",
            "phone_number": "+2347064712188",
            "agreed_to_terms": True,
        }
        with pytest.raises(ValidationError) as exc:
            SignupRequestSchema(**data)

        assert "password must contain at least one lowercase letter" in str(exc.value)

    def test_password_missing_uppercase(self):
        """
        test password missing uppercase
        """
        data = {
            "email": "johnson@gmail.com",
            "password": "validpassword1!",
            "confirm_password": "validpassword1!",
            "phone_number": "+2347064712188",
            "agreed_to_terms": True,
        }
        with pytest.raises(ValidationError) as exc:
            SignupRequestSchema(**data)

        assert "password must contain at least one uppercase letter" in str(exc.value)

    def test_password_missing_digit(self):
        """
        test password missing digit
        """
        data = {
            "email": "johnson@gmail.com",
            "password": "validpassword!",
            "confirm_password": "validpassword!",
            "phone_number": "+2347064712188",
            "agreed_to_terms": True,
        }
        with pytest.raises(ValidationError) as exc:
            SignupRequestSchema(**data)

        assert "password must contain at least one digit" in str(exc.value)

    def test_password_missing_special_char(self):
        """
        test password missing special char
        """
        data = {
            "email": "johnson@gmail.com",
            "password": "validpasswordS1",
            "confirm_password": "validpasswordS1",
            "phone_number": "+2347064712188",
            "agreed_to_terms": True,
        }
        with pytest.raises(ValidationError) as exc:
            SignupRequestSchema(**data)

        assert "password must contain at least one special character" in str(exc.value)

    def test_password_length(self):
        """
        test password length
        """
        data = {
            "email": "johnson@gmail.com",
            "password": "Sho1@",
            "confirm_password": "Sho1@",
            "phone_number": "+2347064712188",
            "agreed_to_terms": True,
        }
        with pytest.raises(ValidationError) as exc:
            SignupRequestSchema(**data)

        assert "String should have at least 8 characters" in str(exc.value)
