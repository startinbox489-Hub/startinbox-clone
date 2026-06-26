import "server-only";
import serverConfig from "../config/private";

export default class NewsLetterService {
  static async subscribeToNewsletter(
    email: string,
    name?: string,
  ): Promise<string> {
    try {
      const response = await fetch(
        `${await serverConfig("BACKEND_BASE_URL")}/api/v1/newsletters`,
        {
          method: "POST",
          body: JSON.stringify({ email, name }),
          credentials: "include",
        },
      );

      if (response.status === 409) {
        return "Email is already subscribed to the newsletter";
      }
      if (response.status > 499) {
        return "Internal Server Error. Please contact us with code #nl002";
      }
      return "Thank you for subscribing to our News Letter.";
    } catch (error) {
      console.error("error subscribing to newsletter: ", error);
      return "Internal Server Error. Please contact us with code #nl002";
    }
  }

  static async unSubscribeToNewsletter(email: string): Promise<string> {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_APP_URL}/api/v1/newsletters`,
        {
          method: "PATCH",
          body: JSON.stringify({ email }),
          credentials: "include",
        },
      );

      if (response.status === 404) {
        // This email is not yet subscribed to the newsletter
        return "Email is already unsubscribed or not subscribed to our Newsletter";
      }
      if (response.status > 499) {
        return "Internal Server Error. Please contact us with code #nl002.1";
      }
      return "Email is unsubscribed from our News Letter.";
    } catch (error) {
      console.error("error unsubscribing to newsletter: ", error);
      return "Internal Server Error. Please contact us with code #nl002.1";
    }
  }
}
