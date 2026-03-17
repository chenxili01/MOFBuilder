"""Net and cell optimization: node rotations and unit-cell scaling to fit linkers."""

import sys
from pathlib import Path
from typing import Optional

import numpy as np
import networkx as nx
import mpi4py.MPI as MPI
import h5py
import re

try:
    from scipy.optimize import minimize
except ImportError:
    pass

from veloxchem.outputstream import OutputStream
from veloxchem.veloxchemlib import mpi_master
from veloxchem.errorhandler import assert_msg_critical
from veloxchem.molecule import Molecule

from ..io.basic import nn, nl, pname, is_list_A_in_B
from ..utils.geometry import (unit_cell_to_cartesian_matrix,
                              fractional_to_cartesian, cartesian_to_fractional,
                              locate_min_idx, reorthogonalize_matrix,
                              find_optimal_pairings, find_edge_pairings)
from .optimizer_contract import (
    compile_local_constrained_refinement,
    compile_discrete_ambiguity_resolution,
    compile_local_rigid_initialization,
    compile_legal_node_correspondences,
    compile_node_placement_contract,
    evaluate_shape_preserving_rollout_eligibility,
)
from .other import fetch_X_atoms_ind_array
from .runtime_snapshot import OptimizationSemanticSnapshot
from .superimpose import superimpose_topology_hungarian


class NetOptimizer:
    """Optimizes node rotations and cell parameters so linkers fit the net, then places edges.

    Uses OptimizationDriver for two-stage rotation optimization and cell scaling.
    Requires G, V_data, V_X_data, E_data, E_X_data, sorted_nodes, sorted_edges,
    cell_info, and linker_frag_length (and optionally EC_data for multitopic). Sets
    opt_rots, sc_unit_cell, sc_rot_node_X_pos, sG, optimized_pair, etc.
    """

    def __init__(self, comm=None, ostream=None, semantic_snapshot=None):
        self.comm = comm or MPI.COMM_WORLD
        self.rank = self.comm.Get_rank()
        self.nodes = self.comm.Get_size()
        self.ostream = ostream or OutputStream(sys.stdout if self.rank ==
                                               mpi_master() else None)

        #NEED to be set before use
        self.G = None
        self.V_data = None
        self.V_X_data = None
        self.V_attachment_data_by_type = {}
        self.V_attachment_coords_by_type = {}
        self.EC_data = None
        self.EC_X_data = None
        self.EC_attachment_data_by_type = {}
        self.EC_attachment_coords_by_type = {}
        self.E_data = None
        self.E_X_data = None
        self.E_attachment_data_by_type = {}
        self.E_attachment_coords_by_type = {}
        self.node_role_registry = None
        self.edge_role_registry = None
        self.sorted_nodes = None
        self.sorted_edges = None
        self.cell_info = None

        #will be generated
        self.sorted_edges_of_sortednodeidx = None
        self.pname_set_dict = None
        self.pname_set = None
        self.opt_rots = None
        self.opt_params = None
        self.new_edge_length = None
        self.new_edge_lengths = None
        self.optimized_pair = None
        self.sc_node_pos_dict = None
        self.sc_rot_node_X_pos = None
        self.sc_unit_cell = None
        self.sc_unit_cell_inv = None
        self.fake_edge = False
        self.node_fragment_payloads = None
        self.edge_fragment_payloads = None
        self.semantic_snapshot = semantic_snapshot
        self.use_role_aware_local_placement = False
        self.role_aware_local_placement_records = {}
        self.role_aware_local_placement_debug_records = {}
        self.sc_rot_node_attachment_lookup = {}
        #self.constant_length = 1.54  #default C-C single bond length
        self.linker_frag_length = None

        self.load_optimized_rotations = None
        self.skip_rotation_optimization = False
        self.rotation_filename = None

        # Optimization parameters
        self.opt_drv = OptimizationDriver(comm=self.comm, ostream=self.ostream)
        self.opt_drv.pname_set_dict = None  #to be set later
        #self.opt_drv.opt_method = 'L-BFGS-B'
        #self.opt_drv.maxfun = 15000
        #self.opt_drv.maxiter = 15000
        #self.opt_drv.display = True
        #self.opt_drv.eps = 1e-8

        #other parameters
        self._debug = False
        self.opt_drv._debug = self._debug

        self.optimized_cell_info = None
        """
        - node_target_type (str):metal atom type of the node
        - node_unit_cell (array):unit cell of the node
        - node_atom (array):2 columns, atom_name, atom_type of the node
        - node_x_fcoords (array):fractional coordinates of the X connected atoms of node
        - node_fcoords (array):fractional coordinates of the whole node
        - node_x_ccoords (array):cartesian coordinates of the X connected atoms of node
        - node_coords (array):cartesian coordinates of the whole node
        - linker_unit_cell (array):unit cell of the ditopic linker or branch of multitopic linker
        - linker_atom (array):2 columns, atom_name, atom_type of the ditopic linker or branch of multitopic linker
        - linker_x_fcoords (array):fractional coordinates of the X connected atoms of ditopic linker or branch of multitopic linker
        - linker_fcoords (array):fractional coordinates of the whole ditopic linker or branch of multitopic linker
        - linker_x_ccoords (array):cartesian coordinates of the X connected atoms of ditopic linker or branch of multitopic linker
        - linker_frag_length (float):distance between two X-X connected atoms of the ditopic linker or branch of multitopic linker
        - linker_ccoords (array):cartesian coordinates of the whole ditopic linker or branch of multitopic linker
        - linker_center_cif (str):cif file of the center of the multitopic linker
        - ec_unit_cell (array):unit cell of the center of the multitopic linker
        - ec_atom (array):2 columns, atom_name, atom_type of the center of the multitopic linker
        - ec_x_vecs (array):fractional coordinates of the X connected atoms of the center of the multitopic linker
        - ec_fcoords (array):fractional coordinates of the whole center of the multitopic linker
        - ec_xcoords (array):cartesian coordinates of the X connected atoms of the center of the multitopic linker
        - eccoords (array):cartesian coordinates of the whole center of the multitopic linker
        - constant_length (float):constant length to add to the linker length, normally 1.54 for single bond of C-C,
        because C is always used as the connecting atom in the builder
        - maxfun (int):maximum number of function evaluations for the node rotation optimization
        - opt_method (str):optimization method for the node rotation optimization
        - G (networkx graph):graph of the template
        - node_max_degree (int):maximum degree of the node in the template, should be the same as the node topic
        - sorted_nodes (list):sorted nodes in the template by connectivity
        - sorted_edges (list):sorted edges in the template by connectivity
        - sorted_edges_of_sortednodeidx (list):sorted edges in the template by connectivity with the index of the sorted nodes
        - optimized_rotations (dict):optimized rotations for the nodes in the template
        - optimized_params (array):optimized cell parameters for the template topology to fit the target MOF cell
        - new_edge_length (float):new edge length of the ditopic linker or branch of multitopic linker, 2*constant_length+linker_frag_length
        - optimized_pair (dict): pair of connected nodes in the template with the index of the X connected atoms, used for the edge placement
        - scaled_rotated_node_positions (dict):scaled and rotated node positions in the target MOF cell
        - scaled_rotated_Xatoms_positions (dict):scaled and rotated X connected atom positions of nodes in the target MOF cell
        - sc_unit_cell (array):(scaled) unit cell of the target MOF cell
        - sc_unit_cell_inv (array):inverse of the (scaled) unit cell of the target MOF cell
        - sG_node (networkx graph):graph of the target MOF cell
        - nodes_atom (dict):atom name and atom type of the nodes
        - rotated_node_positions (dict):rotated node positions
        - supercell (array): supercell set by user, along x,y,z direction
        - multiedge_bundlings (dict):multiedge bundlings of center and branches of the multitopic linker, used for the supercell
        construction and merging of center and branches to form one EDGE
        - prim_multiedge_bundlings (dict):multiedge bundlings in primitive cell, used for the supercell construction
        - super_multiedge_bundlings (dict):multiedge bundlings in the supercell, used for the supercell construction
        - dv_v_pairs (dict):DV and V pairs in the template, used for the supercell construction
        - super_multiedge_bundlings (dict):multiedge bundlings in the supercell, used for the supercell construction
        - superG (networkx graph):graph of the supercell
        - add_virtual_edge (bool): add virtual edge to the target MOF cell
        - vir_edge_range (float): range to search the virtual edge between two Vnodes directly, should <= 0.5,
        used for the virtual edge addition of bridge type nodes: nodes and nodes can connect directly without linker
        - vir_edge_max_neighbor (int): maximum number of neighbors of the node with virtual edge, used for the virtual edge addition of bridge type nodes
        - remove_node_list (list):list of nodes to remove in the target MOF cell
        - remove_edge_list (list):list of edges to remove in the target MOF cell
        - eG (networkx graph):graph of the target MOF cell with only EDGE and V nodes
        - node_topic (int):maximum degree of the node in the template, should be the same as the node_max_degree
        - unsaturated_node (list):unsaturated nodes in the target MOF cell
        - term_info (array):information of the node terminations
        - term_coords (array):coordinates of the node terminations
        - term_xoovecs (array):X and O vectors (usually carboxylate group) of the node terminations
        - unsaturated_vnode_xind_dict (dict):unsaturated node and the exposed X connected atom index
        - unsaturated_vnode_xoo_dict (dict):unsaturated node and the exposed X connected atom index and the corresponding O connected atoms
        """

    def rotation_and_cell_optimization(
        self,
        semantic_snapshot: Optional[OptimizationSemanticSnapshot] = None,
        use_role_aware_local_placement: Optional[bool] = None,
    ):
        """
        two optimization steps:
        1. optimize the node rotation (vertex or edge center)
        2. optimize the cell parameters to fit the target MOF cell
        """
        if semantic_snapshot is not None:
            self.semantic_snapshot = semantic_snapshot
        if use_role_aware_local_placement is not None:
            self.use_role_aware_local_placement = use_role_aware_local_placement
        #if self._debug:
        self.ostream.print_info(f"constant_length: {self.constant_length}")
        self.ostream.flush()

        G = self.G.copy()
        self.node_x_ccoords = (self.V_X_data[:, 5:8].astype(float)
                               if self.V_X_data is not None else None)
        self.node_ccoords = (self.V_data[:, 5:8].astype(float)
                             if self.V_data is not None else None)
        self.ec_x_ccoords = self.EC_X_data[:, 5:8].astype(
            float) if self.EC_X_data is not None else None
        self.ec_ccoords = self.EC_data[:, 5:8].astype(
            float) if self.EC_data is not None else None
        self.e_x_ccoords = (self.E_X_data[:, 5:8].astype(float)
                            if self.E_X_data is not None else None)
        self.e_ccoords = (self.E_data[:, 5:8].astype(float)
                          if self.E_data is not None else None)
        self.opt_drv.sorted_nodes = self.sorted_nodes
        self.opt_drv.pname_set_dict = self.pname_set_dict

        self._prepare_role_fragment_payloads(G)
        # firstly, check if all V nodes have highest connectivity
        # secondly, sort all DV nodes by connectivity
        sorted_nodes = self.sorted_nodes
        sorted_edges = self.sorted_edges

    # reindex the nodes in the Xatoms_positions with the index in the sorted_nodes, like G has 16 nodes[2,5,7], but the new dictionary should be [0,1,2]
        node_pos_dict, node_X_pos_dict = self._generate_pos_dict(G)

        # reindex the edges in the G with the index in the sorted_nodes
        self.sorted_edges_of_sortednodeidx = [(sorted_nodes.index(e[0]),
                                               sorted_nodes.index(e[1]))
                                              for e in self.sorted_edges]
        self.opt_drv.sorted_edges = self.sorted_edges_of_sortednodeidx
        # Optimize rotations
        num_nodes = G.number_of_nodes()
        pname_set, pname_set_dict = self._generate_pname_set(
            G, sorted_nodes, node_X_pos_dict)
        self.pname_set_dict = pname_set_dict
        self.opt_drv.pname_set_dict = pname_set_dict

        node_pos_dict, node_X_pos_dict = self._apply_rot_trans2dict(
            G, node_pos_dict, node_X_pos_dict)
        ###3D free rotation
        saved_optimized_rotations = None

        ini_rot = (np.eye(3, 3).reshape(1, 3, 3).repeat(len(pname_set),
                                                        axis=0))

        if self.load_optimized_rotations is not None and Path(
                self.load_optimized_rotations).is_file():
            #load the saved optimized rotations
            with h5py.File(self.load_optimized_rotations, 'r') as hf:
                saved_optimized_rotations = hf['optimized_rotations'][:]
                if self._debug:
                    self.ostream.print_info(
                        f"Loaded saved optimized rotations from {self.load_optimized_rotations}"
                    )
                    self.ostream.print_info(
                        f"Loaded saved optimized rotations shape: {saved_optimized_rotations.shape}"
                    )
            if not self.skip_rotation_optimization:  #load but not skip
                self.ostream.print_info(
                    "use the loaded optimized_rotations from the previous optimization as initial guess"
                )
                ini_rot = saved_optimized_rotations.reshape(-1, 3, 3)

        if saved_optimized_rotations is None:
            self.skip_rotation_optimization = False
            role_aware_initial_rotations = self._compile_role_aware_initial_rotations(
                pname_set_dict,
                semantic_snapshot=self.semantic_snapshot,
            )
            for index, group_name in enumerate(pname_set_dict):
                rotation_matrix = role_aware_initial_rotations.get(group_name)
                if rotation_matrix is not None:
                    ini_rot[index] = self._convert_role_aware_rotation_to_optimizer_frame(
                        rotation_matrix
                    )

        if not self.skip_rotation_optimization:
            ####TODO: modified for mil53
            #opt_rot_pre, _ = self.opt_drv._optimize_rotations_pre(
            #    num_nodes, G, node_X_pos_dict, ini_rot)
            opt_rot_pre = ini_rot
            opt_rot_aft, _ = self.opt_drv._optimize_rotations_after(
                num_nodes, G, node_X_pos_dict, opt_rot_pre)
            #opt_rot_aft = opt_rot_pre
        else:
            opt_rot_aft = saved_optimized_rotations.reshape(-1, 3, 3)

        if self.rotation_filename is not None:
            #save it as h5 file
            with h5py.File(self.rotation_filename, 'w') as hf:
                hf.create_dataset('optimized_rotations', data=opt_rot_aft)

        opt_rots = expand_set_rots(pname_set_dict, opt_rot_aft, sorted_nodes)
        # Apply rotations
        rot_node_pos, _ = self._apply_rot2atoms_pos(opt_rots, G, node_pos_dict)

        if self._debug:
            self.ostream.print_info(
                f"Optimized Rotations (after optimization): {opt_rots}")

            def temp_save_xyz(filename, rot_node_pos):
                with open(filename, "w") as file:
                    num_atoms = sum(
                        len(positions) for positions in rot_node_pos.values())
                    file.write(f"{num_atoms}\n")
                    file.write("Optimized structure\n")
                    for node, positions in rot_node_pos.items():
                        for pos in positions:
                            file.write(
                                f"X{node}   {pos[0]:.8f} {pos[1]:.8f} {pos[2]:.8f}\n"
                            )

            temp_save_xyz("optimized_nodesstructure.xyz", rot_node_pos)

        rot_node_X_pos_dict, _ = self._apply_rot2atoms_pos(
            opt_rots, G, node_X_pos_dict)

        start_node = self.sorted_edges[0][
            0]  # find_nearest_node_to_beginning_point(G)

        # loop all of the edges in G and get the lengths of the edges, length is the distance between the two nodes ccoords
        edge_lengths, lengths = self._get_edge_lengths(G)

        target_edge_lengths = self._get_target_edge_lengths()
        new_edge_length = target_edge_lengths[(self.sorted_edges[0][0],
                                               self.sorted_edges[0][1])]

        # update the node ccoords in G by loop edge, start from the start_node, and then update the connected node ccoords by the edge length, and update the next node ccords from the updated node

        new_ccoords, old_ccoords = self._update_node_ccoords(
            G, edge_lengths, start_node, target_edge_lengths)
        # exclude the start_node in updated_ccoords and original_ccoords
        new_ccoords = {k: v for k, v in new_ccoords.items() if k != start_node}
        old_ccoords = {k: v for k, v in old_ccoords.items() if k != start_node}

        # use optimized_params to update all of nodes ccoords in G, according to the fccoords
        if self.optimized_cell_info is None:
            self.ostream.print_info("-" * 80)
            self.ostream.print_info(
                "Start to optimize the cell parameters to fit the target MOF cell"
            )
            self.ostream.print_info("-" * 80)

            optimized_cell_info = self.opt_drv._optimize_cell_params(
                self.cell_info, old_ccoords, new_ccoords)

            self.ostream.print_info("-" * 80)
            self.ostream.print_info(
                "Finished the cell parameters optimization")
            self.ostream.print_info("-" * 80)
        else:
            self.ostream.print_info(
                "use the optimized_cell_info from the previous optimization")
            optimized_cell_info = self.optimized_cell_info

        # get scaled unit cell and inverse and sG
        a, b, c, alpha, beta, gamma = optimized_cell_info
        sc_unit_cell = unit_cell_to_cartesian_matrix(a, b, c, alpha, beta,
                                                     gamma)
        sc_unit_cell_inv = np.linalg.inv(sc_unit_cell)
        sG, scaled_ccoords = self._update_ccoords_by_optimized_cell_params(
            G, optimized_cell_info)

        # update ccoords in sG
        sc_node_pos_dict, sc_node_X_pos_dict = self._generate_pos_dict(sG)

        # Apply rotations and translations to the scaled positions in sG
        sc_node_pos_dict, sc_node_X_pos_dict = self._apply_rot_trans2dict(
            sG, sc_node_pos_dict, sc_node_X_pos_dict)
        sc_rot_node_pos, _ = self._apply_rot2atoms_pos(opt_rots, sG,
                                                       sc_node_pos_dict)
        sc_rot_node_X_pos, self.optimized_pair = self._apply_rot2atoms_pos(
            opt_rots, sG, sc_node_X_pos_dict)
        sc_rot_node_attachment_lookup = {}
        if self.use_role_aware_local_placement and self.semantic_snapshot is not None:
            sc_node_attachment_pos_dict, attachment_metadata_by_node = (
                self._generate_attachment_position_dict(sG)
            )
            sc_node_attachment_pos_dict, _ = self._apply_rot_trans2dict(
                sG,
                sc_node_attachment_pos_dict,
                {
                    idx: np.empty((0, 4), dtype=float)
                    for idx in sc_node_attachment_pos_dict
                },
            )
            sc_rot_node_attachment_positions = self._apply_rotations_to_position_dict(
                opt_rots,
                sG,
                sc_node_attachment_pos_dict,
            )
            sc_rot_node_attachment_lookup = self._build_attachment_lookup_from_positions(
                attachment_metadata_by_node,
                sc_rot_node_attachment_positions,
            )

        # Save results to XYZ
        if self._debug:
            temp_save_xyz("scaled_optimized_nodesstructure.xyz",
                          sc_rot_node_pos)

        self.opt_rots = opt_rots
        self.optimized_cell_info = optimized_cell_info
        self.new_edge_length = new_edge_length
        self.new_edge_lengths = {
            edge: target_edge_lengths[edge]
            for edge in self.sorted_edges
        }

        self.sG = sG
        self.sc_node_pos_dict = sc_node_pos_dict
        self.sc_rot_node_X_pos = sc_rot_node_X_pos
        self.sc_rot_node_pos = sc_rot_node_pos
        self.sc_rot_node_attachment_lookup = sc_rot_node_attachment_lookup
        self.sc_unit_cell = sc_unit_cell
        self.sc_unit_cell_inv = sc_unit_cell_inv

        self.rotated_node_positions = rot_node_pos
        self.Xatoms_positions_dict = node_X_pos_dict
        self.node_pos_dict = node_pos_dict

    def _compile_role_aware_initial_rotations(self,
                                              pname_set_dict,
                                              semantic_snapshot=None):
        snapshot = semantic_snapshot or self.semantic_snapshot
        if not self.use_role_aware_local_placement or snapshot is None:
            self.role_aware_local_placement_records = {}
            fallback_reason = (
                "guard_disabled"
                if not self.use_role_aware_local_placement
                else "missing_semantic_snapshot"
            )
            self.role_aware_local_placement_debug_records = (
                self._build_guarded_fallback_debug_records(
                    pname_set_dict,
                    fallback_reason=fallback_reason,
                )
            )
            return {}

        initial_rotations = {}
        placement_records = {}
        debug_records = {}
        for group_name, group_data in pname_set_dict.items():
            if not group_data["ind_ofsortednodes"]:
                continue
            node_id = self.sorted_nodes[group_data["ind_ofsortednodes"][0]]
            node_record = snapshot.graph_node_records.get(node_id)
            if node_record is None:
                debug_records[node_id] = self._build_guarded_debug_record(
                    group_name=group_name,
                    node_id=node_id,
                    status="fallback",
                    fallback_reason="missing_node_semantic_record",
                )
                continue
            if node_record.role_class not in {"V", "C"}:
                debug_records[node_id] = self._build_guarded_debug_record(
                    group_name=group_name,
                    node_id=node_id,
                    node_record=node_record,
                    status="fallback",
                    fallback_reason="unsupported_role_class",
                )
                continue
            try:
                contract = self.compile_node_placement_contract(
                    node_id,
                    semantic_snapshot=snapshot,
                )
                correspondences = self.compile_legal_node_correspondences(
                    node_id,
                    semantic_snapshot=snapshot,
                    node_contract=contract,
                )
                if not correspondences:
                    debug_records[node_id] = self._build_guarded_debug_record(
                        group_name=group_name,
                        node_id=node_id,
                        node_record=node_record,
                        node_contract=contract,
                        status="fallback",
                        fallback_reason="no_legal_correspondence",
                    )
                    continue
                rollout_eligibility = evaluate_shape_preserving_rollout_eligibility(
                    snapshot,
                    contract,
                    correspondences=correspondences,
                )
                if not rollout_eligibility["eligible"]:
                    debug_records[node_id] = self._build_guarded_debug_record(
                        group_name=group_name,
                        node_id=node_id,
                        node_record=node_record,
                        node_contract=contract,
                        correspondences=correspondences,
                        status="fallback",
                        fallback_reason=rollout_eligibility["fallback_reason"],
                    )
                    continue
                ambiguity_resolution = None
                selected_correspondence = None
                selected_initialization = None
                if len(correspondences) == 1:
                    selected_correspondence = correspondences[0]
                    selected_initialization = self.compile_local_rigid_initialization(
                        node_id,
                        semantic_snapshot=snapshot,
                        node_contract=contract,
                        correspondence=selected_correspondence,
                    )
                else:
                    ambiguity_resolution = self.compile_discrete_ambiguity_resolution(
                        node_id,
                        semantic_snapshot=snapshot,
                        node_contract=contract,
                        correspondences=correspondences,
                    )
                    selected_correspondence = ambiguity_resolution.selected_correspondence
                    selected_initialization = ambiguity_resolution.selected_initialization
                refinement = self.compile_local_constrained_refinement(
                    node_id,
                    semantic_snapshot=snapshot,
                    node_contract=contract,
                    correspondence=selected_correspondence,
                    rigid_initialization=selected_initialization,
                    ambiguity_resolution=ambiguity_resolution,
                )
            except (KeyError, ValueError) as exc:
                debug_records[node_id] = self._build_guarded_debug_record(
                    group_name=group_name,
                    node_id=node_id,
                    node_record=node_record,
                    status="fallback",
                    fallback_reason=type(exc).__name__,
                    error_message=str(exc),
                )
                continue
            (
                selected_placement,
                selected_pose_source,
                guard_reason,
                covered_shape_preserving_case,
            ) = self._select_guarded_role_aware_local_placement(
                selected_initialization,
                refinement,
            )
            placement_records[node_id] = selected_placement
            initial_rotations[group_name] = np.asarray(
                selected_placement.rotation_matrix,
                dtype=float,
            )
            debug_records[node_id] = self._build_guarded_debug_record(
                group_name=group_name,
                node_id=node_id,
                node_record=node_record,
                node_contract=contract,
                correspondences=correspondences,
                rigid_initialization=selected_initialization,
                refinement=refinement,
                ambiguity_resolution=ambiguity_resolution,
                covered_shape_preserving_case=covered_shape_preserving_case,
                selected_pose_source=selected_pose_source,
                guard_reason=guard_reason,
                status="selected",
            )
        self.role_aware_local_placement_records = placement_records
        self.role_aware_local_placement_debug_records = debug_records
        return initial_rotations

    def _is_shape_preserving_seed_guard_covered(self, rigid_initialization):
        if rigid_initialization is None:
            return False
        metadata = rigid_initialization.metadata
        return (
            bool(metadata.get("shape_preserving_rollout_eligible", True))
            and metadata.get("shape_preserving_rollout_fallback_reason") is None
            and
            int(metadata.get("shape_preserving_orientation_pair_count", 0)) > 0
            and int(metadata.get("legacy_orientation_proxy_pair_count", 0)) == 0
        )

    def _select_guarded_role_aware_local_placement(self,
                                                   rigid_initialization,
                                                   refinement):
        covered_shape_preserving_case = (
            self._is_shape_preserving_seed_guard_covered(rigid_initialization)
        )
        if not covered_shape_preserving_case:
            return refinement, "downstream_refinement", None, False

        rigid_rotation = np.asarray(rigid_initialization.rotation_matrix, dtype=float)
        rigid_translation = np.asarray(
            rigid_initialization.translation_vector,
            dtype=float,
        )
        refined_rotation = np.asarray(refinement.rotation_matrix, dtype=float)
        refined_translation = np.asarray(refinement.translation_vector, dtype=float)

        if np.allclose(rigid_rotation, refined_rotation, atol=1.0e-8) and np.allclose(
            rigid_translation,
            refined_translation,
            atol=1.0e-8,
        ):
            return refinement, "downstream_refinement", None, True

        return (
            rigid_initialization,
            "rigid_seed",
            "shape_preserving_semantic_seed_preserved",
            True,
        )

    def _convert_role_aware_rotation_to_optimizer_frame(self, rotation_matrix):
        """Convert contract-space row-vector rotations to the optimizer's stored frame."""
        return np.asarray(rotation_matrix, dtype=float).T

    def _build_guarded_fallback_debug_records(self,
                                              pname_set_dict,
                                              *,
                                              fallback_reason):
        debug_records = {}
        for group_name, group_data in pname_set_dict.items():
            if not group_data["ind_ofsortednodes"]:
                continue
            node_id = self.sorted_nodes[group_data["ind_ofsortednodes"][0]]
            debug_records[node_id] = self._build_guarded_debug_record(
                group_name=group_name,
                node_id=node_id,
                status="fallback",
                fallback_reason=fallback_reason,
            )
        return debug_records

    def _build_guarded_debug_record(
        self,
        *,
        group_name,
        node_id,
        status,
        node_record=None,
        node_contract=None,
        correspondences=None,
        rigid_initialization=None,
        refinement=None,
        ambiguity_resolution=None,
        covered_shape_preserving_case=False,
        selected_pose_source=None,
        guard_reason=None,
        fallback_reason=None,
        error_message=None,
    ):
        selected_assignment = {}
        candidate_scores = ()
        selected_candidate_score = None
        active_rigid_initialization = rigid_initialization
        if active_rigid_initialization is None and refinement is not None:
            active_rigid_initialization = refinement.rigid_initialization
        if refinement is not None:
            selected_assignment = dict(
                refinement.correspondence.edge_to_slot_index.items()
            )
        elif active_rigid_initialization is not None:
            selected_assignment = dict(
                active_rigid_initialization.correspondence.edge_to_slot_index.items()
            )
        if ambiguity_resolution is not None:
            candidate_scores = tuple(
                float(candidate.score)
                for candidate in ambiguity_resolution.candidates
            )
            selected_candidate_score = float(
                ambiguity_resolution.selected_candidate.score
            )
        elif active_rigid_initialization is not None:
            candidate_scores = (float(active_rigid_initialization.rmsd),)
            selected_candidate_score = candidate_scores[0]

        null_edge_count = 0
        alignment_only_count = 0
        resolve_mode_hints = ()
        local_slot_types = ()
        incident_edge_ids = ()
        if node_contract is not None:
            null_edge_count = int(sum(node_contract.null_edge_flags.values()))
            alignment_only_count = sum(
                1
                for requirement in node_contract.incident_requirements
                if requirement.resolve_mode == "alignment_only"
            )
            resolve_mode_hints = tuple(node_contract.resolve_mode_hints)
            local_slot_types = tuple(node_contract.local_slot_types)
            incident_edge_ids = tuple(node_contract.incident_edge_ids)

        return {
            "group_name": group_name,
            "node_id": node_id,
            "node_role_id": getattr(node_record, "role_id", None),
            "node_role_class": getattr(node_record, "role_class", None),
            "status": status,
            "fallback_reason": fallback_reason,
            "error_message": error_message,
            "candidate_count": len(correspondences or ()),
            "selected_assignment": selected_assignment,
            "candidate_scores": candidate_scores,
            "selected_candidate_score": selected_candidate_score,
            "refinement_objective_value": (
                float(refinement.objective_value)
                if refinement is not None
                else None
            ),
            "refinement_initial_objective_value": (
                float(refinement.initial_objective_value)
                if refinement is not None
                else None
            ),
            "selected_pose_source": selected_pose_source,
            "guard_preserved_seed": guard_reason is not None,
            "guard_reason": guard_reason,
            "covered_shape_preserving_case": covered_shape_preserving_case,
            "orientation_only_pair_count": (
                active_rigid_initialization.metadata.get(
                    "orientation_only_pair_count",
                    0,
                )
                if active_rigid_initialization is not None
                else 0
            ),
            "shape_preserving_orientation_pair_count": (
                active_rigid_initialization.metadata.get(
                    "shape_preserving_orientation_pair_count",
                    0,
                )
                if active_rigid_initialization is not None
                else 0
            ),
            "stable_shape_support_pair_count": (
                active_rigid_initialization.metadata.get(
                    "stable_shape_support_pair_count",
                    0,
                )
                if active_rigid_initialization is not None
                else 0
            ),
            "legacy_orientation_proxy_pair_count": (
                active_rigid_initialization.metadata.get(
                    "legacy_orientation_proxy_pair_count",
                    0,
                )
                if active_rigid_initialization is not None
                else 0
            ),
            "null_edge_count": null_edge_count,
            "alignment_only_count": alignment_only_count,
            "resolve_mode_hints": resolve_mode_hints,
            "local_slot_types": local_slot_types,
            "incident_edge_ids": incident_edge_ids,
            "used_ambiguity_resolution": ambiguity_resolution is not None,
        }

    def _get_semantic_edge_record(self, edge):
        if self.semantic_snapshot is None:
            return None
        edge_id = "|".join(str(node_name) for node_name in edge)
        record = self.semantic_snapshot.graph_edge_records.get(edge_id)
        if record is not None:
            return record
        return self.semantic_snapshot.graph_edge_records.get(
            "|".join(str(node_name) for node_name in reversed(edge))
        )

    def _is_semantic_null_edge(self, edge, *, edge_role_id=None, edge_record=None):
        if self.semantic_snapshot is None:
            return False
        record = edge_record if edge_record is not None else self._get_semantic_edge_record(edge)
        if record is not None:
            if bool(record.is_null_edge):
                return True
            if record.edge_role_id is not None:
                edge_role_id = record.edge_role_id
        if edge_role_id is None:
            return False
        policy_record = self.semantic_snapshot.null_edge_policy_records.get(edge_role_id)
        if policy_record is not None and bool(policy_record.is_null_edge):
            return True
        edge_role_record = self.semantic_snapshot.edge_role_records.get(edge_role_id)
        if edge_role_record is None:
            return False
        if edge_role_record.null_edge_policy is not None:
            return bool(edge_role_record.null_edge_policy.is_null_edge)
        return edge_role_record.edge_kind == "null"

    def _get_slot_rule_by_attachment_index(self, slot_rules, attachment_index):
        if attachment_index is None:
            return {}
        for slot_rule in slot_rules or ():
            if slot_rule.get("attachment_index") == attachment_index:
                return slot_rule
        return {}

    def _get_resolved_anchor_descriptor(self, slot_rule, *, slot_index=None):
        source_atom_type = (
            slot_rule.get("anchor_source_type")
            or slot_rule.get("source_atom_type")
            or slot_rule.get("slot_type")
        )
        source_ordinal = slot_rule.get("anchor_source_ordinal")
        if source_ordinal is None:
            source_ordinal = slot_rule.get("attachment_index", slot_index)
        if source_atom_type is None or source_ordinal is None:
            return None, None
        return str(source_atom_type), int(source_ordinal)

    def _resolve_semantic_node_anchor_position(self, node_id, edge_record):
        node_record = self.semantic_snapshot.graph_node_records.get(str(node_id))
        if node_record is None:
            raise ValueError(
                f"Missing builder-compiled resolved anchor semantics for node {node_id} during optimizer placement."
            )
        slot_index = (edge_record.slot_index or {}).get(node_id)
        slot_rule = self._get_slot_rule_by_attachment_index(
            node_record.slot_rules,
            slot_index,
        )
        source_atom_type, source_ordinal = self._get_resolved_anchor_descriptor(
            slot_rule,
            slot_index=slot_index,
        )
        if source_atom_type is None or source_ordinal is None:
            raise ValueError(
                f"Missing resolved anchor source metadata for edge {edge_record.edge_id} on node {node_id}."
            )

        attachment_lookup = self.sc_rot_node_attachment_lookup.get(str(node_id), {})
        anchor_position = attachment_lookup.get((source_atom_type, source_ordinal))
        if anchor_position is not None:
            return np.asarray(anchor_position, dtype=float)

        if source_atom_type == "X":
            node_index = self.sorted_nodes.index(node_id)
            x_positions = self.sc_rot_node_X_pos.get(node_index)
            if x_positions is not None and source_ordinal < len(x_positions):
                return np.asarray(x_positions[source_ordinal][1:], dtype=float)

        raise ValueError(
            f"Missing builder-compiled resolved anchor position for edge {edge_record.edge_id} on node {node_id} "
            f"(source_atom_type={source_atom_type}, source_ordinal={source_ordinal})."
        )

    def _resolve_semantic_edge_anchor_coords(self, edge, edge_payload):
        edge_record = self._get_semantic_edge_record(edge)
        if edge_record is None:
            raise ValueError(
                f"Missing builder-compiled resolved anchor semantics for edge {'|'.join(str(node_name) for node_name in edge)} during optimizer placement."
            )

        endpoint_coords = []
        for node_id in edge:
            slot_index = (edge_record.slot_index or {}).get(node_id)
            slot_rule = self._get_slot_rule_by_attachment_index(
                edge_record.slot_rules,
                slot_index,
            )
            source_atom_type, source_ordinal = self._get_resolved_anchor_descriptor(
                slot_rule,
                slot_index=slot_index,
            )
            if source_atom_type is None or source_ordinal is None:
                raise ValueError(
                    f"Missing edge-anchor source metadata for edge {edge_record.edge_id} at endpoint {node_id}."
                )
            coords = np.asarray(
                edge_payload.get("attachment_coords_by_type", {}).get(source_atom_type, ()),
                dtype=float,
            ).reshape(-1, 3)
            if coords.shape[0] > source_ordinal:
                endpoint_coords.append(coords[source_ordinal])
                continue
            if source_atom_type == "X" and edge_payload["x_coords"].shape[0] > source_ordinal:
                endpoint_coords.append(edge_payload["x_coords"][source_ordinal])
                continue
            raise ValueError(
                f"Missing builder-compiled resolved edge anchor coordinates for edge {edge_record.edge_id} "
                f"(source_atom_type={source_atom_type}, source_ordinal={source_ordinal})."
            )
        return edge_record, np.asarray(endpoint_coords, dtype=float)

    def _should_use_semantic_anchor_placement(self):
        if not self.use_role_aware_local_placement:
            return False
        if self.semantic_snapshot is None:
            raise ValueError(
                "Missing builder-compiled resolved anchor semantics: OptimizationSemanticSnapshot is required for role-aware optimizer placement."
            )
        return True

    def place_edge_in_net(self):
        """
        based on the optimized rotations and cell parameters, use optimized pair to find connected X-X pair in optimized cell,
        and place the edge in the target MOF cell

        return:
            sG (networkx graph):graph of the target MOF cell, with scaled and rotated node and edge positions
        """
        # linker_middle_point = np.mean(linker_x_vecs,axis=0)
        optimized_pair = self.optimized_pair
        scaled_rotated_Xatoms_positions = self.sc_rot_node_X_pos
        scaled_rotated_node_positions = self.sc_rot_node_pos
        sorted_nodes = self.sorted_nodes
        sG = self.sG.copy()
        sc_unit_cell_inv = self.sc_unit_cell_inv
        nodes_atom = self.nodes_atom
        norm_xx_vector_record = []
        rot_record = []
        use_semantic_anchors = self._should_use_semantic_anchor_placement()
        edge_items = (
            [
                (edge, optimized_pair.get(edge, (0, 0)))
                for edge in self.sorted_edges
            ]
            if use_semantic_anchors
            else optimized_pair.items()
        )

        # edges = {}
        for (i, j), pair in edge_items:
            edge_payload = self.edge_fragment_payloads[(i, j)]
            if use_semantic_anchors:
                edge_record, e_xx_vec = self._resolve_semantic_edge_anchor_coords(
                    (i, j),
                    edge_payload,
                )
            else:
                edge_record = None
                e_xx_vec = edge_payload["x_coords"]
            linker_frag_length = edge_payload["linker_frag_length"]
            if linker_frag_length > 0.0:
                scalar = (linker_frag_length +
                          2 * self.constant_length) / linker_frag_length
            else:
                scalar = 1.0

            extended_e_xx_vec = [coord * scalar for coord in e_xx_vec]
            x_idx_i, x_idx_j = pair
            if use_semantic_anchors:
                x_i = self._resolve_semantic_node_anchor_position(i, edge_record)
                x_j = self._resolve_semantic_node_anchor_position(j, edge_record)
            else:
                reindex_i = sorted_nodes.index(i)
                reindex_j = sorted_nodes.index(j)
                x_i = scaled_rotated_Xatoms_positions[reindex_i][x_idx_i][1:]
                x_j = scaled_rotated_Xatoms_positions[reindex_j][x_idx_j][1:]
            x_i_x_j_middle_point = np.mean([x_i, x_j], axis=0)
            xx_vector = np.vstack(
                [x_i - x_i_x_j_middle_point, x_j - x_i_x_j_middle_point])
            norm_xx_vector = xx_vector / np.linalg.norm(xx_vector)

            if self._debug:
                self.ostream.print_info(
                    f"Placing edge between Node {i} and Node {j}")
                self.ostream.print_info(
                    f"  X atom index in Node {i}: {x_idx_i}, coordinates: {x_i}"
                )
                self.ostream.print_info(
                    f"  X atom index in Node {j}: {x_idx_j}, coordinates: {x_j}"
                )
                self.ostream.print_info(
                    f"  Middle point: {x_i_x_j_middle_point}")
                self.ostream.print_info(f"  Original XX vector: {xx_vector}")
                self.ostream.print_info(
                    f"  Normalized XX vector: {norm_xx_vector}")
                self.ostream.flush()
            # use superimpose to get the rotation matrix
            # use record to record the rotation matrix for get rid of the repeat calculation
            if linker_frag_length >= 0.0:
                # for normal linker, the direction is important
                indices = [
                    index for index, value in enumerate(norm_xx_vector_record)
                    if value["role_id"] == sG.edges[(i, j)].get("edge_role_id")
                    and is_list_A_in_B(norm_xx_vector, value["xx_vector"])
                ]
                if len(indices) == 1:
                    rot = rot_record[indices[0]]
                    # rot = reorthogonalize_matrix(rot)
                else:
                    _, rot, trans = superimpose_topology_hungarian(
                        extended_e_xx_vec, xx_vector)
                    # rot = reorthogonalize_matrix(rot)
                    norm_xx_vector_record.append({
                        "role_id": sG.edges[(i, j)].get("edge_role_id"),
                        "xx_vector": norm_xx_vector,
                    })
                    # the rot may be opposite, so we need to check the angle between the two vectors
                    # if the angle is larger than 90 degree, we need to reverse the rot
                    roted_xx = np.dot(extended_e_xx_vec, rot)

                    if np.dot(roted_xx[1] - roted_xx[0],
                              xx_vector[1] - xx_vector[0]) < 0:
                        ##rotate 180 around the axis of the cross product of the two vectors
                        axis = np.cross(roted_xx[1] - roted_xx[0],
                                        xx_vector[1] - xx_vector[0])
                        # if 001 not linear to the two vectors
                        if np.linalg.norm(axis) == 0:
                            check_z_axis = np.cross(roted_xx[1] - roted_xx[0],
                                                    [0, 0, 1])
                            if np.linalg.norm(check_z_axis) == 0:
                                axis = np.array([1, 0, 0])
                            else:
                                axis = np.array([0, 0, 1])

                        axis = axis / np.linalg.norm(axis)
                        flip_matrix = np.eye(3) - 2 * np.outer(
                            axis, axis)  # Householder matrix for reflection
                        rot = np.dot(rot, flip_matrix)
                    # Flip the last column of the rotation matrix if the determinant is negative
                    rot_record.append(rot)
            else:
                #get a random rotation matrix
                rot = np.eye(3)

            # use the rotation matrix to rotate the linker x coords
            placed_edge_ccoords = (np.dot(edge_payload["coords"], rot) +
                                   x_i_x_j_middle_point)

            placed_edge = np.hstack(
                (np.asarray(edge_payload["atom"]), placed_edge_ccoords))
            sG.edges[(i, j)]["coords"] = x_i_x_j_middle_point
            sG.edges[(i, j)]["c_points"] = placed_edge

            sG.edges[(i, j)]["f_points"] = np.hstack((
                placed_edge[:, 0:2],
                cartesian_to_fractional(placed_edge[:, 2:5], sc_unit_cell_inv),
            ))

            _, sG.edges[(i, j)]["x_coords"] = fetch_X_atoms_ind_array(
                placed_edge, 0, "X")
        for i, v in scaled_rotated_node_positions.items():
            k = sorted_nodes[i]
            pos = v[:, 1:]  #cause first column is index added by addidx
            sG.nodes[k]["c_points"] = np.hstack((nodes_atom[k], pos))
            sG.nodes[k]["f_points"] = np.hstack(
                (nodes_atom[k], cartesian_to_fractional(pos,
                                                        sc_unit_cell_inv)))
            # find the atoms starts with "x" and extract the coordinates
            _, sG.nodes[k]["x_coords"] = fetch_X_atoms_ind_array(
                sG.nodes[k]["c_points"], 0, "X")
        self.sG = sG
        return sG

    def _get_edge_lengths(self, G):
        """Compute edge length (distance between node ccoords) for each edge. Returns (edge_lengths dict, set of lengths)."""
        edge_lengths = {}
        lengths = []
        for e in G.edges():
            i, j = e
            length = np.linalg.norm(G.nodes[i]["ccoords"] -
                                    G.nodes[j]["ccoords"])
            length = np.round(length, 3)
            edge_lengths[(i, j)] = length
            edge_lengths[(j, i)] = length
            lengths.append(length)
        if self._debug:
            self.ostream.print_info(f"Edge lengths: {edge_lengths}")
            self.ostream.print_info(
                f"Set of unique edge lengths: {set(lengths)}")
        if len(set(lengths)) != 1:
            self.ostream.print_warning(
                "Warning: more than one type of edge length")
            # if the length are close, which can be shown by std
            if np.std(lengths) < 1:  #1 Angstrom
                self.ostream.print_info("the edge lengths are close")
            else:
                self.ostream.print_info("the edge lengths are not close")
            self.ostream.print_info(str(set(lengths)))
        return edge_lengths, set(lengths)

    def _apply_rot2atoms_pos(self, optimized_rotations, G, node_X_pos_dict):
        """Apply optimized rotation matrices to node X positions and compute edge pairings.

        Args:
            optimized_rotations: Rotation matrix per node (by sorted_nodes index).
            G: Net graph with node "ccoords".
            node_X_pos_dict: Dict mapping node index to (N, 4) array [idx, x, y, z].

        Returns:
            Tuple (rotated_positions, optimized_pair): Rotated positions dict and edge (i,j) -> (x_idx_i, x_idx_j).
        """
        rotated_positions = node_X_pos_dict.copy()
        sorted_nodes = self.sorted_nodes
        sorted_edges_of_sortednodeidx = self.sorted_edges_of_sortednodeidx

        for i, node in enumerate(sorted_nodes):
            # if node type is V
            # if 'DV' in G.nodes[node]['type']:
            # continue
            R = optimized_rotations[i]

            original_positions = rotated_positions[i][:, 1:]
            com = G.nodes[node]["ccoords"]

            # Translate, rotate, and translate back to preserve the mass center
            translated_positions = original_positions - com
            rotated_translated_positions = np.dot(translated_positions, R.T)
            rotated_positions[i][:, 1:] = rotated_translated_positions + com
        edge_pair = find_edge_pairings(sorted_nodes,
                                       sorted_edges_of_sortednodeidx,
                                       rotated_positions)
        if self._debug:
            self.ostream.print_info(
                f"Optimized Pairings (after optimization): {edge_pair}")

        optimized_pair = {}
        for (i, j), pair in edge_pair.items():
            if self._debug:
                self.ostream.print_info(
                    f"Node {sorted_nodes[i]} and Node {sorted_nodes[j]}:")
            idx_i, idx_j = pair

            if self._debug:
                self.ostream.print_info(
                    f"Node{sorted_nodes[i]}_{int(idx_i)} -- Node{sorted_nodes[j]}_{int(idx_j)}"
                )
            optimized_pair[sorted_nodes[i],
                           sorted_nodes[j]] = (int(idx_i), int(idx_j))

        return rotated_positions, optimized_pair

    def _fragment_payload_from_arrays(self,
                                      data,
                                      x_data,
                                      *,
                                      attachment_data_by_type=None,
                                      attachment_coords_by_type=None,
                                      attachment_metadata=None,
                                      attachment_lookup=None,
                                      linker_frag_length=None,
                                      fake_edge=False):
        normalized_attachment_coords = self._resolve_attachment_coords_by_type(
            attachment_coords_by_type=attachment_coords_by_type,
            attachment_data_by_type=attachment_data_by_type,
            fallback_x_data=x_data,
        )
        normalized_attachment_metadata, normalized_attachment_lookup = (
            self._resolve_attachment_metadata(
                attachment_metadata=attachment_metadata,
                attachment_lookup=attachment_lookup,
                attachment_coords_by_type=normalized_attachment_coords,
            )
        )
        x_coords = self._flatten_attachment_coords(
            normalized_attachment_coords,
            attachment_metadata=normalized_attachment_metadata,
        )
        assert_msg_critical(
            data is not None and x_coords is not None and x_coords.shape[0] > 0,
            "Optimizer fragment payload is missing atom or attachment coordinate data.")
        return {
            "atom": data[:, 0:2],
            "coords": data[:, 5:8].astype(float),
            "x_coords": x_coords,
            "attachment_coords_by_type": normalized_attachment_coords,
            "attachment_metadata": normalized_attachment_metadata,
            "attachment_lookup": normalized_attachment_lookup,
            "linker_frag_length": linker_frag_length,
            "fake_edge": fake_edge,
        }

    def _extract_attachment_coords_from_data_by_type(self, attachment_data_by_type):
        coords_by_type = {}
        for atom_type, rows in (attachment_data_by_type or {}).items():
            if rows is None:
                continue
            array = np.asarray(rows, dtype=object)
            if array.size == 0:
                coords_by_type[str(atom_type)] = np.empty((0, 3), dtype=float)
                continue
            coords_by_type[str(atom_type)] = array[:, 5:8].astype(float)
        return coords_by_type

    def _normalize_attachment_coords_by_type(self,
                                             attachment_coords_by_type,
                                             *,
                                             fallback_x_coords=None):
        normalized = {}
        if attachment_coords_by_type:
            for atom_type, coords in attachment_coords_by_type.items():
                if coords is None:
                    continue
                array = np.asarray(coords, dtype=float)
                if array.size == 0:
                    normalized[str(atom_type)] = np.empty((0, 3), dtype=float)
                    continue
                normalized[str(atom_type)] = array.reshape(-1, 3)
        if not normalized and fallback_x_coords is not None:
            normalized["X"] = np.asarray(fallback_x_coords,
                                          dtype=float).reshape(-1, 3)
        return normalized

    def _is_legacy_x_only_attachment_coords(self, attachment_coords_by_type):
        nonempty_types = []
        for atom_type, coords in (attachment_coords_by_type or {}).items():
            if coords is None:
                continue
            array = np.asarray(coords, dtype=float).reshape(-1, 3)
            if array.size == 0:
                continue
            nonempty_types.append(str(atom_type))
        return bool(nonempty_types) and set(nonempty_types) <= {"X"}

    def _resolve_attachment_coords_by_type(self,
                                           *,
                                           attachment_coords_by_type=None,
                                           attachment_data_by_type=None,
                                           fallback_x_data=None):
        fallback_x_coords = (
            fallback_x_data[:, 5:8].astype(float)
            if fallback_x_data is not None else None
        )
        normalized_from_coords = self._normalize_attachment_coords_by_type(
            attachment_coords_by_type,
            fallback_x_coords=None,
        )
        if normalized_from_coords:
            return normalized_from_coords
        normalized_from_data = self._normalize_attachment_coords_by_type(
            self._extract_attachment_coords_from_data_by_type(
                attachment_data_by_type
            ),
            fallback_x_coords=None,
        )
        if normalized_from_data:
            return normalized_from_data
        return self._normalize_attachment_coords_by_type(
            None,
            fallback_x_coords=fallback_x_coords,
        )

    def _normalize_attachment_metadata(self, attachment_metadata):
        normalized = []
        for entry in attachment_metadata or ():
            if entry is None:
                continue
            row_index = entry.get("row_index")
            slot_type = entry.get("slot_type")
            slot_ordinal = entry.get("slot_ordinal")
            if row_index is None or slot_type is None or slot_ordinal is None:
                continue
            normalized.append({
                "slot_type": str(slot_type),
                "slot_ordinal": int(slot_ordinal),
                "row_index": int(row_index),
            })
        normalized.sort(
            key=lambda item: (
                item["row_index"],
                item["slot_type"],
                item["slot_ordinal"],
            )
        )
        return tuple(normalized)

    def _compile_attachment_metadata_from_lookup(self, attachment_lookup):
        normalized = []
        for descriptor, row_index in (attachment_lookup or {}).items():
            if not isinstance(descriptor, tuple) or len(descriptor) != 2:
                continue
            slot_type, slot_ordinal = descriptor
            normalized.append({
                "slot_type": str(slot_type),
                "slot_ordinal": int(slot_ordinal),
                "row_index": int(row_index),
            })
        normalized.sort(
            key=lambda item: (
                item["row_index"],
                item["slot_type"],
                item["slot_ordinal"],
            )
        )
        return tuple(normalized)

    def _compile_attachment_lookup_from_metadata(self, attachment_metadata):
        return {
            (entry["slot_type"], entry["slot_ordinal"]): entry["row_index"]
            for entry in attachment_metadata
        }

    def _compile_attachment_metadata_from_coords(self, attachment_coords_by_type):
        assert_msg_critical(
            self._is_legacy_x_only_attachment_coords(attachment_coords_by_type),
            "Optimizer requires builder-defined attachment metadata for mixed typed attachment coordinates; only legacy X-only payloads may derive metadata locally.",
        )
        metadata = []
        lookup = {}
        row_index = 0
        for slot_type in ("X",):
            coords = np.asarray(
                (attachment_coords_by_type or {}).get(slot_type, ()),
                dtype=float,
            ).reshape(-1, 3)
            if coords.size == 0:
                continue
            for slot_ordinal in range(coords.shape[0]):
                entry = {
                    "slot_type": str(slot_type),
                    "slot_ordinal": int(slot_ordinal),
                    "row_index": int(row_index),
                }
                metadata.append(entry)
                lookup[(entry["slot_type"], entry["slot_ordinal"])] = entry["row_index"]
                row_index += 1
        return tuple(metadata), lookup

    def _validate_attachment_metadata_row_indices(self, attachment_metadata):
        if not attachment_metadata:
            return
        row_indices = tuple(entry["row_index"] for entry in attachment_metadata)
        assert_msg_critical(
            row_indices == tuple(range(len(attachment_metadata))),
            "Optimizer attachment metadata row indices must remain contiguous and aligned with flattened attachment rows.",
        )

    def _resolve_attachment_metadata(self,
                                     *,
                                     attachment_metadata=None,
                                     attachment_lookup=None,
                                     attachment_coords_by_type=None):
        normalized_attachment_metadata = self._normalize_attachment_metadata(
            attachment_metadata
        )
        if not normalized_attachment_metadata:
            normalized_attachment_metadata = (
                self._compile_attachment_metadata_from_lookup(
                    attachment_lookup
                )
            )
        if not normalized_attachment_metadata:
            return self._compile_attachment_metadata_from_coords(
                attachment_coords_by_type
            )
        self._validate_attachment_metadata_row_indices(
            normalized_attachment_metadata
        )
        if not self._is_legacy_x_only_attachment_coords(attachment_coords_by_type):
            assert_msg_critical(
                len(normalized_attachment_metadata) == sum(
                    np.asarray(coords, dtype=float).reshape(-1, 3).shape[0]
                    for coords in (attachment_coords_by_type or {}).values()
                    if coords is not None
                ),
                "Optimizer typed attachment metadata must preserve the full flattened attachment-slot count.",
            )
        return (
            normalized_attachment_metadata,
            self._compile_attachment_lookup_from_metadata(
                normalized_attachment_metadata
            ),
        )

    def _flatten_attachment_coords(self,
                                   attachment_coords_by_type,
                                   *,
                                   attachment_metadata=None):
        if not attachment_coords_by_type:
            return None
        flattened_coords = []
        if attachment_metadata:
            for entry in attachment_metadata:
                coords = np.asarray(
                    attachment_coords_by_type.get(entry["slot_type"], ()),
                    dtype=float,
                ).reshape(-1, 3)
                slot_ordinal = entry["slot_ordinal"]
                assert_msg_critical(
                    coords.shape[0] > slot_ordinal,
                    "Optimizer attachment metadata does not align with attachment coordinates.",
                )
                flattened_coords.append(coords[slot_ordinal])
        else:
            for atom_type in sorted(attachment_coords_by_type):
                coords = np.asarray(
                    attachment_coords_by_type[atom_type],
                    dtype=float,
                ).reshape(-1, 3)
                if coords.size == 0:
                    continue
                flattened_coords.append(coords)
        if not flattened_coords:
            return None
        return np.vstack(flattened_coords)

    def _get_single_registry_entry(self, registry):
        if registry and len(registry) == 1:
            return next(iter(registry.values()))
        return None

    def _is_linker_center_node(self, G, node):
        node_data = G.nodes[node]
        node_role_id = node_data.get("node_role_id")
        if isinstance(node_role_id, str):
            if node_role_id.startswith("node:C"):
                return True
            if ":" not in node_role_id and node_role_id.startswith("C"):
                return True

        if node_data.get("note") == "CV":
            return True

        if self.semantic_snapshot is not None:
            node_record = self.semantic_snapshot.graph_node_records.get(str(node))
            if node_record is not None and node_record.role_class == "C":
                return True

        return str(node).startswith("C")

    def _get_node_registry_entry(self, G, node):
        registry = self.node_role_registry or {}
        if not registry:
            return None
        role_id = G.nodes[node].get("node_role_id")
        if role_id in registry:
            return registry[role_id]
        return self._get_single_registry_entry(registry)

    def _get_edge_registry_entry(self, G, edge):
        registry = self.edge_role_registry or {}
        if not registry:
            return None
        role_id = G.edges[edge].get("edge_role_id")
        if role_id in registry:
            return registry[role_id]
        return self._get_single_registry_entry(registry)

    def _get_center_registry_entry_for_node(self, G, node):
        if not (self.edge_role_registry and self._is_linker_center_node(G, node)):
            return None
        for neighbor in G.neighbors(node):
            role_entry = self._get_edge_registry_entry(G, (node, neighbor))
            if (role_entry is not None
                    and role_entry.get("linker_center_data") is not None):
                return role_entry
        return None

    def _resolve_node_fragment_payload(self, G, node):
        if self._is_linker_center_node(G, node):
            role_entry = self._get_center_registry_entry_for_node(G, node)
            if role_entry is not None and role_entry.get("linker_center_data") is not None:
                return self._fragment_payload_from_arrays(
                    role_entry["linker_center_data"],
                    role_entry.get("linker_center_X_data"),
                    attachment_data_by_type=role_entry.get(
                        "linker_center_attachment_data_by_type"
                    ),
                    attachment_coords_by_type=role_entry.get(
                        "linker_center_attachment_coords_by_type"
                    ),
                    attachment_metadata=role_entry.get(
                        "linker_center_attachment_metadata"
                    ),
                    attachment_lookup=role_entry.get(
                        "linker_center_attachment_lookup"
                    ),
                )
            return self._fragment_payload_from_arrays(
                self.EC_data,
                self.EC_X_data,
                attachment_data_by_type=self.EC_attachment_data_by_type,
                attachment_coords_by_type=self.EC_attachment_coords_by_type,
            )

        role_entry = self._get_node_registry_entry(G, node)

        if role_entry is not None and role_entry.get("node_data") is not None:
            return self._fragment_payload_from_arrays(
                role_entry["node_data"],
                role_entry.get("node_X_data"),
                attachment_data_by_type=role_entry.get(
                    "node_attachment_data_by_type"
                ),
                attachment_coords_by_type=role_entry.get(
                    "node_attachment_coords_by_type"
                ),
                attachment_metadata=role_entry.get(
                    "node_attachment_metadata"
                ),
                attachment_lookup=role_entry.get("node_attachment_lookup"),
            )
        return self._fragment_payload_from_arrays(
            self.V_data,
            self.V_X_data,
            attachment_data_by_type=self.V_attachment_data_by_type,
            attachment_coords_by_type=self.V_attachment_coords_by_type,
        )

    def _resolve_edge_fragment_payload(self, G, edge):
        role_entry = self._get_edge_registry_entry(G, edge)
        edge_role_id = G.edges[edge].get("edge_role_id")
        if role_entry is not None:
            if int(role_entry["linker_connectivity"]) > 2:
                data = role_entry.get("linker_outer_data")
                x_data = role_entry.get("linker_outer_X_data")
            else:
                data = role_entry.get("linker_center_data")
                x_data = role_entry.get("linker_center_X_data")
            attachment_coords_by_type = (
                role_entry.get("linker_outer_attachment_coords_by_type")
                if int(role_entry["linker_connectivity"]) > 2
                else role_entry.get("linker_center_attachment_coords_by_type")
            )
            attachment_data_by_type = (
                role_entry.get("linker_outer_attachment_data_by_type")
                if int(role_entry["linker_connectivity"]) > 2
                else role_entry.get("linker_center_attachment_data_by_type")
            )
            if data is not None:
                linker_frag_length = role_entry.get("linker_frag_length")
                if linker_frag_length is None:
                    linker_frag_length = self.linker_frag_length
                payload = self._fragment_payload_from_arrays(
                    data,
                    x_data,
                    attachment_data_by_type=attachment_data_by_type,
                    attachment_coords_by_type=attachment_coords_by_type,
                    attachment_metadata=(
                        role_entry.get("linker_outer_attachment_metadata")
                        if int(role_entry["linker_connectivity"]) > 2
                        else role_entry.get("linker_center_attachment_metadata")
                    ),
                    attachment_lookup=(
                        role_entry.get("linker_outer_attachment_lookup")
                        if int(role_entry["linker_connectivity"]) > 2
                        else role_entry.get("linker_center_attachment_lookup")
                    ),
                    linker_frag_length=linker_frag_length,
                    fake_edge=bool(role_entry.get("linker_fake_edge", False)),
                )
                if self._is_semantic_null_edge(edge, edge_role_id=edge_role_id):
                    payload["fake_edge"] = True
                    payload["linker_frag_length"] = 0.0
                return payload

        payload = self._fragment_payload_from_arrays(
            self.E_data,
            self.E_X_data,
            attachment_data_by_type=self.E_attachment_data_by_type,
            attachment_coords_by_type=self.E_attachment_coords_by_type,
            linker_frag_length=self.linker_frag_length,
            fake_edge=self.fake_edge,
        )
        if self._is_semantic_null_edge(edge, edge_role_id=edge_role_id):
            payload["fake_edge"] = True
            payload["linker_frag_length"] = 0.0
        return payload

    def _prepare_role_fragment_payloads(self, G):
        self.node_fragment_payloads = {}
        self.nodes_atom = {}
        for node in self.sorted_nodes:
            payload = self._resolve_node_fragment_payload(G, node)
            self.node_fragment_payloads[node] = payload
            self.nodes_atom[node] = payload["atom"]

        self.edge_fragment_payloads = {}
        for edge in self.sorted_edges:
            payload = self._resolve_edge_fragment_payload(G, edge)
            self.edge_fragment_payloads[edge] = payload
            self.edge_fragment_payloads[(edge[1], edge[0])] = payload

    def _addidx(self, array):
        row_indices = np.arange(array.shape[0]).reshape(-1, 1).astype(int)
        return np.hstack((row_indices, array))

    def _generate_attachment_position_dict(self, sG):
        position_dict = {}
        metadata_by_node = {}
        for idx, node in enumerate(self.sorted_nodes):
            payload = self.node_fragment_payloads[node]
            x_coords = np.asarray(
                payload.get("x_coords", ()),
                dtype=float,
            ).reshape(-1, 3)
            metadata = tuple(payload.get("attachment_metadata", ()))
            assert_msg_critical(
                x_coords.shape[0] == len(metadata),
                "Optimizer attachment metadata count must align with flattened attachment coordinates.",
            )
            if x_coords.size == 0:
                position_dict[idx] = np.empty((0, 4), dtype=float)
            else:
                position_dict[idx] = self._addidx(
                    sG.nodes[node]["ccoords"] + x_coords
                )
            metadata_by_node[idx] = metadata
        return position_dict, metadata_by_node

    def _apply_rotations_to_position_dict(self, optimized_rotations, G, position_dict):
        rotated_positions = {
            key: np.array(value, copy=True)
            for key, value in position_dict.items()
        }
        for i, node in enumerate(self.sorted_nodes):
            positions = rotated_positions.get(i)
            if positions is None or positions.size == 0:
                continue
            com = G.nodes[node]["ccoords"]
            positions[:, 1:] = np.dot(positions[:, 1:] - com,
                                      optimized_rotations[i].T) + com
        return rotated_positions

    def _build_attachment_lookup_from_positions(self,
                                                metadata_by_node,
                                                position_dict):
        lookup = {}
        for node_index, metadata in metadata_by_node.items():
            node_id = self.sorted_nodes[node_index]
            node_lookup = {}
            positions = position_dict.get(node_index)
            if positions is None or positions.size == 0:
                lookup[node_id] = node_lookup
                continue
            for entry in metadata:
                row_index = entry["row_index"]
                source_atom_type = entry["slot_type"]
                source_ordinal = entry["slot_ordinal"]
                if row_index >= positions.shape[0]:
                    continue
                node_lookup[(str(source_atom_type), int(source_ordinal))] = np.asarray(
                    positions[row_index][1:],
                    dtype=float,
                )
            lookup[node_id] = node_lookup
        return lookup

    def _get_target_edge_lengths(self):
        target_edge_lengths = {}
        for edge in self.sorted_edges:
            node_i, node_j = edge
            node_i_payload = self.node_fragment_payloads[node_i]
            node_j_payload = self.node_fragment_payloads[node_j]
            edge_payload = self.edge_fragment_payloads[edge]
            x_com_i = np.mean(np.linalg.norm(node_i_payload["x_coords"], axis=1))
            x_com_j = np.mean(np.linalg.norm(node_j_payload["x_coords"], axis=1))
            if edge_payload["fake_edge"]:
                target_length = self.constant_length + x_com_i + x_com_j
            else:
                target_length = (edge_payload["linker_frag_length"] +
                                 2 * self.constant_length + x_com_i + x_com_j)
            target_edge_lengths[edge] = target_length
            target_edge_lengths[(edge[1], edge[0])] = target_length
        return target_edge_lengths

    def _generate_pos_dict(self, sG):
        """Build dicts of node positions and X-atom positions per node index from sG and node/EC coords."""
        sorted_nodes = self.sorted_nodes

        sc_node_pos_dict = {}
        sc_node_X_pos_dict = {}
        for idx, node in enumerate(sorted_nodes):
            payload = self.node_fragment_payloads[node]
            sc_node_X_pos_dict[idx] = self._addidx(sG.nodes[node]["ccoords"] +
                                                   payload["x_coords"])
            sc_node_pos_dict[idx] = self._addidx(sG.nodes[node]["ccoords"] +
                                                 payload["coords"])
        return sc_node_pos_dict, sc_node_X_pos_dict

    def _apply_rot_trans2dict(self, sG, sc_node_pos_dict, sc_node_X_pos_dict):
        """Apply per-pname rotation and translation to node and X positions in place."""
        sorted_nodes = self.sorted_nodes
        pname_set_dict = self.pname_set_dict
        opt_rots = self.opt_rots
        for p_name in pname_set_dict:
            rot, trans = pname_set_dict[p_name]["rot_trans"]
            for k in pname_set_dict[p_name]["ind_ofsortednodes"]:
                node = sorted_nodes[k]
                sc_node_X_pos_dict[k][:, 1:] = (np.dot(
                    sc_node_X_pos_dict[k][:, 1:] - sG.nodes[node]["ccoords"],
                    rot,
                ) + trans + sG.nodes[node]["ccoords"])

                sc_node_pos_dict[k][:, 1:] = (np.dot(
                    sc_node_pos_dict[k][:, 1:] - sG.nodes[node]["ccoords"],
                    rot) + trans + sG.nodes[node]["ccoords"])

        return sc_node_pos_dict, sc_node_X_pos_dict

    def _generate_pname_set(self, G, sorted_nodes, node_X_pos_dict):
        """Build pname set and dict mapping pname to sorted node indices and initial rot_trans per pname."""
        pname_list = [self._get_rotation_group_name(G, n) for n in sorted_nodes]
        pname_set = set(pname_list)
        pname_set_dict = {}
        for n in pname_set:
            pname_set_dict[n] = {
                "ind_ofsortednodes": [],
            }
        for i, node in enumerate(sorted_nodes):
            group_name = self._get_rotation_group_name(G, node)
            pname_set_dict[group_name]["ind_ofsortednodes"].append(i)
            if len(pname_set_dict[group_name]
                   ["ind_ofsortednodes"]) == 1:  # first node
                anchor_rows = node_X_pos_dict[i].shape[0]
                node_degree = len(list(G.neighbors(node)))
                assert_msg_critical(
                    anchor_rows == node_degree,
                    f"Optimizer node anchor count must match graph degree before rotation seeding for {node}: got {anchor_rows} anchors and {node_degree} neighbors.",
                )
                pname_set_dict[group_name]["rot_trans"] = get_rot_trans_matrix(
                        node, G, sorted_nodes,
                        node_X_pos_dict)  # initial guess

        if self._debug:
            self.ostream.print_info(f"sorted_nodes: {sorted_nodes} ")
            self.ostream.print_info(f"pname_set: {pname_set}")
            self.ostream.print_info(f"pname_set_dict: {pname_set_dict}")
        return pname_set, pname_set_dict

    def _get_rotation_group_name(self, G, node):
        role_id = G.nodes[node].get("node_role_id")
        if role_id is None:
            return pname(node)
        if role_id == "node:default" and (not self.node_role_registry
                                           or len(self.node_role_registry) <= 1):
            return pname(node)
        return f"{pname(node)}::{role_id}"

    def _update_node_ccoords(self, G, edge_lengths, start_node,
                             new_edge_lengths):
        """Propagate node positions from start_node so edge lengths match per-edge target lengths."""
        updated_ccoords = {}
        original_ccoords = {}
        updated_ccoords[start_node] = G.nodes[start_node]["ccoords"]
        original_ccoords[start_node] = G.nodes[start_node]["ccoords"]
        updated_node = [start_node]
        # to update all the nodes start from the startnode and spread to neighbors
        for i in range(len(G.nodes()) - 1):
            for n in updated_node:
                for nn in G.neighbors(n):
                    if nn in updated_node:
                        continue
                    edge = (n, nn)
                    edge_length = edge_lengths[edge]
                    target_edge_length = new_edge_lengths[edge]
                    updated_ccoords[nn] = (
                        updated_ccoords[n] +
                        (G.nodes[nn]["ccoords"] - G.nodes[n]["ccoords"]) *
                        target_edge_length / edge_length)
                    original_ccoords[nn] = G.nodes[nn]["ccoords"]
                    updated_node.append(nn)

        return updated_ccoords, original_ccoords

    def _update_ccoords_by_optimized_cell_params(self, G, optimized_params):
        """Update node ccoords in G from fcoords using the optimized unit cell matrix."""
        sG = G.copy()
        a, b, c, alpha, beta, gamma = optimized_params
        T_unitcell = unit_cell_to_cartesian_matrix(a, b, c, alpha, beta, gamma)
        updated_ccoords = {}
        for n in sG.nodes():
            updated_ccoords[n] = fractional_to_cartesian(
                T_unitcell, sG.nodes[n]["fcoords"].T).T
            sG.nodes[n]["ccoords"] = updated_ccoords[n]
        return sG, updated_ccoords

    def compile_node_placement_contract(self,
                                        node_id,
                                        semantic_snapshot=None):
        snapshot = semantic_snapshot or self.semantic_snapshot
        if snapshot is None:
            raise ValueError(
                "OptimizationSemanticSnapshot is required to compile a node placement contract."
            )
        return compile_node_placement_contract(snapshot, node_id)

    def compile_legal_node_correspondences(self,
                                           node_id,
                                           semantic_snapshot=None,
                                           node_contract=None):
        snapshot = semantic_snapshot or self.semantic_snapshot
        if snapshot is None:
            raise ValueError(
                "OptimizationSemanticSnapshot is required to compile legal node correspondences."
            )
        return compile_legal_node_correspondences(
            snapshot,
            node_id,
            node_contract=node_contract,
        )

    def compile_local_rigid_initialization(self,
                                           node_id,
                                           semantic_snapshot=None,
                                           node_contract=None,
                                           correspondence=None):
        snapshot = semantic_snapshot or self.semantic_snapshot
        if snapshot is None:
            raise ValueError(
                "OptimizationSemanticSnapshot is required to compile local rigid initialization."
            )
        return compile_local_rigid_initialization(
            snapshot,
            node_id,
            node_contract=node_contract,
            correspondence=correspondence,
        )

    def compile_discrete_ambiguity_resolution(self,
                                              node_id,
                                              semantic_snapshot=None,
                                              node_contract=None,
                                              correspondences=None):
        snapshot = semantic_snapshot or self.semantic_snapshot
        if snapshot is None:
            raise ValueError(
                "OptimizationSemanticSnapshot is required to compile discrete ambiguity resolution."
            )
        return compile_discrete_ambiguity_resolution(
            snapshot,
            node_id,
            node_contract=node_contract,
            correspondences=correspondences,
        )

    def compile_local_constrained_refinement(self,
                                             node_id,
                                             semantic_snapshot=None,
                                             node_contract=None,
                                             correspondence=None,
                                             rigid_initialization=None,
                                             ambiguity_resolution=None,
                                             objective_weights=None):
        snapshot = semantic_snapshot or self.semantic_snapshot
        if snapshot is None:
            raise ValueError(
                "OptimizationSemanticSnapshot is required to compile local constrained refinement."
            )
        return compile_local_constrained_refinement(
            snapshot,
            node_id,
            node_contract=node_contract,
            correspondence=correspondence,
            rigid_initialization=rigid_initialization,
            ambiguity_resolution=ambiguity_resolution,
            objective_weights=objective_weights,
        )


class OptimizationDriver:
    """Driver for two-stage rotation optimization and cell-parameter optimization.

    Stage 1: minimize distance from rotated X positions to neighbor COMs.
    Stage 2: minimize pairwise distances between paired X atoms across edges.
    Cell optimization minimizes fractional-coordinate change when scaling the cell.
    """

    def __init__(self, comm=None, ostream=None):
        self.comm = comm or MPI.COMM_WORLD
        self.rank = self.comm.Get_rank()
        self.nodes = self.comm.Get_size()
        self.ostream = ostream or OutputStream(sys.stdout if self.rank ==
                                               mpi_master() else None)

        # attributes to be set before use
        self.sorted_nodes = None
        self.sorted_edges = None
        self.pname_set_dict = None

        self.initial_rotations = None
        self.initial_set_rotations = None
        self.optimized_rotations = None
        self.optimized_set_rotations = None
        self.static_atom_positions = None

        # Optimization parameters
        self.opt_method = 'L-BFGS-B'
        self.maxfun = 15000
        self.maxiter = 15000
        self.display = True
        self.eps = 1e-8

        self.fixed_cell_shape = False

        self._debug = False

    def _objective_function_pre(self, params, G, static_atom_positions):
        """
        Objective function to minimize distances between paired node to paired node_com along edges.

        Parameters:
            params (numpy.ndarray): Flattened array of rotation matrices.
            G (networkx.Graph): Graph structure.
            atom_positions (dict): Original positions of X atoms for each node.


        Returns:
            float: Total distance metric to minimize.
        """
        # num_nodes = len(G.nodes())

        sorted_nodes = self.sorted_nodes
        sorted_edges = self.sorted_edges
        pname_set_dict = self.pname_set_dict
        set_rotation_matrices = params.reshape(len(pname_set_dict), 3, 3)
        rotation_matrices = expand_set_rots(pname_set_dict,
                                            set_rotation_matrices,
                                            sorted_nodes)
        total_distance = 0.0

        for i, j in sorted_edges:
            R_i = reorthogonalize_matrix(rotation_matrices[i])

            com_i = G.nodes[sorted_nodes[i]]["ccoords"]
            com_j = G.nodes[sorted_nodes[j]]["ccoords"]
            # Rotate positions around their mass center
            rotated_i_positions = (
                np.dot(static_atom_positions[i][:, 1:] - com_i, R_i.T) + com_i)

            #dist_matrix = np.empty((len(rotated_i_positions), 1))
            #for idx_i in range(len(rotated_i_positions)):
            #    dist = np.linalg.norm(rotated_i_positions[idx_i] - com_j)
            #    dist_matrix[idx_i, 0] = dist
            dist_matrix = np.linalg.norm(rotated_i_positions - com_j,
                                         axis=1,
                                         keepdims=True)
            # total_distance += dist ** 2
            if np.argmin(dist_matrix) > 1:
                total_distance += 1e4  # penalty for the distance difference
            total_distance += np.min(dist_matrix)**2

            spread = np.max(dist_matrix) - np.min(dist_matrix)
            # Symmetric edges can produce identical distances for all candidate
            # X atoms, which carries no ordering signal and would otherwise
            # inject an infinite objective into L-BFGS-B.
            if np.isfinite(spread) and spread > 1e-8:
                total_distance += 1e3 / spread

        return total_distance

    def _objective_function_after(self, params, G, static_atom_positions):
        """
        Objective function to minimize distances between paired atoms along edges. just use minimum distance

        Parameters:
            params (numpy.ndarray): Flattened array of rotation matrices.
            G (networkx.Graph): Graph structure.
            atom_positions (dict): Original positions of X atoms for each node.
            edge_pairings (dict): Precomputed pairings for each edge.

        Returns:
            float: Total distance metric to minimize.
        """
        # num_nodes = len(G.nodes())
        set_rotation_matrices = params.reshape(len(self.pname_set_dict), 3, 3)
        rotation_matrices = expand_set_rots(self.pname_set_dict,
                                            set_rotation_matrices,
                                            self.sorted_nodes)
        total_distance = 0.0

        #for i, j in self.sorted_edges:
        #    R_i = reorthogonalize_matrix(rotation_matrices[i])
        #    R_j = reorthogonalize_matrix(rotation_matrices[j])
        #
        #    com_i = G.nodes[self.sorted_nodes[i]]["ccoords"]
        #    com_j = G.nodes[self.sorted_nodes[j]]["ccoords"]

        # Rotate positions around their mass center
        #rotated_i_positions = (
        #    np.dot(static_atom_positions[i][:, 1:] - com_i, R_i.T) + com_i)
        #rotated_j_positions = (
        #    np.dot(static_atom_positions[j][:, 1:] - com_j, R_j.T) + com_j)
        #
        #dist_matrix = np.empty(
        #    (len(rotated_i_positions), len(rotated_j_positions)))
        #for idx_i in range(len(rotated_i_positions)):
        #    for idx_j in range(len(rotated_j_positions)):
        #        dist = np.linalg.norm(rotated_i_positions[idx_i] -
        #                              rotated_j_positions[idx_j])
        #        dist_matrix[idx_i, idx_j] = dist
        for i, j in self.sorted_edges:
            R_i = reorthogonalize_matrix(rotation_matrices[i])
            R_j = reorthogonalize_matrix(rotation_matrices[j])

            com_i = G.nodes[self.sorted_nodes[i]]["ccoords"]
            com_j = G.nodes[self.sorted_nodes[j]]["ccoords"]

            # Rotate positions around their mass center
            rotated_i_positions = (
                np.dot(static_atom_positions[i][:, 1:] - com_i, R_i.T) + com_i
            )  # shape (Ni, 3)
            rotated_j_positions = (
                np.dot(static_atom_positions[j][:, 1:] - com_j, R_j.T) + com_j
            )  # shape (Nj, 3)

            # Vectorized pairwise distance matrix
            diff = rotated_i_positions[:, None, :] - rotated_j_positions[
                None, :, :]
            # shape (Ni, Nj, 3)

            dist_matrix = np.linalg.norm(diff, axis=2)

            if np.argmin(dist_matrix) > 1:
                total_distance += 1e4  # penalty for the distance difference

            total_distance += np.min(dist_matrix)**2

        return total_distance

    def _optimize_rotations_pre(self, num_nodes, G, atom_positions,
                                initial_set_rotations):
        """
        Optimize rotations for all nodes in the graph.

        Parameters:
            G (networkx.Graph): Graph structure with edges between nodes.
            atom_positions (dict): Positions of X atoms for each node.

        Returns:
            list: Optimized rotation matrices for all nodes.
        """

        assert_msg_critical("scipy" in sys.modules,
                            "scipy is required for optimize_rotations_pre.")

        self.ostream.print_info(f"Rotations optimization information:")
        self.ostream.print_info(f"opt_method:, {self.opt_method}")
        self.ostream.print_info(f"maxfun:, {self.maxfun}")
        self.ostream.print_info(f"maxiter:, {self.maxiter}")
        self.ostream.print_info(f"display:, {self.display}")
        self.ostream.print_info(f"eps:, {self.eps}")
        self.ostream.print_info(f"Number of nodes to optimize:, {num_nodes}")
        self.ostream.print_info("\n")
        self.ostream.print_separator()
        self.ostream.print_info(f"Rotation Optimization (stage 1)")
        self.ostream.flush()

        # initial_rotations = np.tile(np.eye(3), (num_nodes, 1)).flatten()
        # get a better initial guess, use random rotation matrix combination
        # initial_rotations  = np.array([reorthogonalize_matrix(np.random.rand(3,3)) for i in range(num_nodes)]).flatten()
        static_atom_positions = atom_positions.copy()
        # Precompute edge-specific pairings
        # edge_pairings = find_edge_pairings(sorted_edges, atom_positions).

        result = minimize(
            self._objective_function_pre,
            initial_set_rotations.flatten(),
            args=(G, static_atom_positions),
            method=self.opt_method,
            options={
                "maxfun": self.maxfun,
                "maxiter": self.maxiter,
                "disp": self.display,
                "eps": self.eps,
                "maxls": 50,
            },
        )

        optimized_rotations = result.x

        return optimized_rotations, static_atom_positions

    def _optimize_rotations_after(self, num_nodes, G, atom_positions,
                                  initial_rotations):
        """
        Optimize rotations for all nodes in the graph.

        Parameters:
            G (networkx.Graph): Graph structure with edges between nodes.
            atom_positions (dict): Positions of X atoms for each node.

        Returns:
            list: Optimized rotation matrices for all nodes.
        """

        assert_msg_critical("scipy" in sys.modules,
                            "scipy is required for optimize_rotations_after.")
        self.ostream.print_info('-' * 20)
        self.ostream.print_info(f"Rotation Optimization (stage 2)")
        self.ostream.print_separator()
        self.ostream.flush()

        # get a better initial guess, use random rotation matrix combination
        # initial_rotations  = np.array([reorthogonalize_matrix(np.random.rand(3,3)) for i in range(num_nodes)]).flatten()
        static_atom_positions = atom_positions.copy()
        # Precompute edge-specific pairings
        # edge_pairings = find_edge_pairings(sorted_edges, atom_positions)

        result = minimize(
            self._objective_function_after,
            initial_rotations.flatten(),
            args=(G, static_atom_positions),
            method=self.opt_method,
            options={
                "maxfun": self.maxfun,
                "maxiter": self.maxiter,
                "disp": self.display,
                "eps": self.eps,
            },
        )

        optimized_rotations = result.x.reshape(-1, 3, 3)
        optimized_rotations = [
            reorthogonalize_matrix(R) for R in optimized_rotations
        ]
        optimized_rotations = np.array(optimized_rotations)

        return optimized_rotations, static_atom_positions

    def _scale_objective_function(self, params, old_cell_params,
                                  old_cartesian_coords, new_cartesian_coords,
                                  ratio_ba, ratio_ca):
        """Sum of squared differences between old fractional coords and new coords in new cell (optionally fixed shape)."""
        a_old, b_old, c_old, alpha_old, beta_old, gamma_old = old_cell_params
        a_new, b_new, c_new, _, _, _ = params
        #constrain the angles to be the same as old cell
        if self.fixed_cell_shape:
            b_new = a_new * ratio_ba
            c_new = a_new * ratio_ca

        # Compute transformation matrix for the old unit cell, T is the unit cell matrix
        T_old = unit_cell_to_cartesian_matrix(a_old, b_old, c_old, alpha_old,
                                              beta_old, gamma_old)
        T_old_inv = np.linalg.inv(T_old)
        old_fractional_coords = cartesian_to_fractional(
            old_cartesian_coords, T_old_inv)

        # backup
        # old_fractional_coords = cartesian_to_fractional(old_cartesian_coords,T_old_inv)

        # Compute transformation matrix for the new unit cell
        T_new = unit_cell_to_cartesian_matrix(a_new, b_new, c_new, alpha_old,
                                              beta_old, gamma_old)
        T_new_inv = np.linalg.inv(T_new)

        # Convert the new Cartesian coordinates to fractional coordinate using the old unit cell

        # Recalculate fractional coordinates from updated Cartesian coordinates
        new_fractional_coords = cartesian_to_fractional(
            new_cartesian_coords, T_new_inv)

        # Compute difference from original fractional coordinates
        diff = new_fractional_coords - old_fractional_coords
        return np.sum(diff**2)  # Sum of squared differences

    def _optimize_cell_params(self, cell_info, original_ccoords,
                              updated_ccoords):
        """Minimize fractional coordinate change when scaling cell to fit updated_ccoords; returns (a, b, c, alpha, beta, gamma)."""
        assert_msg_critical("scipy" in sys.modules,
                            "scipy is required for optimize_cell_parameters.")

        # Old cell parameters (example values)
        old_cell_params = cell_info  # [a, b, c, alpha, beta, gamma]

        # Old Cartesian coordinates of points (example values)
        old_cartesian_coords = np.vstack(list(
            original_ccoords.values()))  # original_ccoords

        # New Cartesian coordinates of the same points (example values)
        new_cartesian_coords = np.vstack(list(
            updated_ccoords.values()))  # updated_ccoords
        # Initial guess for new unit cell parameters (e.g., slightly modified cell)
        initial_params = cell_info

        # Bounds: a, b, c > 3; angles [0, 180]
        bounds = [(3, None), (3, None), (3, None)] + [(20, 180)] * 3

        ratio_ba = round(initial_params[1] / initial_params[0], 5)
        ratio_ca = round(initial_params[2] / initial_params[0], 5)

        # Optimize using L-BFGS-B to minimize the objective function
        result = minimize(
            self._scale_objective_function,
            x0=initial_params,
            args=(old_cell_params, old_cartesian_coords, new_cartesian_coords,
                  ratio_ba, ratio_ca),
            method="L-BFGS-B",
            bounds=bounds,
        )

        # Extract optimized parameters
        optimized_params = np.round(result.x, 5)
        self.ostream.print_info(
            f"Optimized New Cell Parameters: {optimized_params}\nTemplate Cell Parameters: {cell_info}"
        )
        if self.fixed_cell_shape:
            self.ostream.print_info(
                "Note: Cell shape is fixed during optimization.")
            optimized_params[1] = optimized_params[0] * (old_cell_params[1] /
                                                         old_cell_params[0])
            optimized_params[2] = optimized_params[0] * (old_cell_params[2] /
                                                         old_cell_params[0])
        return optimized_params

    def _update_ccoords_by_optimized_cell_params(self, G, optimized_params):
        sG = G.copy()
        a, b, c, alpha, beta, gamma = optimized_params
        T_unitcell = unit_cell_to_cartesian_matrix(a, b, c, alpha, beta, gamma)
        updated_ccoords = {}
        for n in sG.nodes():
            updated_ccoords[n] = fractional_to_cartesian(
                T_unitcell, sG.nodes[n]["fcoords"].T).T
            sG.nodes[n]["ccoords"] = updated_ccoords[n]
        return sG, updated_ccoords


def recenter_and_norm_vectors(vectors, extra_mass_center=None):
    """Center vectors (optionally at extra_mass_center) and normalize each row. Returns (normalized_vectors, mass_center)."""
    vectors = np.asarray(vectors, dtype=float)
    if extra_mass_center is not None:
        mass_center = extra_mass_center
    else:
        mass_center = np.mean(vectors, axis=0)
    vectors = vectors - mass_center
    vectors = vectors / np.linalg.norm(vectors, axis=1)[:, None]
    return vectors, mass_center


def get_connected_nodes_vectors(node, G):
    """Return list of neighbor ccoords and this node's ccoords from G."""
    vectors = []
    for i in list(G.neighbors(node)):
        vectors.append(G.nodes[i]["ccoords"])
    return vectors, G.nodes[node]["ccoords"]


def get_rot_trans_matrix(node, G, sorted_nodes, Xatoms_positions_dict):
    """Compute rotation and translation to align node X vectors to neighbor directions (for initial guess)."""
    node_id = sorted_nodes.index(node)
    node_xvecs = Xatoms_positions_dict[node_id][:, 1:]
    vecsA, _ = recenter_and_norm_vectors(node_xvecs, extra_mass_center=None)
    v2, node_center = get_connected_nodes_vectors(node, G)
    vecsB, _ = recenter_and_norm_vectors(v2, extra_mass_center=node_center)
    rmsd, rot, trans = superimpose_topology_hungarian(vecsA, vecsB)
    return rot, trans


def expand_set_rots(pname_set_dict, set_rotations, sorted_nodes):
    """Expand one rotation per pname to a full list of rotations per sorted_nodes index."""
    set_rotations = set_rotations.reshape(len(pname_set_dict), 3, 3)
    rotations = np.empty((len(sorted_nodes), 3, 3))
    idx = 0
    for name in pname_set_dict:
        for k in pname_set_dict[name]["ind_ofsortednodes"]:
            rotations[k] = set_rotations[idx]
        idx += 1
    return rotations
