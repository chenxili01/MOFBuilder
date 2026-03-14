from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping, Optional, Tuple

from .runtime_snapshot import (
    EdgeRoleRecord,
    GraphEdgeSemanticRecord,
    GraphNodeSemanticRecord,
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
