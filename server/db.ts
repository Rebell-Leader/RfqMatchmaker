
<old_str>import { Pool, neonConfig } from '@neondatabase/serverless';
import { drizzle } from 'drizzle-orm/neon-serverless';
import ws from "ws";
import * as schema from "@shared/schema";

neonConfig.webSocketConstructor = ws;

if (!process.env.DATABASE_URL) {
  throw new Error(
    "DATABASE_URL must be set. Did you forget to provision a database?",
  );
}

export const pool = new Pool({ connectionString: process.env.DATABASE_URL });
export const db = drizzle({ client: pool, schema });</old_str>
<new_str>// Database operations are handled by Python backend
// This file is kept for compatibility but all DB operations
// should go through the Python API at http://localhost:8000

export const db = null; // Placeholder - not used</new_str>
