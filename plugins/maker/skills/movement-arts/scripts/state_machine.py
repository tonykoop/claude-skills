"""
Movement Arts — valid-transition state machine.

ValidTransitionMachine(domain_primitives) → .valid_next_maneuvers(current_state)

Rule-based, not hand-enumerated per style:
  - Weight-shift feasibility: can't shift to a foot that already bears full weight
    and requires a weight transfer first.
  - Facing continuity: target primitive's facing must be reachable from current
    facing without an impossible teleport (180° pivots only allowed if weight is
    unweighted or bilateral).
  - Returns only primitives whose id is in current_primitive.valid_next,
    further filtered by mechanical constraints.

Raises ImpossibleTransitionError when the caller tries to apply a primitive
that fails the constraint check.
"""

from __future__ import annotations
import argparse
import json
import sys
from typing import Dict, List, Optional


class ImpossibleTransitionError(ValueError):
    """Raised when a requested primitive transition violates mechanical constraints."""


FACING_ADJACENCY = {
    "north": {"north", "east", "west"},
    "south": {"south", "east", "west"},
    "east": {"east", "north", "south"},
    "west": {"west", "north", "south"},
    "any": {"north", "south", "east", "west", "any"},
}


def _weight_allows_shift(current_weight: Dict[str, float], target_shift: str) -> bool:
    """
    Return True if the target weight shift is mechanically reachable.

    Rules:
    - 'left'  requires right foot to have some weight available (right > 0 OR bilateral)
    - 'right' requires left foot to have some weight available (left > 0 OR bilateral)
    - 'bilateral' is always reachable
    - 'unweighted' requires some surface/jump transition — allowed only when
      current weight is bilateral (both feet on ground)
    """
    left = current_weight.get("left", 0.5)
    right = current_weight.get("right", 0.5)

    if target_shift == "bilateral":
        return True
    if target_shift == "left":
        # cannot shift to full left if already fully on left
        return not (left == 1.0 and right == 0.0)
    if target_shift == "right":
        return not (right == 1.0 and left == 0.0)
    if target_shift == "unweighted":
        # jumping requires bilateral base
        return left > 0.0 and right > 0.0
    return True


def _facing_allows_transition(
    current_facing: str, target_facing: str, current_weight: Dict[str, float]
) -> bool:
    """
    Return True if facing change is mechanically possible.

    A 180° flip (north↔south, east↔west) requires either bilateral or
    unweighted base (no single-foot pivot through 180°).
    """
    if target_facing == "any":
        return True
    if current_facing == "any":
        return True

    OPPOSITE = {"north": "south", "south": "north", "east": "west", "west": "east"}
    if OPPOSITE.get(current_facing) == target_facing:
        left = current_weight.get("left", 0.5)
        right = current_weight.get("right", 0.5)
        bilateral = abs(left - right) < 0.1
        unweighted = left == 0.0 and right == 0.0
        return bilateral or unweighted

    return target_facing in FACING_ADJACENCY.get(current_facing, set())


class ValidTransitionMachine:
    """
    Computes mechanically valid next maneuvers from current tracker state.

    Parameters
    ----------
    domain_primitives : list[dict]
        The 'primitives' list from a domain JSON.
    """

    def __init__(self, domain_primitives: List[dict]):
        self._primitives = domain_primitives
        self._prim_map: Dict[str, dict] = {p["id"]: p for p in domain_primitives}

    def valid_next_maneuvers(
        self, current_state: dict, current_primitive_id: Optional[str] = None
    ) -> List[dict]:
        """
        Return list of primitives that are mechanically valid from current_state.

        If current_primitive_id is given, constrain to its valid_next list first.
        Then apply weight-shift and facing filters.
        """
        weight = current_state.get("weight_distribution", {"left": 0.5, "right": 0.5})
        facing = current_state.get("facing_direction", "any")

        if current_primitive_id and current_primitive_id in self._prim_map:
            candidates_ids = self._prim_map[current_primitive_id].get("valid_next", [])
            if candidates_ids:
                candidates = [self._prim_map[i] for i in candidates_ids if i in self._prim_map]
            else:
                candidates = self._primitives
        else:
            candidates = self._primitives

        valid = []
        for p in candidates:
            target_shift = p.get("weight_shift", "bilateral")
            target_facing = p.get("facing", "any")
            if _weight_allows_shift(weight, target_shift) and \
               _facing_allows_transition(facing, target_facing, weight):
                valid.append(p)

        return valid

    def assert_transition_valid(
        self, current_state: dict, target_primitive: dict,
        current_primitive_id: Optional[str] = None
    ) -> None:
        """
        Raise ImpossibleTransitionError if the target_primitive cannot follow
        from current_state given the current_primitive's valid_next list.
        """
        valid = self.valid_next_maneuvers(current_state, current_primitive_id)
        valid_ids = {p["id"] for p in valid}
        if target_primitive["id"] not in valid_ids:
            weight = current_state.get("weight_distribution", {})
            facing = current_state.get("facing_direction", "any")
            raise ImpossibleTransitionError(
                f"Impossible transition to '{target_primitive['id']}': "
                f"current weight={weight}, facing={facing}, "
                f"target weight_shift='{target_primitive.get('weight_shift')}', "
                f"target facing='{target_primitive.get('facing')}'"
            )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="movement-arts state machine")
    parser.add_argument("--domain", required=True, help="path to domain JSON file")
    parser.add_argument(
        "--state",
        help='JSON string of tracker state, e.g. \'{"weight_distribution":{"left":1.0,"right":0.0},"facing_direction":"north"}\'',
    )
    parser.add_argument("--from-primitive", help="current primitive ID")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    with open(args.domain) as f:
        domain = json.load(f)

    machine = ValidTransitionMachine(domain["primitives"])
    state = json.loads(args.state) if args.state else {
        "weight_distribution": {"left": 0.5, "right": 0.5},
        "facing_direction": "north",
    }
    valid = machine.valid_next_maneuvers(state, args.from_primitive)

    if args.json:
        print(json.dumps([{"id": p["id"], "name": p.get("name", p["id"])} for p in valid], indent=2))
    else:
        print(f"State: {state}")
        print(f"Valid next maneuvers ({len(valid)}):")
        for p in valid:
            print(f"  {p['id']:30s} weight_shift={p.get('weight_shift','?')} facing={p.get('facing','?')}")


if __name__ == "__main__":
    main()
