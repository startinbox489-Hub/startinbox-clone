import {
  isEmail,
  isLowercase,
  isNumber,
  isPhoneNumber,
  isUppercase,
} from "class-validator";

export default class AuthServiceClient {
  static validatePassword(
    password: string,
    confirmPassword?: string,
  ): string | boolean {
    let hasLowerCase = false;
    let hasUpperCase = false;
    let hasDigit = false;
    let hasSpecialChar = false;
    for (const char of password) {
      if (isLowercase(char)) {
        hasLowerCase = true;
      }
      if (isUppercase(char)) {
        hasUpperCase = true;
      }
      if (isNumber(parseInt(char, 10))) {
        hasDigit = true;
      }
      if (
        [
          "`",
          "!",
          "@",
          "#",
          "$",
          "%",
          "^",
          "&",
          "*",
          "(",
          ")",
          "_",
          "-",
          "=",
          "+",
          "'",
          ";",
          ":",
        ].includes(char)
      ) {
        hasSpecialChar = true;
      }
    }
    if (password.length < 8) {
      return "password must have length up to 8 characters.";
    }
    if (!hasDigit) {
      return "password must contain at least one digit character.";
    }
    if (!hasLowerCase) {
      return "password must have at least one lowercase character.";
    }
    if (!hasUpperCase) {
      return "password must have at least one uppercase character.";
    }
    if (!hasSpecialChar) {
      return "password must have at least one special character.";
    }
    if (confirmPassword) {
      if (password !== confirmPassword) {
        return "passwords do not match.";
      }
    }

    return true;
  }

  static validateEmail(email: string): string | boolean {
    if (!isEmail(email)) {
      return "email must be valid";
    }
    return true;
  }

  static validatePhoneNumber(
    phoneNumber: string,
    countryCode: string,
  ): string | boolean {
    console.log(`${countryCode}${phoneNumber}`);
    if (!isPhoneNumber(`${countryCode}${phoneNumber}`)) {
      return "Contact Number is not valid.";
    }
    return true;
  }
}
