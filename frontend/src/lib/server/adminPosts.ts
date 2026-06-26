import { proxyWithAuth } from "./apiProxy";

export default class AdminPostsService {
  static async getPosts(path: string) {
    console.log("path: ", path);
    return await proxyWithAuth(path);
  }
}
