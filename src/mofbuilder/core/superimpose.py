import numpy as np
from typing import Union, List, Tuple

try:
    from scipy.optimize import linear_sum_assignment
except ImportError as e:
    raise ImportError(
        "This function requires scipy. Install it with: pip install scipy"
    ) from e


ArrayLike = Union[np.ndarray, List]


def superimpose_topology_hungarian(
    src_arr: ArrayLike,
    target_arr: ArrayLike,
    max_iter: int = 50,
    tol: float = 1e-8,
) -> Tuple[float, np.ndarray, np.ndarray]:
    """
    Align src_arr to target_arr while preserving the original src_arr order.

    Returns:
        rmsd, rot, trans

    Notes:
        - src_arr itself is never modified or reordered.
        - Internally, target points are re-matched to src points by Hungarian assignment.
        - The returned rot/trans apply directly to the original src_arr:
              aligned = src_arr @ rot + trans
    """
    src = np.asarray(src_arr, dtype=float)
    target = np.asarray(target_arr, dtype=float)

    if src.ndim != 2 or src.shape[1] != 3:
        raise ValueError(f"src_arr must have shape (N, 3), got {src.shape}")
    if target.ndim != 2 or target.shape[1] != 3:
        raise ValueError(f"target_arr must have shape (N, 3), got {target.shape}")
    if src.shape != target.shape:
        raise ValueError(
            f"src_arr and target_arr must have the same shape, got "
            f"{src.shape} and {target.shape}"
        )

    n = src.shape[0]

    def kabsch(src_pts: np.ndarray, tgt_pts: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Return rotation and translation aligning src_pts to tgt_pts."""
        com_src = src_pts.mean(axis=0)
        com_tgt = tgt_pts.mean(axis=0)

        src_c = src_pts - com_src
        tgt_c = tgt_pts - com_tgt

        cov = src_c.T @ tgt_c
        U, _, Vt = np.linalg.svd(cov)

        rot = U @ Vt
        if np.linalg.det(rot) < 0:
            Vt[-1, :] *= -1.0
            rot = U @ Vt

        trans = com_tgt - com_src @ rot
        return rot, trans

    def rmsd_of(src_pts: np.ndarray, tgt_pts: np.ndarray, rot: np.ndarray, trans: np.ndarray) -> float:
        diff = tgt_pts - (src_pts @ rot + trans)
        return np.sqrt(np.mean(np.sum(diff**2, axis=1)))

    # Initial guess: identity correspondence
    matched_target = target.copy()
    best_rmsd = np.inf
    best_rot = np.eye(3)
    best_trans = np.zeros(3)

    prev_assignment = None

    for _ in range(max_iter):
        # Solve rigid transform for current correspondence
        rot, trans = kabsch(src, matched_target)

        # Transform original src (without modifying or reordering it)
        src_aligned = src @ rot + trans

        # Build squared-distance cost matrix between transformed src and target
        diff = src_aligned[:, None, :] - target[None, :, :]
        cost = np.sum(diff**2, axis=2)

        # Find best one-to-one assignment
        row_ind, col_ind = linear_sum_assignment(cost)

        # linear_sum_assignment returns sorted row_ind, but we make it explicit
        perm = np.empty(n, dtype=int)
        perm[row_ind] = col_ind

        matched_target_new = target[perm]

        # Recompute transform with updated correspondence
        rot_new, trans_new = kabsch(src, matched_target_new)
        rmsd_new = rmsd_of(src, matched_target_new, rot_new, trans_new)

        if rmsd_new < best_rmsd:
            best_rmsd = rmsd_new
            best_rot = rot_new
            best_trans = trans_new

        # Convergence: assignment unchanged or RMSD improvement tiny
        if prev_assignment is not None and np.array_equal(perm, prev_assignment):
            break
        if np.allclose(matched_target_new, matched_target, atol=tol, rtol=0.0):
            break

        matched_target = matched_target_new
        prev_assignment = perm

    return best_rmsd, best_rot, best_trans