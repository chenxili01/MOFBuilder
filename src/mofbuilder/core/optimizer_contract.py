from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Dict, Mapping, Optional, Tuple

from .runtime_snapshot import (
    EdgeRoleRecord,
    GraphEdgeSemanticRecord,
    GraphNodeSemanticRecord,
    NodeRoleRecord,
    OptimizationSemanticSnapshot,
)


FrozenMapping = Mapping[str, Any]


def _freeze_value(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({key: _freeze_value(item) for key, item in value.items()})
    if isinstance(value, tuple):
        return tuple(_freeze_value(item) for item in value)
    if isinstance(value, list):
        return tuple(_freeze_value(item) for item in value)
    return value


def _freeze_mapping(mapping: Optional[Mapping[str, Any]]) -> FrozenMapping:
    if mapping is None:
        return MappingProxyType({})
    return MappingProxyType({key: _freeze_value(value) for key, value in mapping.items()})


def _freeze_tuple(values: Optional[Tuple[Any, ...]]) -> Tuple[Any, ...]:
    if values is None:
        return ()
    return tuple(_freeze_value(value) for value in values)


@dataclass(frozen=True)
class TargetDirectionReference:
    edge_id: str
    local_node_id: str
    remote_node_id: Optional[str] = None
    local_role_id: Optional[str] = None
    remote_role_id: Optional[str] = None
    path_type: Optional[str] = None
    endpoint_pattern: Tuple[str, ...] = ()
    slot_index: Optional[int] = None
    metadata: FrozenMapping = field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self) -> None:
        object.__setattr__(self, "endpoint_pattern", _freeze_tuple(self.endpoint_pattern))
        object.__setattr__(self, "metadata", _freeze_mapping(self.metadata))


@dataclass(frozen=True)
class IncidentEdgePlacementRequirement:
    edge_id: str
    edge_role_id: str
    incident_index: int
    local_slot_index: Optional[int] = None
    local_slot_rule: FrozenMapping = field(default_factory=lambda: MappingProxyType({}))
    edge_slot_rule: FrozenMapping = field(default_factory=lambda: MappingProxyType({}))
    required_slot_type: Optional[str] = None
    endpoint_side: Optional[str] = None
    path_type: Optional[str] = None
    remote_node_id: Optional[str] = None
    remote_role_id: Optional[str] = None
    endpoint_pattern: Tuple[str, ...] = ()
    resolve_mode: Optional[str] = None
    bundle_id: Optional[str] = None
    bundle_order_index: Optional[int] = None
    is_null_edge: bool = False
    allows_null_fallback: bool = False
    null_payload_model: Optional[str] = None
    target_direction: Optional[TargetDirectionReference] = None
    metadata: FrozenMapping = field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self) -> None:
        object.__setattr__(self, "local_slot_rule", _freeze_mapping(self.local_slot_rule))
        object.__setattr__(self, "edge_slot_rule", _freeze_mapping(self.edge_slot_rule))
        object.__setattr__(self, "endpoint_pattern", _freeze_tuple(self.endpoint_pattern))
        object.__setattr__(self, "metadata", _freeze_mapping(self.metadata))


@dataclass(frozen=True)
class NodePlacementContract:
    node_id: str
    node_role_id: str
    node_role_class: str
    slot_rules: Tuple[FrozenMapping, ...] = ()
    local_slot_types: Tuple[Optional[str], ...] = ()
    incident_edge_ids: Tuple[str, ...] = ()
    incident_edge_role_ids: Tuple[str, ...] = ()
    incident_requirements: Tuple[IncidentEdgePlacementRequirement, ...] = ()
    bundle_id: Optional[str] = None
    bundle_order_hint: FrozenMapping = field(default_factory=lambda: MappingProxyType({}))
    bundle_ordered_attachment_indices: Tuple[int, ...] = ()
    bundle_order_kind: Optional[str] = None
    resolve_mode_hints: Tuple[str, ...] = ()
    null_edge_flags: FrozenMapping = field(default_factory=lambda: MappingProxyType({}))
    metadata: FrozenMapping = field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self) -> None:
        object.__setattr__(self, "slot_rules", _freeze_tuple(self.slot_rules))
        object.__setattr__(self, "local_slot_types", _freeze_tuple(self.local_slot_types))
        object.__setattr__(self, "incident_edge_ids", _freeze_tuple(self.incident_edge_ids))
        object.__setattr__(self, "incident_edge_role_ids", _freeze_tuple(self.incident_edge_role_ids))
        object.__setattr__(
            self,
            "incident_requirements",
            _freeze_tuple(self.incident_requirements),
        )
        object.__setattr__(self, "bundle_order_hint", _freeze_mapping(self.bundle_order_hint))
        object.__setattr__(
            self,
            "bundle_ordered_attachment_indices",
            _freeze_tuple(self.bundle_ordered_attachment_indices),
        )
        object.__setattr__(self, "resolve_mode_hints", _freeze_tuple(self.resolve_mode_hints))
        object.__setattr__(self, "null_edge_flags", _freeze_mapping(self.null_edge_flags))
        object.__setattr__(self, "metadata", _freeze_mapping(self.metadata))


@dataclass(frozen=True)
class LegalSlotAssignment:
    edge_id: str
    edge_role_id: str
    incident_index: int
    slot_index: int
    slot_type: Optional[str] = None
    endpoint_side: Optional[str] = None
    path_type: Optional[str] = None
    resolve_mode: Optional[str] = None
    is_null_edge: bool = False
    endpoint_pattern: Tuple[str, ...] = ()
    metadata: FrozenMapping = field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self) -> None:
        object.__setattr__(self, "endpoint_pattern", _freeze_tuple(self.endpoint_pattern))
        object.__setattr__(self, "metadata", _freeze_mapping(self.metadata))


@dataclass(frozen=True)
class LegalNodeCorrespondence:
    node_id: str
    node_role_id: str
    assignments: Tuple[LegalSlotAssignment, ...] = ()
    edge_to_slot_index: FrozenMapping = field(default_factory=lambda: MappingProxyType({}))
    metadata: FrozenMapping = field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self) -> None:
        object.__setattr__(self, "assignments", _freeze_tuple(self.assignments))
        object.__setattr__(self, "edge_to_slot_index", _freeze_mapping(self.edge_to_slot_index))
        object.__setattr__(self, "metadata", _freeze_mapping(self.metadata))


def _select_edge_slot_rule(
    edge_record: GraphEdgeSemanticRecord,
    role_record: Optional[EdgeRoleRecord],
    node_record: GraphNodeSemanticRecord,
    slot_index: Optional[int],
) -> FrozenMapping:
    endpoint_side = node_record.role_class
    candidate_rules = edge_record.slot_rules or ()
    if not candidate_rules and role_record is not None:
        candidate_rules = role_record.slot_rules or ()

    matched_by_side = []
    for rule in candidate_rules:
        rule_side = rule.get("endpoint_side")
        if rule_side is not None and rule_side == endpoint_side:
            matched_by_side.append(rule)

    if slot_index is not None:
        for rule in matched_by_side:
            if rule.get("attachment_index") == slot_index:
                return _freeze_mapping(rule)
        for rule in candidate_rules:
            if rule.get("attachment_index") == slot_index:
                return _freeze_mapping(rule)

    if matched_by_side:
        return _freeze_mapping(matched_by_side[0])
    if candidate_rules:
        return _freeze_mapping(candidate_rules[0])
    return _freeze_mapping({})


def _build_target_direction(
    node_record: GraphNodeSemanticRecord,
    edge_record: GraphEdgeSemanticRecord,
    slot_index: Optional[int],
) -> TargetDirectionReference:
    endpoint_node_ids = tuple(edge_record.endpoint_node_ids or ())
    endpoint_role_ids = tuple(edge_record.endpoint_role_ids or ())
    remote_node_id = None
    remote_role_id = None

    if endpoint_node_ids:
        for idx, endpoint_node_id in enumerate(endpoint_node_ids):
            if endpoint_node_id != node_record.node_id:
                remote_node_id = endpoint_node_id
                if idx < len(endpoint_role_ids):
                    remote_role_id = endpoint_role_ids[idx]
                break

    return TargetDirectionReference(
        edge_id=edge_record.edge_id,
        local_node_id=node_record.node_id,
        remote_node_id=remote_node_id,
        local_role_id=node_record.role_id,
        remote_role_id=remote_role_id,
        path_type=edge_record.path_type,
        endpoint_pattern=edge_record.endpoint_pattern,
        slot_index=slot_index,
        metadata={
            "graph_edge": edge_record.graph_edge,
            "endpoint_node_ids": endpoint_node_ids,
            "endpoint_role_ids": endpoint_role_ids,
        },
    )


def _get_role_alias(role_record: Optional[NodeRoleRecord | EdgeRoleRecord], role_id: Optional[str]) -> Optional[str]:
    if role_record is not None and role_record.family_alias:
        return role_record.family_alias
    if role_id is None:
        return None
    if ":" in role_id:
        return role_id.split(":", 1)[1]
    return role_id


def _matches_endpoint_pattern(
    contract: NodePlacementContract,
    requirement: IncidentEdgePlacementRequirement,
    semantic_snapshot: OptimizationSemanticSnapshot,
) -> bool:
    if not requirement.endpoint_pattern:
        return True

    node_role_record = semantic_snapshot.node_role_records.get(contract.node_role_id)
    edge_role_record = semantic_snapshot.edge_role_records.get(requirement.edge_role_id)
    node_alias = _get_role_alias(node_role_record, contract.node_role_id)
    edge_alias = _get_role_alias(edge_role_record, requirement.edge_role_id)
    pattern = requirement.endpoint_pattern

    if len(pattern) >= 2 and edge_alias is not None and pattern[1] != edge_alias:
        return False

    if len(pattern) == 3:
        if requirement.target_direction is None:
            return node_alias == pattern[0] or node_alias == pattern[2]
        endpoint_node_ids = requirement.target_direction.metadata.get("endpoint_node_ids", ())
        if not endpoint_node_ids:
            return node_alias == pattern[0] or node_alias == pattern[2]
        local_is_first = requirement.target_direction.local_node_id == endpoint_node_ids[0]
        expected_node_alias = pattern[0] if local_is_first else pattern[2]
        return node_alias == expected_node_alias

    return True


def _bundle_order_slot_index(
    contract: NodePlacementContract,
    requirement: IncidentEdgePlacementRequirement,
) -> Optional[int]:
    if (
        contract.bundle_id is None
        or requirement.bundle_id != contract.bundle_id
        or requirement.bundle_order_index is None
        or not contract.bundle_ordered_attachment_indices
    ):
        return None
    if requirement.bundle_order_index >= len(contract.bundle_ordered_attachment_indices):
        return None
    return contract.bundle_ordered_attachment_indices[requirement.bundle_order_index]


def _candidate_slot_indices(
    contract: NodePlacementContract,
    requirement: IncidentEdgePlacementRequirement,
    semantic_snapshot: OptimizationSemanticSnapshot,
) -> Tuple[int, ...]:
    if requirement.endpoint_side is not None and requirement.endpoint_side != contract.node_role_class:
        return ()
    if not _matches_endpoint_pattern(contract, requirement, semantic_snapshot):
        return ()

    bundle_slot_index = _bundle_order_slot_index(contract, requirement)
    if bundle_slot_index is not None:
        candidate_indices = (bundle_slot_index,)
    elif requirement.local_slot_index is not None:
        candidate_indices = (requirement.local_slot_index,)
    else:
        candidate_indices = tuple(range(len(contract.slot_rules)))

    legal_indices = []
    for slot_index in candidate_indices:
        if slot_index >= len(contract.slot_rules):
            continue
        slot_rule = contract.slot_rules[slot_index]
        local_slot_type = slot_rule.get("slot_type")
        required_slot_type = requirement.required_slot_type
        if required_slot_type is not None and local_slot_type is not None and required_slot_type != local_slot_type:
            continue
        legal_indices.append(slot_index)

    return tuple(legal_indices)


def _build_legal_correspondence(
    contract: NodePlacementContract,
    assignment_by_incident_index: Dict[int, int],
) -> LegalNodeCorrespondence:
    assignments = []
    edge_to_slot_index = {}
    for requirement in contract.incident_requirements:
        slot_index = assignment_by_incident_index[requirement.incident_index]
        slot_rule = contract.slot_rules[slot_index] if slot_index < len(contract.slot_rules) else {}
        assignments.append(
            LegalSlotAssignment(
                edge_id=requirement.edge_id,
                edge_role_id=requirement.edge_role_id,
                incident_index=requirement.incident_index,
                slot_index=slot_index,
                slot_type=slot_rule.get("slot_type"),
                endpoint_side=requirement.endpoint_side,
                path_type=requirement.path_type,
                resolve_mode=requirement.resolve_mode,
                is_null_edge=requirement.is_null_edge,
                endpoint_pattern=requirement.endpoint_pattern,
                metadata={
                    "required_slot_type": requirement.required_slot_type,
                    "bundle_id": requirement.bundle_id,
                    "bundle_order_index": requirement.bundle_order_index,
                    "remote_node_id": requirement.remote_node_id,
                    "remote_role_id": requirement.remote_role_id,
                },
            )
        )
        edge_to_slot_index[requirement.edge_id] = slot_index

    return LegalNodeCorrespondence(
        node_id=contract.node_id,
        node_role_id=contract.node_role_id,
        assignments=tuple(assignments),
        edge_to_slot_index=edge_to_slot_index,
        metadata={
            "candidate_count": len(assignments),
            "bundle_id": contract.bundle_id,
        },
    )


def compile_node_placement_contract(
    semantic_snapshot: OptimizationSemanticSnapshot,
    node_id: str,
) -> NodePlacementContract:
    node_record = semantic_snapshot.graph_node_records[node_id]
    bundle_record = None
    if node_record.bundle_id is not None:
        bundle_record = semantic_snapshot.bundle_records.get(node_record.bundle_id)

    incident_requirements = []
    null_edge_flags = {}

    for incident_index, edge_id in enumerate(node_record.incident_edge_ids):
        edge_record = semantic_snapshot.graph_edge_records[edge_id]
        edge_role_record = semantic_snapshot.edge_role_records.get(edge_record.edge_role_id)
        null_policy = semantic_snapshot.null_edge_policy_records.get(edge_record.edge_role_id)

        slot_index = None
        constraint = (
            node_record.incident_edge_constraints[incident_index]
            if incident_index < len(node_record.incident_edge_constraints)
            else {}
        )
        if constraint.get("slot_index") is not None:
            slot_index = constraint.get("slot_index")
        elif edge_record.slot_index:
            slot_index = edge_record.slot_index.get(node_id)

        local_slot_rule = {}
        if slot_index is not None:
            for rule in node_record.slot_rules:
                if rule.get("attachment_index") == slot_index:
                    local_slot_rule = rule
                    break

        edge_slot_rule = _select_edge_slot_rule(edge_record, edge_role_record, node_record, slot_index)
        required_slot_type = edge_slot_rule.get("slot_type") or local_slot_rule.get("slot_type")

        target_direction = _build_target_direction(node_record, edge_record, slot_index)

        incident_requirement = IncidentEdgePlacementRequirement(
            edge_id=edge_record.edge_id,
            edge_role_id=edge_record.edge_role_id,
            incident_index=incident_index,
            local_slot_index=slot_index,
            local_slot_rule=local_slot_rule,
            edge_slot_rule=edge_slot_rule,
            required_slot_type=required_slot_type,
            endpoint_side=edge_slot_rule.get("endpoint_side"),
            path_type=edge_record.path_type,
            remote_node_id=target_direction.remote_node_id,
            remote_role_id=target_direction.remote_role_id,
            endpoint_pattern=edge_record.endpoint_pattern,
            resolve_mode=edge_record.resolve_mode,
            bundle_id=edge_record.bundle_id,
            bundle_order_index=edge_record.bundle_order_index,
            is_null_edge=edge_record.is_null_edge or bool(
                null_policy is not None and null_policy.is_null_edge
            ),
            allows_null_fallback=edge_record.allows_null_fallback or bool(
                null_policy is not None and null_policy.allows_null_fallback
            ),
            null_payload_model=edge_record.null_payload_model
            or (null_policy.null_payload_model if null_policy is not None else None),
            target_direction=target_direction,
            metadata={
                "constraint": constraint,
                "edge_slot_index": edge_record.slot_index,
                "null_policy_edge_kind": null_policy.edge_kind if null_policy is not None else None,
            },
        )
        incident_requirements.append(incident_requirement)
        null_edge_flags[edge_record.edge_id] = incident_requirement.is_null_edge

    resolve_mode_hints = tuple(
        requirement.resolve_mode
        for requirement in incident_requirements
        if requirement.resolve_mode is not None
    )

    return NodePlacementContract(
        node_id=node_record.node_id,
        node_role_id=node_record.role_id,
        node_role_class=node_record.role_class,
        slot_rules=node_record.slot_rules,
        local_slot_types=tuple(rule.get("slot_type") for rule in node_record.slot_rules),
        incident_edge_ids=node_record.incident_edge_ids,
        incident_edge_role_ids=node_record.incident_edge_role_ids,
        incident_requirements=tuple(incident_requirements),
        bundle_id=node_record.bundle_id,
        bundle_order_hint=node_record.bundle_order_hint,
        bundle_ordered_attachment_indices=(
            bundle_record.ordered_attachment_indices if bundle_record is not None else ()
        ),
        bundle_order_kind=bundle_record.order_kind if bundle_record is not None else None,
        resolve_mode_hints=resolve_mode_hints,
        null_edge_flags=null_edge_flags,
        metadata={
            "family_name": semantic_snapshot.family_name,
            "graph_phase": semantic_snapshot.graph_phase,
        },
    )


def compile_legal_node_correspondences(
    semantic_snapshot: OptimizationSemanticSnapshot,
    node_id: str,
    node_contract: Optional[NodePlacementContract] = None,
) -> Tuple[LegalNodeCorrespondence, ...]:
    contract = node_contract or compile_node_placement_contract(semantic_snapshot, node_id)
    if len(contract.incident_requirements) > len(contract.slot_rules):
        return ()

    candidate_lists = []
    for requirement in contract.incident_requirements:
        candidate_indices = _candidate_slot_indices(contract, requirement, semantic_snapshot)
        if not candidate_indices:
            return ()
        candidate_lists.append((requirement.incident_index, candidate_indices))

    correspondence_candidates = []
    seen_mappings = set()
    ordered_candidates = sorted(candidate_lists, key=lambda item: (len(item[1]), item[0]))

    def backtrack(position: int, assigned_slots: Dict[int, int], used_slots: set[int]) -> None:
        if position == len(ordered_candidates):
            key = tuple(sorted(assigned_slots.items()))
            if key in seen_mappings:
                return
            seen_mappings.add(key)
            correspondence_candidates.append(
                _build_legal_correspondence(contract, assigned_slots)
            )
            return

        incident_index, slot_candidates = ordered_candidates[position]
        for slot_index in slot_candidates:
            if slot_index in used_slots:
                continue
            assigned_slots[incident_index] = slot_index
            used_slots.add(slot_index)
            backtrack(position + 1, assigned_slots, used_slots)
            used_slots.remove(slot_index)
            del assigned_slots[incident_index]

    backtrack(0, {}, set())
    correspondence_candidates.sort(
        key=lambda candidate: tuple(
            candidate.edge_to_slot_index[requirement.edge_id]
            for requirement in contract.incident_requirements
        )
    )
    return tuple(correspondence_candidates)
