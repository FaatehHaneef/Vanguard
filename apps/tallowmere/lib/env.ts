import { z } from "zod";

/**
 * Server-side environment. Parsed lazily so that builds do not need secrets, and so
 * that a missing value fails with a clear message at the point of use.
 */

const serverEnvSchema = z.object({
  BRAINTREE_MERCHANT_ID: z.string().min(1),
  BRAINTREE_PUBLIC_KEY: z.string().min(1),
  BRAINTREE_PRIVATE_KEY: z.string().min(1),
  /** Optional. If present it must say "sandbox". See lib/guards/sandbox.ts. */
  PAYMENTS_ENVIRONMENT: z.string().optional(),
});

export type ServerEnv = z.infer<typeof serverEnvSchema>;

type EnvSource = Record<string, string | undefined>;

export function parseServerEnv(source: EnvSource): ServerEnv {
  const result = serverEnvSchema.safeParse(source);
  if (!result.success) {
    const missing = result.error.issues.map((issue) => issue.path.join(".")).join(", ");
    throw new Error(`Missing or invalid environment variables: ${missing}. See .env.example.`);
  }
  return result.data;
}

let cached: ServerEnv | undefined;

export function getServerEnv(): ServerEnv {
  cached ??= parseServerEnv(process.env);
  return cached;
}
