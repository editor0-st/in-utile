/**
 * Syncs ALL token files into Figma as Variables.
 *
 * Collections created:
 *   • Primitives  (color)          — tokens/007383c9-Mode_1.tokens.json  (1 mode)
 *   • Typography  (string, float)  — tokens/typography.tokens.json        (1 mode)
 *   • Spacing     (float)          — tokens/spacing.tokens.json            (1 mode)
 *   • Semantic    (color)          — tokens/semantic.tokens.json           (Light + Dark)
 *
 * Usage:
 *   FIGMA_TOKEN=figd_... npx tsx scripts/sync-figma-all.ts
 *   FIGMA_TOKEN=figd_... FIGMA_FILE_KEY=<key> npx tsx scripts/sync-figma-all.ts
 */

import fs from "fs";
import path from "path";

// ── Config ────────────────────────────────────────────────────────────────────

const TOKEN = process.env.FIGMA_TOKEN;
const FILE_KEY = process.env.FIGMA_FILE_KEY ?? "0Ycf5NiD6I082kykCLEvVA";

if (!TOKEN) {
  console.error("Error: FIGMA_TOKEN environment variable is required.");
  process.exit(1);
}

const BASE = "https://api.figma.com/v1";
const HEADERS = {
  "X-Figma-Token": TOKEN,
  "Content-Type": "application/json",
};
const ROOT = path.resolve(import.meta.dirname, "..");

// ── Types ─────────────────────────────────────────────────────────────────────

type FigmaVarType = "COLOR" | "FLOAT" | "STRING" | "BOOLEAN";

interface FigmaRGBA {
  r: number;
  g: number;
  b: number;
  a: number;
}

interface FigmaCollection {
  id: string;
  name: string;
  modes: { modeId: string; name: string }[];
  defaultModeId: string;
  variableIds: string[];
}

interface FigmaVariable {
  id: string;
  name: string;
  resolvedType: FigmaVarType;
  variableCollectionId: string;
  valuesByMode: Record<string, unknown>;
}

interface LocalVarsResponse {
  meta: {
    variableCollections: Record<string, FigmaCollection>;
    variables: Record<string, FigmaVariable>;
  };
}

// Token file flat entry
interface TokenVar {
  name: string;
  type: FigmaVarType;
  values: Record<string, FigmaRGBA | number | string>; // keyed by mode name
}

// ── Colour helpers ─────────────────────────────────────────────────────────────

function hexToRgba(hex: string): FigmaRGBA {
  const clean = hex.replace("#", "");
  const full = clean.length === 3
    ? clean.split("").map((c) => c + c).join("")
    : clean;
  return {
    r: parseInt(full.slice(0, 2), 16) / 255,
    g: parseInt(full.slice(2, 4), 16) / 255,
    b: parseInt(full.slice(4, 6), 16) / 255,
    a: 1,
  };
}

function parseCssColor(raw: string): FigmaRGBA {
  const rgba = raw.match(/rgba?\(([^)]+)\)/);
  if (rgba) {
    const [r, g, b, a = "1"] = rgba[1].split(",").map((s) => s.trim());
    return {
      r: Number(r) / 255,
      g: Number(g) / 255,
      b: Number(b) / 255,
      a: parseFloat(a),
    };
  }
  return hexToRgba(raw);
}

// ── Token file parsers ─────────────────────────────────────────────────────────

/** Parse the W3C primitive colors file (single mode). */
function parsePrimitives(filePath: string): TokenVar[] {
  const raw = JSON.parse(fs.readFileSync(filePath, "utf-8")) as Record<string, unknown>;
  const out: TokenVar[] = [];

  for (const [group, gv] of Object.entries(raw)) {
    if (group === "$extensions" || typeof gv !== "object" || gv === null) continue;
    for (const [step, sv] of Object.entries(gv as Record<string, unknown>)) {
      if (step === "$extensions") continue;
      const entry = sv as { $type: string; $value: { components: [number, number, number]; alpha: number } | string };
      if (entry.$type === "color") {
        const v = entry.$value as { components: [number, number, number]; alpha: number };
        out.push({
          name: `${group}/${step}`,
          type: "COLOR",
          values: {
            "Mode 1": { r: v.components[0], g: v.components[1], b: v.components[2], a: v.alpha },
          },
        });
      } else if (entry.$type === "string") {
        out.push({
          name: `${group}/${step}`,
          type: "STRING",
          values: { "Mode 1": entry.$value as string },
        });
      }
    }
  }

  return out;
}

/** Parse typography.tokens.json or spacing.tokens.json (single mode). */
function parseSingleMode(filePath: string): TokenVar[] {
  const raw = JSON.parse(fs.readFileSync(filePath, "utf-8")) as Record<string, unknown>;
  const out: TokenVar[] = [];

  for (const [group, gv] of Object.entries(raw)) {
    if (group.startsWith("$") || typeof gv !== "object" || gv === null) continue;
    for (const [step, sv] of Object.entries(gv as Record<string, unknown>)) {
      if (step.startsWith("$")) continue;
      const entry = sv as { $type: string; $value: unknown };
      if (!entry.$type) continue;

      const type: FigmaVarType =
        entry.$type === "string" ? "STRING" :
        entry.$type === "number" ? "FLOAT" :
        entry.$type === "color" ? "COLOR" : "STRING";

      out.push({
        name: `${group}/${step}`,
        type,
        values: { "Mode 1": entry.$value as string | number },
      });
    }
  }

  return out;
}

/** Parse semantic.tokens.json (Light + Dark modes). */
function parseSemantic(filePath: string): TokenVar[] {
  const raw = JSON.parse(fs.readFileSync(filePath, "utf-8")) as Record<string, unknown>;
  const out: TokenVar[] = [];

  for (const [group, gv] of Object.entries(raw)) {
    if (group.startsWith("$") || typeof gv !== "object" || gv === null) continue;
    for (const [step, sv] of Object.entries(gv as Record<string, unknown>)) {
      if (step.startsWith("$")) continue;
      const entry = sv as { $type: string; $light: string; $dark: string };
      if (entry.$type !== "color") continue;

      out.push({
        name: `${group}/${step}`,
        type: "COLOR",
        values: {
          Light: parseCssColor(entry.$light),
          Dark: parseCssColor(entry.$dark),
        },
      });
    }
  }

  return out;
}

// ── Figma API ─────────────────────────────────────────────────────────────────

async function getLocalVars(): Promise<LocalVarsResponse> {
  const res = await fetch(`${BASE}/files/${FILE_KEY}/variables/local`, { headers: HEADERS });
  if (!res.ok) throw new Error(`GET variables/local: ${res.status} ${await res.text()}`);
  return res.json() as Promise<LocalVarsResponse>;
}

async function postVars(payload: unknown): Promise<unknown> {
  const res = await fetch(`${BASE}/files/${FILE_KEY}/variables`, {
    method: "POST",
    headers: HEADERS,
    body: JSON.stringify(payload),
  });
  const json = await res.json();
  if (!res.ok) throw new Error(`POST variables: ${res.status}\n${JSON.stringify(json, null, 2)}`);
  return json;
}

// ── Upsert a single collection ─────────────────────────────────────────────────

interface CollectionSpec {
  name: string;
  modes: string[];
  tokens: TokenVar[];
}

async function upsertCollection(
  spec: CollectionSpec,
  existingCollections: Map<string, FigmaCollection>,
  existingVariables: Map<string, FigmaVariable>
): Promise<void> {
  console.log(`\n── ${spec.name} (${spec.tokens.length} vars, modes: ${spec.modes.join(", ")}) ──`);

  const col = existingCollections.get(spec.name);
  const tempColId = `temp:col-${spec.name.toLowerCase().replace(/\s+/g, "-")}`;

  const payloadCollections: unknown[] = [];
  const payloadModes: unknown[] = [];
  const payloadVars: unknown[] = [];
  const payloadModeValues: unknown[] = [];

  // Mode ID map: mode name → Figma modeId or temp ID
  const modeIdMap = new Map<string, string>();

  if (col) {
    for (const m of col.modes) modeIdMap.set(m.name, m.modeId);

    // Ensure all required modes exist
    for (const modeName of spec.modes) {
      if (!modeIdMap.has(modeName)) {
        const tempModeId = `temp:mode-${spec.name}-${modeName}`.replace(/\s/g, "_");
        payloadModes.push({
          action: "CREATE",
          id: tempModeId,
          name: modeName,
          variableCollectionId: col.id,
        });
        modeIdMap.set(modeName, tempModeId);
        console.log(`  + mode "${modeName}" (new)`);
      }
    }
  } else {
    // Create collection with first mode
    const firstMode = spec.modes[0];
    const tempFirstModeId = `temp:mode-${spec.name}-${firstMode}`.replace(/\s/g, "_");
    payloadCollections.push({
      action: "CREATE",
      id: tempColId,
      name: spec.name,
      initialModeId: tempFirstModeId,
    });
    payloadModes.push({
      action: "CREATE",
      id: tempFirstModeId,
      name: firstMode,
      variableCollectionId: tempColId,
    });
    modeIdMap.set(firstMode, tempFirstModeId);
    console.log(`  + collection "${spec.name}" created`);

    // Additional modes
    for (const modeName of spec.modes.slice(1)) {
      const tempModeId = `temp:mode-${spec.name}-${modeName}`.replace(/\s/g, "_");
      payloadModes.push({
        action: "CREATE",
        id: tempModeId,
        name: modeName,
        variableCollectionId: tempColId,
      });
      modeIdMap.set(modeName, tempModeId);
    }
  }

  const collectionId = col?.id ?? tempColId;

  // Build existing name→var map within this collection
  const byName = new Map<string, FigmaVariable>();
  if (col) {
    for (const vid of col.variableIds) {
      const v = existingVariables.get(vid);
      if (v) byName.set(v.name, v);
    }
  }

  let creates = 0;
  let updates = 0;
  let unchanged = 0;

  for (const token of spec.tokens) {
    const existing = byName.get(token.name);

    if (existing) {
      // Check if any mode value changed
      let changed = false;
      for (const [modeName, value] of Object.entries(token.values)) {
        const modeId = modeIdMap.get(modeName);
        if (!modeId) continue;
        const cur = existing.valuesByMode[modeId];
        if (JSON.stringify(cur) !== JSON.stringify(value)) {
          changed = true;
          payloadModeValues.push({ variableId: existing.id, modeId, value });
        }
      }
      if (changed) {
        payloadVars.push({ action: "UPDATE", id: existing.id });
        updates++;
      } else {
        unchanged++;
      }
    } else {
      const tempId = `temp:var-${token.name}`.replace(/[/\s]/g, "-");
      payloadVars.push({
        action: "CREATE",
        id: tempId,
        name: token.name,
        variableCollectionId: collectionId,
        resolvedType: token.type,
        scopes: ["ALL_SCOPES"],
      });
      for (const [modeName, value] of Object.entries(token.values)) {
        const modeId = modeIdMap.get(modeName);
        if (modeId) payloadModeValues.push({ variableId: tempId, modeId, value });
      }
      creates++;
    }
  }

  console.log(`  create: ${creates}  update: ${updates}  unchanged: ${unchanged}`);

  if (
    payloadCollections.length === 0 &&
    payloadModes.length === 0 &&
    payloadVars.length === 0 &&
    payloadModeValues.length === 0
  ) {
    console.log("  nothing to send");
    return;
  }

  await postVars({
    variableCollections: payloadCollections,
    variableModes: payloadModes,
    variables: payloadVars,
    variableModeValues: payloadModeValues,
  });
  console.log("  ✓ synced");
}

// ── Main ──────────────────────────────────────────────────────────────────────

async function main() {
  console.log(`Figma file: ${FILE_KEY}`);
  console.log("Fetching existing variables…");

  const state = await getLocalVars();
  const cols = state.meta.variableCollections;
  const vars = state.meta.variables;

  const existingCollections = new Map(Object.values(cols).map((c) => [c.name, c]));
  const existingVariables = new Map(Object.values(vars).map((v) => [v.id, v]));

  console.log(`  ${existingCollections.size} existing collections, ${existingVariables.size} existing variables`);

  const specs: CollectionSpec[] = [
    {
      name: "Primitives",
      modes: ["Mode 1"],
      tokens: parsePrimitives(path.join(ROOT, "007383c9-Mode_1.tokens.json")),
    },
    {
      name: "Typography",
      modes: ["Mode 1"],
      tokens: parseSingleMode(path.join(ROOT, "tokens/typography.tokens.json")),
    },
    {
      name: "Spacing",
      modes: ["Mode 1"],
      tokens: parseSingleMode(path.join(ROOT, "tokens/spacing.tokens.json")),
    },
    {
      name: "Semantic",
      modes: ["Light", "Dark"],
      tokens: parseSemantic(path.join(ROOT, "tokens/semantic.tokens.json")),
    },
  ];

  for (const spec of specs) {
    await upsertCollection(spec, existingCollections, existingVariables);
  }

  console.log("\n✓ All done.");
}

main().catch((err: Error) => {
  console.error("\nFailed:", err.message ?? err);
  process.exit(1);
});
