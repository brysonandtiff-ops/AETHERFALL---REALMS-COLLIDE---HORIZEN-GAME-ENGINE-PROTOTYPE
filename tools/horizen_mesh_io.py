"""Dependency-free geometry/STL and integrity helpers for the Blender handoff.

No Blender, Godot, or print-readiness certification is implied by these checks.
"""
from __future__ import annotations

import hashlib
import math
import re
import struct
from pathlib import Path

ASSET_ID = re.compile(r"^(?:CHR|WPN|PRP|LVL|ENV)_[A-Za-z][A-Za-z0-9_]{1,70}$")
MAX_TRIANGLES = 2_000_000
MAX_BINARY_STL_TRIANGLES = (64 * 1024 * 1024 - 84) // 50


def safe_asset_id(value: str) -> str:
    if not isinstance(value, str) or not ASSET_ID.fullmatch(value):
        raise ValueError("Asset ID must be CHR_/WPN_/PRP_/LVL_/ENV_ and use letters, digits or underscores")
    return value


def sha256_file(path: str | Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _checked(vertices, faces):
    if not vertices or not faces or len(faces) > MAX_TRIANGLES:
        raise ValueError("Expected 1 to 2,000,000 mesh triangles")
    positions = []
    for point in vertices:
        if len(point) != 3 or any(not math.isfinite(float(v)) for v in point):
            raise ValueError("Invalid or nonfinite mesh vertex")
        positions.append(tuple(float(v) for v in point))
    indexed = []
    for face in faces:
        if len(face) != 3 or any(type(i) is not int or i < 0 or i >= len(positions) for i in face):
            raise ValueError("Mesh triangles must reference three valid vertex indices")
        indexed.append(tuple(face))
    return positions, indexed


def audit_triangles(vertices, faces) -> dict:
    """Conservative indexed-edge count; manifold candidacy is not printable proof."""
    positions, indexed = _checked(vertices, faces)
    edges = {}
    degenerate = 0
    for a, b, c in indexed:
        va, vb, vc = positions[a], positions[b], positions[c]
        u = [vb[i] - va[i] for i in range(3)]
        v = [vc[i] - va[i] for i in range(3)]
        normal = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
        if len({a, b, c}) != 3 or math.sqrt(sum(q * q for q in normal)) < 1e-12:
            degenerate += 1
        for edge in ((a, b), (b, c), (c, a)):
            key = tuple(sorted(edge))
            edges[key] = edges.get(key, 0) + 1
    bounds = [[min(p[i] for p in positions), max(p[i] for p in positions)] for i in range(3)]
    boundary = sum(n == 1 for n in edges.values())
    non_manifold = sum(n > 2 for n in edges.values())
    return {
        "vertices": len(positions), "triangles": len(indexed),
        "boundary_edges": boundary, "overused_edges": non_manifold,
        "degenerate_triangles": degenerate, "axis_bounds_metres": bounds,
        "watertight_candidate": boundary == 0 and non_manifold == 0 and degenerate == 0,
        "assessment": "Indexed edge screen only; orientation, intersections, wall thickness and slicer validation NOT TESTED",
    }


def binary_stl(vertices, faces, *, millimetres_per_metre: float = 1000.0) -> bytes:
    """Write scaled triangles in binary STL (unitless format, output intended in mm)."""
    if len(faces) > MAX_BINARY_STL_TRIANGLES:
        raise ValueError("Binary STL would exceed the HORIZEN 64 MiB intake limit")
    positions, indexed = _checked(vertices, faces)
    scale = float(millimetres_per_metre)
    if not math.isfinite(scale) or scale <= 0 or scale > 1_000_000:
        raise ValueError("Invalid positive millimetre scale")
    data = bytearray(b"HORIZEN SCALE FROM METRES TO MM - UNVERIFIED PRINT QUALITY".ljust(80, b" "))
    data.extend(struct.pack("<I", len(indexed)))
    for ia, ib, ic in indexed:
        tri = [tuple(scale * c for c in positions[i]) for i in (ia, ib, ic)]
        u = [tri[1][i] - tri[0][i] for i in range(3)]
        v = [tri[2][i] - tri[0][i] for i in range(3)]
        n = (u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0])
        magnitude = math.sqrt(sum(q*q for q in n))
        normal = tuple(q / magnitude for q in n) if magnitude else (0., 0., 0.)
        values = (*normal, *tri[0], *tri[1], *tri[2])
        if any(not math.isfinite(q) or abs(q) > 3.0e38 for q in values):
            raise ValueError("Triangle outside binary STL float range")
        data.extend(struct.pack("<12fH", *values, 0))
    return bytes(data)
