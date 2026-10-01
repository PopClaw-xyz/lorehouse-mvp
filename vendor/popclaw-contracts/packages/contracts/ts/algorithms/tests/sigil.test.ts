import { describe, it, expect } from 'vitest';
import { sigil, SIGIL_LEN } from '../src/sigil.js';

describe('sigil', () => {
  // NOTE: The literal 'gdx8rgtp' below MUST match the value in the Rust
  // twin's `sigil_matches_hand_computed_value` test (Crockford b32).
  it('matches hand-computed BlackFeather -> gdx8rgtp', () => {
    expect(sigil('BlackFeather', SIGIL_LEN)).toBe('gdx8rgtp');
  });

  it('SIGIL_LEN defaults to 8', () => {
    expect(SIGIL_LEN).toBe(8);
  });

  it('extends deterministically with larger length', () => {
    const eight = sigil('BlackFeather', SIGIL_LEN);
    const twelve = sigil('BlackFeather', 12);
    expect(twelve).toHaveLength(12);
    expect(twelve.startsWith(eight)).toBe(true);
  });

  it('prefix stability across 6/8/12', () => {
    const six = sigil('BlackFeather', 6);
    const eight = sigil('BlackFeather', SIGIL_LEN);
    const twelve = sigil('BlackFeather', 12);
    expect(twelve.startsWith(eight)).toBe(true);
    expect(eight.startsWith(six)).toBe(true);
  });

  it('differentiates different inputs', () => {
    expect(sigil('A', 6)).not.toBe(sigil('B', 6));
  });
});
