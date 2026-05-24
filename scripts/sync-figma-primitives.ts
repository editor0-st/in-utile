/**
 * Syncs primitive color tokens from a W3C-format .tokens.json file
 * into a Figma file as Variables using the Figma Variables REST API.
 *
 * Usage:
 *   FIGMA_TOKEN=figd_... FIGMA_FILE_KEY=0Ycf5NiD6I082kykCLEvVA npx tsx scripts/sync-figma-primitives.ts [tokens.json]
 *
 * The script will:
 *   1. GET existing variable collections in the file
 *   2. Find or create a collection named "Primitives"
 *   3. Create or UPDATE all color/string variables, grouped by their top-level key
 */

import fs from "fs";
import path from "path";

// ── Config ────────────────────────────────────────────────────────────────────

const TOKEN = process.env.FIGMA_TOKEN;
const FILE_KEY = process.env.FIGMA_FILE_KEY ?? "0Ycf5NiD6I082kykCLEvVA";
const COLLECTION_NAME = "Primitives";
const TOKEN_FILE =
  process.argv[2] ??
  path.resolve(import.meta.dirname, "../007383c9-Mode_1.tokens.json");

if (!TOKEN) {
  console.error(
    "Error: FIGMA_TOKEN environment variable is required.\n" +
      "  export FIGMA_TOKEN=figd_..."
  );
  process.exit(1);
}

const BASE = "https://api.figma.com/v1";
const headers = {
  "X-Figma-Token": TOKEN,
  "Content-Type": "application/json",
};

// ── Types ─────────────────────────────────────────────────────────────────────

interface TokenColorValue {
  colorSpace: string;
  components: [number, number, number];
  alpha: number;
  hex: string;
}

interface TokenEntry {
  $type: "color" | "string";
  $value: TokenColorValue | string;
  $extensions?: {
    "com.figma.variableId"?: string;
    "com.figma.scopes"?: string[];
    "com.figma.type"?: string;
  };
}

interface FigmaRGBA {
  r: number;
  g: number;
  b: number;
  a: number;
}

interface FigmaVariableCollection {
  id: string;
  name: string;
  modes: { modeId: string; name: string }[];
  defaultModeId: string;
  variableIds: string[];
}

interface FigmaVariable {
  id: string;
  name: string;
  resolvedType: "COLOR" | "STRING" | "FLOAT" | "BOOLEAN";
  variableCollectionId: string;
  valuesByMode: Record<string, unknown>;
}

interface LocalVariablesResponse {
  status: number;
  error: boolean;
  meta: {
    variableCollections: Record<string, FigmaVariableCollection>;
    variables: Record<string, FigmaVariable>;
  };
}

// ── Flatten tokens ─────────────────────────────────────────────────────────────

/** Returns a flat list of { name, type, value } from the tokens JSON. */
function flattenTokens(
  raw: Record<string, unknown>
): { name: string; type: "COLOR" | "STRING"; value: FigmaRGBA | string }[] {
  const out: {
    name: string;
    type: "COLOR" | "STRING";
    value: FigmaRGBA | string;
  }[] = [];

  for (const [group, groupValue] of Object.entries(raw)) {
    if (group === "$extensions") continue;
    if (typeof groupValue !== "object" || groupValue === null) continue;

    for (const [step, stepValue] of Object.entries(
      groupValue as Record<string, unknown>
    )) {
      if (step === "$extensions") continue;
      const entry = stepValue as TokenEntry;
      if (!entry.$type) continue;

      const name = `${group}/${step}`;

      if (entry.$type === "color") {
        const v = entry.$value as TokenColorValue;
        out.push({
          name,
          type: "COLOR",
          value: {
            r: v.components[0],
            g: v.components[1],
            b: v.components[2],
            a: v.alpha,
          },
        });
      } else if (entry.$type === "string") {
        out.push({ name, type: "STRING", value: entry.$value as string });
      }
    }
  }

  return out;
}

// ── Figma API helpers ─────────────────────────────────────────────────────────

async function getLocalVariables(): Promise<LocalVariablesResponse> {
  const res = await fetch(`${BASE}/files/${FILE_KEY}/variables/local`, {
    headers,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`GET variables/local failed (${res.status}): ${text}`);
  }
  return res.json() as Promise<LocalVariablesResponse>;
}

async function postVariables(payload: unknown): Promise<unknown> {
  const res = await fetch(`${BASE}/files/${FILE_KEY}/variables`, {
    method: "POST",
    headers,
    body: JSON.stringify(payload),
  });
  const json = await res.json();
  if (!res.ok) {
    throw new Error(
      `POST variables failed (${res.status}): ${JSON.stringify(json, null, 2)}`
    );
  }
  return json;
}

// ── Main ──────────────────────────────────────────────────────────────────────

async function main() {
  // 1. Load tokens
  if (!fs.existsSync(TOKEN_FILE)) {
    console.error(`Token file not found: ${TOKEN_FILE}`);
    process.exit(1);
  }
  const raw = JSON.parse(fs.readFileSync(TOKEN_FILE, "utf-8")) as Record<
    string,
    unknown
  >;
  const tokens = flattenTokens(raw);
  console.log(`Loaded ${tokens.length} tokens from ${path.basename(TOKEN_FILE)}`);

  // 2. Fetch current state
  console.log(`\nFetching existing variables from file ${FILE_KEY}…`);
  const existing = await getLocalVariables();
  const collections = existing.meta.variableCollections;
  const variables = existing.meta.variables;

  // 3. Find or create "Primitives" collection
  let collection = Object.values(collections).find(
    (c) => c.name === COLLECTION_NAME
  );
  let modeId: string;
  const tempCollectionId = "temp:primitives-collection";
  const tempModeId = "temp:primitives-mode-1";

  const payloadCollections: unknown[] = [];
  const payloadModes: unknown[] = [];

  if (collection) {
    console.log(`Found existing collection "${COLLECTION_NAME}" (${collection.id})`);
    modeId = collection.defaultModeId;
  } else {
    console.log(`Collection "${COLLECTION_NAME}" not found — will create it`);
    payloadCollections.push({
      action: "CREATE",
      id: tempCollectionId,
      name: COLLECTION_NAME,
      initialModeId: tempModeId,
    });
    payloadModes.push({
      action: "CREATE",
      id: tempModeId,
      name: "Mode 1",
      variableCollectionId: tempCollectionId,
    });
    modeId = tempModeId;
  }

  const collectionId = collection?.id ?? tempCollectionId;

  // 4. Build existing name→variable map for the collection
  const existingByName = new Map<string, FigmaVariable>();
  if (collection) {
    for (const vid of collection.variableIds) {
      const v = variables[vid];
      if (v) existingByName.set(v.name, v);
    }
    console.log(`  ${existingByName.size} variables already in collection`);
  }

  // 5. Build CREATE / UPDATE lists
  const payloadVariables: unknown[] = [];
  const payloadModeValues: unknown[] = [];

  let creates = 0;
  let updates = 0;

  for (const token of tokens) {
    const existing_var = existingByName.get(token.name);

    if (existing_var) {
      // UPDATE — only if value differs
      const currentValue = existing_var.valuesByMode[modeId];
      const valuesMatch =
        token.type === "COLOR"
          ? JSON.stringify(currentValue) === JSON.stringify(token.value)
          : currentValue === token.value;

      if (!valuesMatch) {
        payloadVariables.push({
          action: "UPDATE",
          id: existing_var.id,
        });
        payloadModeValues.push({
          variableId: existing_var.id,
          modeId: collection!.defaultModeId,
          value: token.value,
        });
        updates++;
      }
    } else {
      // CREATE
      const tempId = `temp:${token.name.replace(/\//g, "-").replace(/\s/g, "_")}`;
      payloadVariables.push({
        action: "CREATE",
        id: tempId,
        name: token.name,
        variableCollectionId: collectionId,
        resolvedType: token.type,
        scopes: token.type === "COLOR" ? ["ALL_SCOPES"] : ["ALL_SCOPES"],
      });
      payloadModeValues.push({
        variableId: tempId,
        modeId,
        value: token.value,
      });
      creates++;
    }
  }

  console.log(`\nPlan: ${creates} create, ${updates} update, ${tokens.length - creates - updates} unchanged`);

  if (
    payloadCollections.length === 0 &&
    payloadVariables.length === 0 &&
    payloadModeValues.length === 0
  ) {
    console.log("Nothing to do — all variables are up to date.");
    return;
  }

  // 6. Send
  console.log("Sending to Figma API…");
  const result = await postVariables({
    variableCollections: payloadCollections,
    variableModes: payloadModes,
    variables: payloadVariables,
    variableModeValues: payloadModeValues,
  });

  console.log("\nDone.");
  const r = result as { meta?: { createdVariables?: unknown[] } };
  if (r.meta?.createdVariables) {
    console.log(`  Created: ${(r.meta.createdVariables as unknown[]).length} variables`);
  }
}

main().catch((err) => {
  console.error("\nFailed:", err.message ?? err);
  process.exit(1);
});
