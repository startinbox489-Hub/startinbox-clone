import PublicConfig, { PublicConfigKeys } from "./public";
import serverConfig, { PrivateConfigKeys } from "./private";

type d = "BACKEND_BASE_URL" | "GOOGLE_CLIENT_ID" | "GOOGLE_CLIENT_SECRET";
export default class ConfigService {
  static PUBLIC = PublicConfig;
  static PRIVATE = serverConfig;

  static async get<K extends PublicConfigKeys>(
    key: K,
    defaultValue?: (typeof PublicConfig)["values"][K],
  ): Promise<(typeof PublicConfig)["values"][K]>;

  static async get<K extends PrivateConfigKeys>(
    key: K,
    defaultValue?: PrivateConfigKeys,
  ): Promise<PrivateConfigKeys>;

  static async get(
    key: PublicConfigKeys | PrivateConfigKeys,
    defaultValue?: string,
  ): Promise<string | undefined> {
    if (key in PublicConfig.values) {
      return PublicConfig.values[key as PublicConfigKeys] ?? defaultValue;
    }

    return await serverConfig(key as PrivateConfigKeys, defaultValue);

    // throw new Error(`❌ Config Error: Unknown key "${key}"`);
  }
}
