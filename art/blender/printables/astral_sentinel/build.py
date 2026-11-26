"""Build the Astral Sentinel collectible in Blender 4.3.

blender -b -t 5 --python-exit-code 1 --python build.py -- --output /path/to/output
"""

import argparse
from hashlib import sha256
import json
from math import cos, pi, sin
from pathlib import Path
import sys
from zipfile import ZIP_DEFLATED, ZipFile
from xml.sax.saxutils import escape

import bmesh
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree


def material(name, rgb, metal, roughness, emission=0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*rgb, 1)
    mat.use_nodes = True
    principled = mat.node_tree.nodes.get("Principled BSDF")
    principled.inputs["Base Color"].default_value = (*rgb, 1)
    principled.inputs["Metallic"].default_value = metal
    principled.inputs["Roughness"].default_value = roughness
    principled.inputs["Emission Color"].default_value = (*rgb, 1)
    principled.inputs["Emission Strength"].default_value = emission
    return mat


class Sculpture:
    def __init__(self):
        self.parts = bpy.data.collections.new("Editable sculpture")
        bpy.context.scene.collection.children.link(self.parts)
        self.group = self.parts
        self.dark = material("Obsidian | undersuit", (.022, .019, .036), .36, .34)
        self.iron = material("Gunmetal | engraved steel", (.075, .080, .124), .68, .31)
        self.silver = material("Moonsteel | polished plate", (.61, .67, .78), .72, .24)
        self.gold = material("Electrum | raised trim", (.80, .43, .105), .73, .24)
        self.gold_dark = material("Bronze | recessed metal", (.25, .095, .039), .62, .33)
        self.blue = material("Aether | cyan crystal", (.012, .31, .82), .36, .22, .44)
        self.light = material("Aether | inner light", (.12, .56, 1.0), .28, .23, .78)
        self.violet = material("Mantle | midnight violet", (.078, .024, .16), .44, .34)
        self.purple = material("Mantle | amethyst", (.23, .074, .36), .50, .30)
        self.lavender = material("Mantle | polished ridges", (.29, .13, .52), .51, .32)
        self.stone = material("Plinth | basalt", (.035, .029, .059), .24, .50)
        self.stone_light = material("Plinth | raised carving", (.12, .084, .16), .48, .39)
        self.palette = [self.dark, self.iron, self.silver, self.gold, self.gold_dark,
                        self.blue, self.light, self.violet, self.purple, self.lavender,
                        self.stone, self.stone_light]

    def section(self, name):
        self.group = bpy.data.collections.new(name)
        self.parts.children.link(self.group)

    def object(self, name, mesh, mat, smooth=False):
        obj = bpy.data.objects.new(name, mesh)
        self.group.objects.link(obj)
        mesh.materials.append(mat)
        for face in mesh.polygons:
            face.use_smooth = smooth
        return obj

    def mesh(self, name, verts, faces, mat, smooth=False):
        mesh = bpy.data.meshes.new(name)
        mesh.from_pydata(verts, [], faces)
        mesh.update()
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        bm.to_mesh(mesh)
        bm.free()
        return self.object(name, mesh, mat, smooth)

    def rings(self, name, rings, mat, smooth=False):
        sides = len(rings[0])
        verts = [point for ring in rings for point in ring]
        faces = [tuple(reversed(range(sides)))]
        for row in range(len(rings) - 1):
            base = row * sides
            for col in range(sides):
                a = base + col
                b = base + (col + 1) % sides
                faces.append((a, b, b + sides, a + sides))
        faces.append(tuple(range(len(verts) - sides, len(verts))))
        return self.mesh(name, verts, faces, mat, smooth)

    def loft(self, name, sections, mat, sides=32, smooth=True):
        return self.rings(name, [
            [(x + rx * cos(2*pi*i/sides), y + ry * sin(2*pi*i/sides), z)
             for i in range(sides)]
            for z, x, y, rx, ry in sections
        ], mat, smooth)

    def ellipsoid(self, name, center, scales, mat, direction=None, detail=3):
        bm = bmesh.new()
        bmesh.ops.create_icosphere(bm, subdivisions=detail, radius=1)
        rotation = Vector(direction).to_track_quat("Z", "Y") if direction else None
        for vert in bm.verts:
            local = Vector(tuple(v * s for v, s in zip(vert.co, scales)))
            vert.co = (rotation @ local if rotation else local) + Vector(center)
        mesh = bpy.data.meshes.new(name)
        bm.to_mesh(mesh)
        bm.free()
        return self.object(name, mesh, mat, detail > 2)

    def limb(self, name, begin, end, width, depth, mat):
        begin, end = Vector(begin), Vector(end)
        direction = end - begin
        return self.ellipsoid(name, (begin + end)/2, (width, depth, direction.length/2 + 1.8),
                              mat, direction)

    def tube(self, name, controls, mat, sides=10):
        points = [Vector(item[0]) for item in controls]
        reference = Vector((0, 1, 0))
        rings = []
        for i, (point, (_, radius)) in enumerate(zip(points, controls)):
            tangent = (points[min(i+1, len(points)-1)] - points[max(i-1, 0)]).normalized()
            guide = Vector((0, 0, 1)) if abs(tangent.dot(reference)) > .92 else reference
            u = tangent.cross(guide).normalized()
            v = tangent.cross(u).normalized()
            rings.append([point + radius*(u*cos(2*pi*j/sides) + v*sin(2*pi*j/sides))
                          for j in range(sides)])
        return self.rings(name, rings, mat, True)

    def line(self, name, points, radius, mat):
        return self.tube(name, [(point, radius) for point in points], mat)

    def blade(self, name, controls, mat, normal=(0, -1, 0), edge=None):
        """A closed, cambered leaf with a forward ridge and a thick root."""
        points = [Vector(item[0]) for item in controls]
        normal = Vector(normal)
        section = [(0, 1), (.56, .52), (1, 0), (.64, -.48), (0, -.65),
                   (-.64, -.48), (-1, 0), (-.56, .52)]
        rings = []
        for i, (point, (_, span, height)) in enumerate(zip(points, controls)):
            tangent = (points[min(i+1, len(points)-1)] - points[max(i-1, 0)]).normalized()
            sideways = normal.cross(tangent).normalized()
            outward = tangent.cross(sideways).normalized()
            rings.append([point + sideways*(x*span) + outward*(y*height) for x, y in section])
        obj = self.rings(name, rings, mat)
        if edge:
            obj.data.materials.append(edge)
            for face in obj.data.polygons[1:-1]:
                if (face.index - 1) % 8 in (1, 6):
                    face.material_index = 1
        return obj

    def feather(self, name, controls, mat, edge, normal=(0, 1, 0)):
        """A curved feather with a raised rachis molded into the front surface."""
        controls = [(*position, width, relief) for position, width, relief in controls]
        path = []
        for i, (start, end) in enumerate(zip(controls, controls[1:])):
            before = controls[max(i-1, 0)]
            after = controls[min(i+2, len(controls)-1)]
            for t in (0, 1/3, 2/3):
                point = [.5*(2*a + (b-p)*t + (2*p-5*a+4*b-q)*t*t +
                             (3*a-p-3*b+q)*t*t*t)
                         for p, a, b, q in zip(before, start, end, after)]
                path.append((Vector(point[:3]), point[3], point[4]))
        last = controls[-1]
        path.append((Vector(last[:3]), last[3], last[4]))
        self.blade(name, path, mat, normal, edge)

        spine = []
        forward = Vector(normal)
        for i, (point, width, relief) in enumerate(path[1:-3], 1):
            tangent = (path[i+1][0] - path[i-1][0]).normalized()
            outward = tangent.cross(forward.cross(tangent).normalized())
            spine.append((point + outward*(relief-.11), min(.45, .20+width*.067)))
        self.tube(name+" raised rachis", spine, edge, sides=8)

    def plate(self, name, outline, crown, mat, trim=None, face=(0, -1, 0)):
        """Build a thick armor plate with a beveled outline and a raised crest."""
        outline = [Vector(p) for p in outline]
        center = sum(outline, Vector()) / len(outline)
        normal = Vector(face).normalized()
        front = [p.lerp(center, .14) + .44*normal for p in outline]
        back = [p - 1.5*normal for p in outline]
        count = len(outline)
        verts = back + outline + front + [Vector(crown)]
        faces = [tuple(reversed(range(count)))]
        for i in range(count):
            j = (i+1) % count
            faces.extend([(i, j, j+count, i+count),
                          (i+count, j+count, j+2*count, i+2*count),
                          (i+2*count, j+2*count, 3*count)])
        obj = self.mesh(name, verts, faces, mat)
        if trim:
            obj.data.materials.append(trim)
            for face in obj.data.polygons[1:]:
                if (face.index - 1) % 3 == 1:
                    face.material_index = 1
        return obj

    def bezel(self, name, center, radius, thickness, mat, normal=(0, -1, 0)):
        center = Vector(center)
        n = Vector(normal).normalized()
        guide = (0, 1, 0) if abs(n.z) > .92 else (0, 0, 1)
        u = n.cross(Vector(guide)).normalized()
        v = n.cross(u).normalized()
        rings = []
        for i in range(32):
            angle = 2*pi*i/32
            radial = u*cos(angle) + v*sin(angle)
            rings.append([center + radial*(radius+thickness*cos(2*pi*j/8))
                          + n*(thickness*sin(2*pi*j/8)) for j in range(8)])
        points = [p for row in rings for p in row]
        faces = [(i*8+j, i*8+(j+1)%8, ((i+1)%32)*8+(j+1)%8, ((i+1)%32)*8+j)
                 for i in range(32) for j in range(8)]
        return self.mesh(name, points, faces, mat, True)


def mirror(points, side):
    return [(side*x, y, z) for x, y, z in points]


def mirrored_blade(controls, side):
    return [((side*x, y, z), span, height) for (x, y, z), span, height in controls]


def build_base(s):
    s.section("01   Eclipse plinth")
    s.loft("Turned basalt plinth", [
        (0, 0, 0, 30.5, 30.5), (.65, 0, 0, 31.5, 31.5),
        (2.1, 0, 0, 31.5, 31.5), (3.3, 0, 0, 30.2, 30.2),
        (5.9, 0, 0, 29.0, 29.0), (6.8, 0, 0, 30.0, 30.0),
        (7.7, 0, 0, 30.0, 30.0), (8.7, 0, 0, 28.7, 28.7),
        (9.0, 0, 0, 27.7, 27.7)], s.stone, sides=128)
    for z, r, w, mat in [(2.47, 31.15, .46, s.gold_dark), (6.35, 29.56, .47, s.gold),
                         (7.86, 29.58, .42, s.iron)]:
        s.loft("Turned inset band", [(z-.34, 0, 0, r-w-.55, r-w-.55),
               (z-.20, 0, 0, r+w*.4, r+w*.4), (z+.20, 0, 0, r+w*.4, r+w*.4),
               (z+.34, 0, 0, r-w-.55, r-w-.55)], mat, sides=128)
    s.bezel("Outer plinth inlay", (0, 0, 8.97), 25.9, .49, s.gold_dark, (0, 0, 1))
    s.bezel("Inner plinth inlay", (0, 0, 8.95), 24.1, .35, s.stone_light, (0, 0, 1))
    # The front panel is a raised eclipse icon. Repeating runes curve around the plinth.
    for i in range(16):
        a = i*pi/8 - pi/2
        radial = Vector((cos(a), sin(a), 0))
        tangent = Vector((-sin(a), cos(a), 0))

        def relief(u, z, rise=.4):
            r = 31.18 - (z-2.45)*.60 + rise
            return tuple(radial*r + tangent*u + Vector((0, 0, z)))

        if i == 0:
            crest = [relief(-3.3, 4.3), relief(0, 6.25),
                     relief(3.3, 4.3), relief(0, 2.65)]
            s.plate("Plinth eclipse medallion", crest, relief(0, 4.3, 1.35),
                    s.gold_dark, s.gold, radial)
            s.ellipsoid("Plinth aether cabochon", relief(0, 4.3, 1.13),
                        (1.02, .85, 1.05), s.blue, detail=2)
        else:
            s.line("Raised plinth rune", [relief(-1.7, 3.2), relief(0, 5.38),
                                         relief(1.65, 3.2)], .50, s.stone_light)
            s.line("Rune stem", [relief(0, 3.13), relief(0, 5.36)], .45, s.gold_dark)

    # Damaged radial masonry and intact engraved spokes on the eclipse disc.
    for i in range(12):
        a = i*2*pi/12 + .09
        r = 19.2 + 1.65*cos(i*1.94)
        radial = Vector((cos(a), sin(a), 0))
        tangent = Vector((-sin(a), cos(a), 0))
        if i in (2, 3, 4, 5, 6, 8, 10):
            width = 2.4 + .9*sin(i*1.7)**2
            rise = 1.25 + .65*cos(i*2.23)**2
            outline = [radial*(r+u) + tangent*v + Vector((0, 0, z)) for u, v, z in [
                (-2.45, -width, 9.1), (.8, -width-.5, 9.25), (2.65, -width*.23, 9.2),
                (2.45, width*.71, 9.15), (.15, width, 9.14), (-1.6, width*.61, 9.2)]]
            apex = radial*(r-.42) + tangent*(width*.3) + Vector((0, 0, 9.4+rise))
            s.plate("Fractured altar flagstone", outline, apex, s.stone_light,
                    face=(0, 0, 1))
        else:
            detail = [radial*r0 + tangent*u + Vector((0, 0, 9.08))
                      for r0, u in [(15.2, 0), (19.2, -.65), (22.7, 0), (19.2, .65), (15.2, 0)]]
            s.line("Raised radial eclipse engraving", detail, .32, s.gold_dark)


def build_body(s):
    s.section("02   Body and articulated undersuit")
    s.loft("Pelvis and torso", [
        (45, 0, 0, 2.6, 3.5), (48, 0, .2, 9, 5.6), (53, -.3, .45, 11.2, 6.5),
        (59, -.35, .8, 9.4, 5.6), (65, -.25, .65, 10.4, 6.5),
        (71, 0, .7, 13.1, 7.7), (77, .2, .8, 15.1, 8.05),
        (82, .3, 1, 15.65, 7.3), (85.5, .4, .35, 9.6, 5.6),
        (88.2, .55, -.25, 5.5, 4.7)], s.dark)
    s.loft("Armored neck", [(83, .5, 0, 6.4, 5.4), (86.7, .6, 0, 6.6, 5.2),
                          (89.4, .7, -.5, 4.9, 4.8), (94, .8, -.8, 4.6, 4.15)], s.iron)
    legs = [(-1, (-6, -.5, 53), (-10.1, -3.7, 33), (-11.1, -3.9, 13.4)),
            (1, (6.4, 1.5, 53), (9.6, 2.65, 33.1), (12.0, 3.9, 13.45))]
    for side, hip, knee, ankle in legs:
        s.limb("Cuisses undersuit", hip, knee, 5.45, 5.18, s.dark)
        s.ellipsoid("Knee joint", knee, (4.6, 4.55, 4.7), s.iron)
        s.limb("Greave undersuit", knee, ankle, 4.25, 4.0, s.dark)
        x, y, _ = ankle
        s.loft("Sabatons", [(8.1, x, y-2.25, 3.3, 5.85),
                          (9.6, x, y-2.6, 4.1, 6.85), (11.4, x, y-2.65, 4.1, 6.8),
                          (13.5, x, y-1.15, 3.8, 5.05), (16.6, x, y-.1, 3.55, 3.4)],
               s.iron)
    arms = [((-13.9, .2, 81), (-19.35, -.1, 69), (-21.4, -2.85, 58.6)),
            ((14.25, .8, 81.2), (21.15, 1.6, 68.35), (23.25, -10.5, 70.45))]
    for shoulder, elbow, wrist in arms:
        s.ellipsoid("Shoulder articulation", shoulder, (5.6, 5.65, 5.65), s.dark)
        s.limb("Upper arm undersuit", shoulder, elbow, 3.95, 4.15, s.dark)
        s.ellipsoid("Elbow", elbow, (3.55, 3.5, 3.65), s.iron)
        s.limb("Forearm undersuit", elbow, wrist, 3.4, 3.55, s.dark)
    return legs, arms


def build_mantle(s):
    s.section("03   Raptor mantle")
    # A sculpted wrap beneath the feathers. The hem rests on the rear plinth.
    rings = []
    for j, (z, width, spine, sweep, drape) in enumerate([
        (8.5, 15, 16.4, 8.3, 5), (14, 21.7, 18.5, 10.7, 5),
        (25, 24.5, 17.6, 11.6, 3), (41, 20.5, 14.5, 10.2, 2),
        (59, 17.3, 11.3, 8.4, 1.5), (73, 16.8, 8.4, 6.2, .8),
        (82, 15.8, 6.7, 6, .5), (85, 8.5, 4.3, 3.2, .5)]):
        front = []
        back = []
        for i in range(29):
            u = i/14 - 1
            x = width*u
            y = spine - sweep*abs(u)**2.7 + .62*cos(5*pi*u + .47*j)
            height = z + drape*abs(u)**1.6
            if j == 0:
                height += .85*(1-cos(6*pi*u))
            front.append((x, y-1.92, height))
            back.append((x, y+.7, height))
        rings.append(back + list(reversed(front)))
    s.rings("Structural mantle lining", rings, s.violet, True)

    for side in (-1, 1):
        for row, (anchor_z, root_y, tip_y, width) in enumerate([
            (82.4, 5.05, 10.8, 3.2), (72.4, 8.2, 14.8, 3.45),
            (57.5, 11.0, 17.2, 3.8), (41.0, 13.6, 19.7, 4.25),
            (27.3, 16.2, 20.9, 3.8)]):
            for j in range(5):
                u = (j+.35)/5
                x0 = 2.0 + j*(2.6 + row*.36)
                wave = sin(j*1.3 + row*.82 + side*.57)
                stagger = .9*sin(row*2.0 + j*1.8 + side*.7)
                x1 = x0 + 2.0 + j*(.48 + row*.045) + .95*wave
                y0 = root_y - 6.2*u**2.25
                y1 = tip_y - 11.3*u**2.5 + 1.35*wave
                z0 = anchor_z - j*(.35 + row*.21) + stagger
                z1 = max(9.35, z0 - (13.2 + row*1.8 + j*.85 + 2.4*wave))
                if row == 4:
                    z1 += 1.5*abs(j-2)
                feather = [((x0, y0, z0), width*.53, 1.3),
                           ((x0+1.15, y0+1.3, z0-3.3), width*(.90+.09*wave), 2.15),
                           ((x0*.48+x1*.52+.48*wave, y0*.50+y1*.50+1.25,
                             z0*.52+z1*.48), width*.76, 1.85),
                           ((x1-.6, y1+.30, z1+3.8), width*.38, 1.05),
                           ((x1, y1, z1), .36, .41)]
                s.feather("Overlapping mantle feather", mirrored_blade(feather, side),
                          s.purple if (j+row) % 3 else s.violet,
                          s.lavender if row < 4 else s.purple)
        for i in range(4):
            x = 9.5 + i*3.3
            mantle_edge = [((x, 3.95, 79.0-i*2), 2.5, 1.45),
                           ((x+1.9, 2.65+i*.41, 74.2-i*2.1), 2.8, 2.05),
                           ((x+4.8, 3.6+i*.8, 66.4-i*3.4), 1.45, 1.35),
                           ((x+5.9, 5.2+i*.87, 61.7-i*3.85), .43, .47)]
            if i == 3:
                mantle_edge[2] = ((24.3, 8.2, 55.8), 1.55, 1.4)
                mantle_edge[3] = ((25.0, 8.9, 52.7), .54, .62)
            s.feather("Overhanging mantle feather", mirrored_blade(mantle_edge, side),
                      s.purple, s.lavender, normal=(0, -1, 0))
        for index, (x_tip, y_tip, z_tip) in enumerate(
                [(25, 6.5, 20), (29, 8.9, 16), (30.4, 12.7, 24)] if side < 0
                else [(26.5, 6.3, 16.2), (30.8, 8.7, 17.5), (33, 12, 27.3)]):
            root = 15.1 + index*1.9
            tail = [((root, 5.9+index*.65, 58.4-index*2.9), 2.4, 1.4),
                    ((root+2, 6.4+index*.6, 52.0-index*2), 2.9, 2.0),
                    ((root+4.4, 7.2+index*.72, 40.3-index), 3.2, 1.9),
                    ((x_tip-2.3, y_tip-.35, z_tip+8.0), 1.7, 1.52),
                    ((x_tip, y_tip, z_tip), .48, .52)]
            s.feather("Swept mantle hem", mirrored_blade(tail, side),
                      s.purple if index != 1 else s.violet, s.lavender,
                      normal=(side*.34, -.94, 0))
    s.blade("Mantle spine ridge", [((0, 7, 82), 1.8, 1.7), ((0, 11, 65), 2.5, 1.8),
            ((0, 16, 39), 2, 1.8), ((0, 20.4, 21), 1.4, 1.4), ((0, 21.1, 12), .4, .5)],
            s.violet, normal=(0, 1, 0), edge=s.gold_dark)


def build_chest(s):
    s.section("04   Cuirass and pauldrons")
    for row in range(3):
        z = 86 + 1.82*row
        s.plate("Overlapping gorget", [(-3.3, -4.1, z+.95), (0, -4.75, z+.49),
                (3.9, -3.94, z+.95), (2.55, -4.42, z-.73), (0, -4.93, z-1.2),
                (-2.06, -4.55, z-.68)], (0, -5.33, z-.18),
                s.iron if row != 1 else s.silver, s.gold_dark)
    for side in (-1, 1):
        def plate(name, outline, crown, color, trim=s.gold, normal=(0, -1, 0)):
            return s.plate(name, mirror(outline, side), mirror([crown], side)[0],
                           color, trim, (side*normal[0], normal[1], normal[2]))

        plate("Collar fin", [(2, -4.1, 85.4), (5.4, -4.7, 92.2),
                            (8.2, -2.2, 91.0), (9.2, -3.8, 84.2), (5, -5.3, 80.7)],
              (6.4, -6.4, 87.5), s.iron)
        plate("Swept breastplate", [(1.3, -6.9, 80.5), (8.5, -6.75, 84.5),
                                    (14.9, -5.15, 84.1), (13.0, -6.65, 78.3),
                                    (9.1, -7.8, 72.4), (5.4, -8.75, 71),
                                    (2.2, -8.05, 75.3)],
              (8.2, -10.0, 78.9), s.silver)
        plate("Breastplate lower sweep", [(2.5, -7.6, 72.5), (8.4, -6.95, 73.5),
                                          (12.75, -5.4, 76.2), (11.5, -5.15, 69.7),
                                          (6.15, -7, 64.7), (4.7, -7.3, 68.2)],
              (7.6, -8.3, 69.8), s.iron)
        s.blade("Breastplate starburst relief", mirrored_blade([
            ((3.1, -10.07, 76.0), .68, .65),
            ((6.4, -10.02, 77.6), .88, .66),
            ((8.45, -9.91, 78.88), .9, .56),
            ((10.62, -8.81, 80.16), .43, .45),
            ((12.63, -7.34, 81.47), .36, .39)], side), s.gold)
        s.blade("Secondary chest engraving", mirrored_blade([
            ((4.95, -9.61, 74.65), .39, .47),
            ((7.6, -9.46, 75.0), .55, .55),
            ((9.65, -8.97, 75.94), .43, .47),
            ((10.97, -7.75, 77.05), .33, .37)], side), s.gold_dark)
        for i in range(3):
            z = 65.5 - i*3.9
            plate("Overlapping abdominal lame",
                  [(1, -5.9, z+1.9), (7.85-i*.32, -3.9, z+4.2),
                   (9.1-i*.44, -3.1, z+1.45), (5, -5.2, z-1.45), (1.5, -6.1, z-2.2)],
                  (4.4, -6.4, z+.7), s.iron, s.gold_dark)
        plate("Pauldron underlayer", [(9.8, -3.2, 85.0), (16.9, -3.9, 88.0),
                                     (24.6, -1.3, 88.1), (22.1, -3.0, 81.5),
                                     (18.8, -5.1, 77.3), (13.4, -5.55, 79.9)],
              (17.95, -5.9, 84.15), s.iron)
        plate("Crowned pauldron", [(10.5, -2.9, 85.6), (15.5, -1.7, 89.05),
                                  (22.9, -.65, 90.15), (27.2, 1.4, 91.5),
                                  (24.3, 1.6, 86.05), (20.7, -1.2, 83.55),
                                  (16.4, -4.85, 82.65)],
              (19.9, -4.05, 88.65), s.silver, s.gold, (.14, -.73, .67))
        plate("Overlapping pauldron blade", [(15.2, -4.47, 85.15), (19.95, -4.18, 88.28),
                 (24.2, -2.22, 87.7), (22.8, -4.15, 83.53), (22.41, -3.72, 79.33),
                 (19.28, -5.57, 80.97)],
              (20.05, -6.12, 84.23), s.iron, s.gold)
        plate("Rear pauldron feather socket", [(12.5, 3.8, 84.8), (18, 4.6, 90.1),
                                               (25, 5.9, 89.3), (23.2, 6.35, 84.3),
                                               (18.0, 7.15, 79.5)],
              (19.6, 8.4, 85.9), s.iron, s.gold, (.16, .92, .36))
        for i in range(2):
            plume = [((15.7+i*3.7, 3.7+i*1.3, 86.2-i*1.4), 2.7, 1.45),
                     ((17.5+i*3.8, 4.3+i*1.3, 88.15-i*1.6), 3.1, 1.7),
                     ((20.5+i*3.2, 6.3+i*1.2, 91.1-i*2.05), 1.5, 1.05),
                     ((22.4+i*3.05, 8.25+i*.8, 92.85-i*2.25), .39, .52)]
            s.blade("Swept shoulder feather", mirrored_blade(plume, side), s.purple,
                    normal=(0, -.3, .95), edge=s.gold_dark)
        s.line("Inlaid chest channel", mirror([(3.4, -7.85, 82), (6.7, -8.1, 83.3),
                (9.75, -7.55, 84.0)], side), .53, s.blue)
        # The long articulated hip plates follow the stance and lap into the undersuit.
        for i in range(3):
            z = 55.4 - i*2.2
            x = 5.45 + i*2.4
            plate("Hanging tasset", [(x-2.2, -5.25+i*.82, z+2.1),
                                    (x+3.4, -3.5+i*1.0, z+3),
                                    (x+5.0, -3.0+i*1.17, z-4.8),
                                    (x+4.15, -4.1+i*1.04, z-13.25),
                                    (x-.5, -5.45+i*.82, z-9.3),
                                    (x-1.8, -6.1+i*.68, z-4.4)],
                  (x+1.75, -7.3+i*.86, z-4.2), s.silver if i != 1 else s.iron)
    s.plate("Waist buckle shield", [(-4.6, -5.45, 56.6), (0, -6.15, 58.4),
                         (4.5, -5.5, 56.55), (3, -6.15, 52.6), (0, -6.7, 49),
                         (-3, -5.9, 52.5)], (0, -8.0, 54), s.gold_dark, s.gold)
    for z in (62.15, 66.25):
        s.plate("Central abdominal keel", [(-2.24, -5.69, z+1.55), (0, -6.3, z+2.52),
                (2.24, -5.69, z+1.56), (1.18, -6.38, z-.72),
                (0, -6.57, z-1.9), (-1.18, -6.38, z-.73)],
                (0, -7.31, z+.45), s.iron, s.gold_dark)
    s.ellipsoid("Buckle crystal", (0, -7.65, 54.4), (1.08, .97, 1.65), s.blue, detail=2)
    s.ellipsoid("Chest core housing", (0, -7.9, 77.1), (4.55, 2.85, 4.55), s.gold_dark)
    s.bezel("Chest core electrum bezel", (0, -9.8, 77.1), 3.25, .74, s.gold)
    s.ellipsoid("Chest core", (0, -9.75, 77.1), (2.9, 1.68, 2.9), s.blue, detail=2)
    s.ellipsoid("Chest core inner detail", (0, -11.0, 77.1), (1.4, .62, 1.4), s.light, detail=2)
    for i in range(8):
        a = pi*(i+.5)/4
        s.ellipsoid("Chest bezel rivet", (3.48*cos(a), -10.04, 77.1+3.48*sin(a)),
                    (.48, .47, .48), s.gold, detail=2)
    for a in (0, pi/2, pi, 3*pi/2):
        dx, dz = cos(a), sin(a)
        s.blade("Eclipse bezel ray", [((2.42*dx, -10.04, 77.1+2.42*dz), .58, .59),
                ((3.35*dx, -9.55, 77.1+3.35*dz), 1.05, .94),
                ((5.55*dx, -7.27, 77.1+5.55*dz), .39, .53)], s.gold)


def build_limbs(s, legs, arms):
    s.section("05   Limb armor and gauntlets")
    for side, hip, knee, ankle in legs:
        x, y, z = knee

        def knee_points(points):
            return [(x+side*u, y+v, z+w) for u, v, w in points]

        s.plate("Winged poleyn", knee_points([(-3.85, -3.25, 2.4), (-1.2, -4.2, 4.4),
                    (1.0, -4.0, 6.35), (4.75, -2.95, 4.45), (4.1, -3.9, -.4),
                    (1.05, -5.1, -4.05), (-2.65, -4.45, -2.55)]),
                knee_points([(1.15, -6.1, .9)])[0], s.silver, s.gold)
        s.plate("Knee crest relief", knee_points([(-1.35, -5.31, 1.35),
                (1.12, -5.36, 3.8), (3.0, -4.91, 1.42), (1.22, -5.67, -1.44)]),
                knee_points([(1.22, -6.42, 1.26)])[0], s.gold_dark, s.gold)
        s.ellipsoid("Knee crest crystal", knee_points([(1.18, -6.17, 1.37)])[0],
                    (.70, .45, .94), s.blue, detail=2)
        ax, ay, _ = ankle

        def shin_points(points):
            return [(ax+side*u, ay+v, 15+w) for u, v, w in points]

        s.plate("Gilded shin crest", shin_points([(-3.45, -3.2, 10.9),
                (-.8, -4.1, 13.2), (2.95, -3.6, 12), (3.9, -2.1, 14.5),
                (3.45, -3.15, 5.3), (1.25, -4.75, -1.08), (-2.3, -3.9, 2.8)]),
                shin_points([(.8, -5.75, 6.65)])[0], s.silver, s.gold)
        s.line("Raised greave filigree", shin_points([(-1.70, -4.17, 10.55),
                (.25, -5.07, 8.8), (1.85, -5.02, 9.49)]), .44, s.gold_dark)
        s.line("Greave aether channel", shin_points([(-2.7, -3.2, 10.2),
               (-3.34, -2.57, 7.3), (-2.82, -3.1, 4.2), (-2.15, -3.8, 2.2)]),
               .65, s.blue)
        s.plate("Winged instep", shin_points([(-3.1, -4, .8), (0, -4.35, 2.6),
                 (3.5, -2.85, 2.55), (4.05, -4.85, -2.95), (2.75, -8.05, -4.25),
                 (-3.1, -8.25, -4.03), (-3.7, -6.1, -2.8)]),
                shin_points([(.55, -6.15, -.89)])[0], s.silver, s.gold)
        for row in range(2):
            y0 = ay-4.6-row*1.75
            s.line("Articulated toe trim",
                   [(ax-3.3, y0, 11.53-row*.47), (ax, y0-.42, 13.36-row*.85),
                    (ax+3.19, y0-.04, 11.53-row*.47)], .46, s.gold_dark)
        xh, yh, zh = hip
        s.blade("Outer thigh rail", [((xh+side*3.2, yh-3, zh-2), 2.45, 1.45),
                ((xh+side*5.65, yh-3.15, zh-8), 2.25, 1.4),
                ((x+side*3, y-3, z+5), 1.55, 1.28),
                ((x+side*3.7, y-1.6, z+1.5), .49, .57)], s.iron, edge=s.gold)

    for index, (shoulder, elbow, wrist) in enumerate(arms):
        side = -1 if index == 0 else 1
        xs, ys, zs = shoulder
        xe, ye, ze = elbow
        xw, yw, zw = wrist
        s.blade("Upper arm armor fin", [((xs+side*1.0, ys-2.65, zs-.15), 2.65, 1.85),
                ((xs+side*3.5, ys-3.6, zs-3.6), 3.5, 2.15),
                ((xe-side*.4, ye-3.6, ze+2.9), 2.3, 1.75),
                ((xe-side*.75, ye-3.65, ze+.6), .62, .7)], s.silver, edge=s.gold)
        s.blade("Upper arm aether ridge", [((xs+side*3.7, ys-3.8, zs-3), .67, .65),
                ((xs+side*3.9, ys-3.8, zs-5.8), .86, .67),
                ((xe+side*.9, ye-3.39, ze+3.75), .57, .64),
                ((xe+side*1, ye-3.36, ze+2.08), .41, .48)], s.blue)
        if index == 0:
            s.plate("Falling vambrace", [(-17.4, -2.58, 66.45), (-21.7, -2.7, 68.9),
                    (-24.75, -1.6, 68.3), (-24.75, -4.28, 61.65), (-22, -5.9, 57.0),
                    (-18.5, -5.24, 59.45), (-17.25, -3.75, 63.9)],
                    (-21.6, -6.2, 64.1), s.silver, s.gold)
            s.ellipsoid("Closed left grip", (-21.6, -3.25, 55.0), (2.92, 2.8, 3.95), s.iron)
            for j in range(3):
                s.line("Left finger ridges", [(-23.5+j*1.18, -5.04, 55.47),
                       (-23.2+j*1.12, -5.4, 53.32), (-22.63+j*.98, -4.95, 52.15)],
                       .52, s.gold)
            s.ellipsoid("Left thumb", (-19.46, -4.0, 55.34), (1.18, 1.38, 2.26),
                        s.dark, (-.2, .2, 1))
        else:
            s.plate("Raised vambrace", [(20.2, .1, 71.5), (24.38, 1.32, 71.5),
                    (25.3, -3.85, 71.55), (25.05, -10.05, 73.45),
                    (22.45, -12.3, 72.55), (20.9, -7.9, 72.75), (20.3, -3.1, 72.3)],
                    (23.25, -5.65, 74.4), s.silver, s.gold, (.27, -.15, 1))
            s.ellipsoid("Raised grip", (23.8, -13.1, 71.65), (2.75, 3.15, 2.35), s.iron)
            for j in range(3):
                x = 22+j*1.52
                s.line("Orb-cradling fingers", [(x, -14.05, 71.08), (x, -15.45, 71.95),
                       (x, -15.34, 73.69), (x-.14, -14.75, 74.45)], .68, s.gold)
            s.ellipsoid("Raised thumb", (21.47, -12.78, 73.14), (1.34, 1.28, 1.8), s.dark)
            s.ellipsoid("Orb mounting clasp", (23.75, -13.47, 73.4), (2.94, 2.54, 1.81),
                        s.gold_dark)
            focus = s.loft("Six-cut aether prism", [(72.7, 23.75, -13.54, .7, .7),
                (75.52, 23.75, -13.54, 3.7, 3.45), (78.21, 23.05, -13.54, 3.38, 3.18),
                (81.55, 22.52, -13.47, .43, .43)], s.blue, sides=6, smooth=False)
            focus.data.materials.append(s.light)
            for face_index in (4, 10, 11, 17):
                focus.data.polygons[face_index].material_index = 1
            for tooth in range(3):
                angle = -pi*.48 + tooth*2*pi/3
                dx, dy = cos(angle), sin(angle)
                s.tube("Electrum setting prong", [
                    ((23.7+1.97*dx, -13.54+1.97*dy, 73.24), .73),
                    ((23.6+3.05*dx, -13.54+3.02*dy, 75.40), .66),
                    ((23.4+3.61*dx, -13.54+3.44*dy, 76.68), .58),
                    ((23.1+3.01*dx, -13.54+2.90*dy, 78.13), .37)], s.gold)


def build_helmet(s):
    s.section("06   Visored helm and crest")
    s.loft("Closed elven helmet core", [(90.25, .6, -.35, 3.38, 3.36),
            (92.3, .72, -.75, 4.17, 4.55), (96.4, .75, -.9, 5.81, 5.25),
            (101.2, .9, -.55, 6.14, 5.15), (105, .96, .0, 5.9, 4.78),
            (108, 1.02, .55, 4.5, 3.8), (110, 1.05, .9, 2.85, 2.75),
            (110.9, 1.08, 1.15, 1.4, 1.5)], s.iron)
    for side in (-1, 1):
        def helm(points):
            return [(.77+side*x, y, z) for x, y, z in points]

        s.plate("Split helmet brow", helm([(0, -5.5, 105.75), (2.6, -5.1, 108.15),
                (5.4, -3.2, 107.85), (6.45, -.95, 105.28), (5.82, -3.25, 101.99),
                (3.4, -5.35, 101.65), (.35, -6.12, 100.6)]),
                helm([(2.87, -6.27, 104.65)])[0], s.silver, s.gold)
        s.plate("Swept cheek armor", helm([(.3, -5.85, 99.05), (3.7, -4.95, 99.8),
                (6.15, -2.35, 100.8), (5.35, -2.4, 95.7), (2.45, -4.75, 92.95),
                (.28, -5.47, 92.35)]),
                helm([(2.83, -6.3, 96.3)])[0], s.silver, s.gold)
        s.line("Visor slit", helm([(.67, -6.10, 99.96), (2.35, -5.91, 100.14),
                (4.2, -5.09, 100.57), (5.61, -3.74, 101.12)]), .62, s.blue)
        s.line("Creased edge beneath visor", helm([(1.55, -6.24, 99.12), (2.9, -5.92, 99.39),
                (4.25, -4.82, 99.92), (5.64, -3.11, 100.52)]), .40, s.gold)
        s.plate("Temple fin", helm([(4.75, .34, 102.35), (6.25, .95, 107.1),
                (8.5, 4.15, 110.0), (7.95, 4.43, 105.34), (6.0, 3.8, 100.7),
                (4.95, 1.65, 97.4)]),
                helm([(6.62, 2.15, 103.56)])[0], s.iron, s.gold, (side*.7, -.65, 0))
        s.blade("Cheek fluting", [(p, width, h) for p, width, h in zip(
            helm([(3.75, -4.81, 98.95), (3.37, -5.84, 97.18),
                  (2.68, -6.24, 95.93), (1.81, -5.95, 94.44)]),
            (.45, .61, .51, .34), (.44, .53, .48, .37))], s.gold_dark)
    s.plate("Layered nape guard", [(-4.35, 3.64, 104), (.75, 5.19, 106.6),
            (5.8, 3.86, 104.2), (5.17, 4.30, 98.4), (3.53, 3.67, 92.35),
            (.82, 4.19, 90.7), (-2.19, 3.68, 92.85), (-4.02, 4.12, 98.56)],
            (.79, 6.1, 100.9), s.iron, s.gold_dark, (0, 1, 0))
    s.blade("Nape crest spine", [((.87, 5.4, 107.1), .55, .75),
            ((.88, 5.82, 104.3), 1.16, 1.1), ((.86, 5.97, 101.4), 1.3, 1),
            ((.86, 5.25, 97.67), .78, .82), ((.86, 4.8, 94.7), .41, .56)],
            s.silver, normal=(0, 1, 0), edge=s.gold)
    s.blade("Helm nose guard", [((.78, -5.75, 105.4), 1.05, .83),
            ((.78, -6.17, 102.1), 1.35, 1.05), ((.78, -6.05, 98.1), .82, .85),
            ((.78, -5.72, 94.2), .55, .72)], s.gold_dark, edge=s.gold)
    s.ellipsoid("Brow jewel", (.79, -6.15, 104.27), (1.0, .97, 1.68), s.blue, detail=2)
    s.blade("Swept central crown", [((.8, -4.12, 105.6), 1.99, 1.47),
            ((.8, -2.75, 109.1), 2.84, 1.73), ((1.05, .15, 112.75), 2.88, 1.85),
            ((1.8, 4.25, 115.72), 2.26, 1.56), ((2.35, 8.1, 118.35), 1.17, 1.0),
            ((2.85, 11.1, 118.7), .49, .47)], s.silver, normal=(0, -.7, .7), edge=s.gold)
    for side in (-1, 1):
        for i in range(3):
            plume = [((1.6+i*1.17, 2.35-i*.82, 108.4-i*.71), 1.48, 1.3),
                     ((2.8+i*1.18, 4.15-i*.35, 110.6-i*1.04), 1.8, 1.55),
                     ((4.5+i*1.18, 7.2, 113.4-i*1.39), 1.36, 1.14),
                     ((5.25+i*1.56, 10.85-i*.3, 115.3-i*1.7), .46, .51)]
            s.blade("Crown feather", mirrored_blade(plume, side), s.purple,
                    normal=(0, -.45, .89), edge=s.lavender)


def select_only(obj):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def source_surface(parts, palette):
    vertices, triangles, colors = [], [], []
    color_index = {mat: i for i, mat in enumerate(palette)}
    for obj in parts:
        mesh = obj.data
        mesh.calc_loop_triangles()
        offset = len(vertices)
        vertices.extend(v.co.copy() for v in mesh.vertices)
        triangles.extend(tuple(offset+i for i in tri.vertices) for tri in mesh.loop_triangles)
        colors.extend(color_index[mesh.materials[tri.material_index]] for tri in mesh.loop_triangles)
    return BVHTree.FromPolygons(vertices, triangles, all_triangles=True), colors


def components(bm):
    remaining = set(bm.verts)
    groups = []
    while remaining:
        queue = [remaining.pop()]
        group = queue.copy()
        while queue:
            vertex = queue.pop()
            for edge in vertex.link_edges:
                neighbor = edge.other_vert(vertex)
                if neighbor in remaining:
                    remaining.remove(neighbor)
                    group.append(neighbor)
                    queue.append(neighbor)
        groups.append(group)
    return sorted(groups, key=len, reverse=True)


def build_print(s):
    parts = list(s.parts.all_objects)
    surface, colors = source_surface(parts, s.palette)
    print_collection = bpy.data.collections.new("Print-ready mesh")
    bpy.context.scene.collection.children.link(print_collection)
    copies = []
    for part in parts:
        copy = part.copy()
        copy.data = part.data.copy()
        print_collection.objects.link(copy)
        copies.append(copy)
    select_only(copies[0])
    for copy in copies:
        copy.select_set(True)
    bpy.ops.object.join()
    obj = bpy.context.object
    obj.name = "Astral Sentinel • fused print"
    obj.data.remesh_voxel_size = .24
    obj.data.use_remesh_preserve_attributes = False
    obj.data.use_remesh_preserve_volume = True
    bpy.ops.object.voxel_remesh()

    bm = bmesh.new()
    bm.from_mesh(obj.data)
    groups = components(bm)
    discarded = [len(group) for group in groups[1:]]
    print("Remesh component vertex counts:", [len(group) for group in groups], flush=True)
    bmesh.ops.delete(bm, geom=[v for group in groups[1:] for v in group], context="VERTS")
    bm.to_mesh(obj.data)
    bm.free()

    smooth = obj.modifiers.new("Remove voxel stair-stepping", "SMOOTH")
    smooth.factor = .55
    smooth.iterations = 3
    bpy.ops.object.modifier_apply(modifier=smooth.name)
    decimate = obj.modifiers.new("Reduce redundant triangles", "DECIMATE")
    decimate.ratio = .155
    decimate.use_collapse_triangulate = True
    bpy.ops.object.modifier_apply(modifier=decimate.name)
    triangulate = obj.modifiers.new("Triangulate export", "TRIANGULATE")
    bpy.ops.object.modifier_apply(modifier=triangulate.name)

    # A single planar face at the bottom prevents a floating first layer.
    for vertex in obj.data.vertices:
        if vertex.co.z < .24:
            vertex.co.z = 0
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=.0001)
    bmesh.ops.dissolve_degenerate(bm, edges=list(bm.edges), dist=.0001)
    bmesh.ops.triangulate(bm, faces=list(bm.faces))
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(obj.data)
    bm.free()

    obj.data.materials.clear()
    for mat in s.palette:
        obj.data.materials.append(mat)
    obj.data.update()
    for face in obj.data.polygons:
        # Cast inward to find the visible original surface where sculpt parts overlap.
        center, normal = face.center, face.normal
        _, _, index, _ = surface.ray_cast(center + normal*.75, -normal, 1.45)
        if index is None:
            _, _, index, _ = surface.find_nearest(center)
        face.material_index = colors[index] if index is not None else 0
        face.use_smooth = True

    s.parts.hide_render = True
    s.parts.hide_viewport = True
    bpy.context.view_layer.update()
    return obj, discarded


def inspection(mesh):
    bm = bmesh.new()
    bm.from_mesh(mesh)
    low = [min(v.co[i] for v in bm.verts) for i in range(3)]
    high = [max(v.co[i] for v in bm.verts) for i in range(3)]
    result = {
        "vertices": len(bm.verts),
        "triangles": len(bm.faces),
        "non_triangles": sum(len(f.verts) != 3 for f in bm.faces),
        "connected_components": len(components(bm)),
        "non_manifold_edges": sum(not e.is_manifold for e in bm.edges),
        "non_manifold_vertices": sum(not v.is_manifold for v in bm.verts),
        "inconsistent_edges": sum(not e.is_contiguous for e in bm.edges),
        "degenerate_faces": sum(f.calc_area() < 1e-8 for f in bm.faces),
        "volume_mm3": round(bm.calc_volume(signed=True), 3),
        "dimensions_mm": [round(b-a, 3) for a, b in zip(low, high)],
        "min_z_mm": round(low[2], 5),
    }
    bm.free()
    assert result["connected_components"] == 1, result
    for field in ("non_triangles", "non_manifold_edges", "non_manifold_vertices",
                  "inconsistent_edges", "degenerate_faces", "min_z_mm"):
        assert result[field] == 0, result
    assert result["volume_mm3"] > 0, result
    return result


def write_3mf(path, mesh, title="Aetherfall - Astral Sentinel"):
    # The format records millimeters explicitly. The printable part is one mesh.
    types = ('<?xml version="1.0" encoding="UTF-8"?>'
             '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
             '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
             '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>'
             '</Types>')
    relations = ('<?xml version="1.0" encoding="UTF-8"?>'
                 '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                 '<Relationship Target="/3D/3dmodel.model" Id="model" '
                 'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>'
                 '</Relationships>')
    with ZipFile(path, "w", ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", types)
        archive.writestr("_rels/.rels", relations)
        with archive.open("3D/3dmodel.model", "w") as model:
            def write(text):
                model.write(text.encode("utf-8"))

            write('<?xml version="1.0" encoding="UTF-8"?>\n'
                  '<model unit="millimeter" xml:lang="en-US" '
                  'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">\n'
                  f'<metadata name="Title">{escape(title)}</metadata>\n'
                  '<resources><object id="1" type="model"><mesh><vertices>\n')
            for v in mesh.vertices:
                x, y, z = v.co
                write(f'<vertex x="{x:.8g}" y="{y:.8g}" z="{z:.8g}"/>\n')
            write('</vertices><triangles>\n')
            for face in mesh.polygons:
                a, b, c = face.vertices
                write(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>\n')
            write('</triangles></mesh></object></resources><build><item objectid="1"/></build></model>\n')


def aim(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def setup_studio(s):
    scene = bpy.context.scene
    stage = bpy.data.collections.new("Render studio")
    scene.collection.children.link(stage)
    s.group = stage
    backdrop = material("Studio | indigo charcoal", (.027, .031, .059), .10, .49)
    floor = s.mesh("Studio floor", [(-3000, -3000, -.06), (3000, -3000, -.06),
                             (3000, 3000, -.06), (-3000, 3000, -.06)], [(0, 1, 2, 3)], backdrop)
    floor.hide_select = True

    def area(name, position, power, size, color, target, stretch=None):
        lamp = bpy.data.lights.new(name, "AREA")
        lamp.energy, lamp.color = power, color
        lamp.size = size
        if stretch:
            lamp.shape = "RECTANGLE"
            lamp.size_y = stretch
        obj = bpy.data.objects.new(name, lamp)
        stage.objects.link(obj)
        obj.location = position
        aim(obj, target)

    area("Warm key", (-73, -94, 145), 410000, 94, (1, .84, .66), (0, 0, 66), 70)
    area("Cool studio fill", (76, -73, 91), 270000, 94, (.61, .77, 1), (0, 0, 55), 124)
    area("Violet rim", (40, 61, 151), 470000, 72, (.68, .46, 1), (0, 0, 61), 105)
    area("Crown highlight", (-42, 29, 133), 235000, 54, (.81, .93, 1), (0, 0, 64))
    area("Low front bounce", (-17, -99, 28), 60000, 65, (.80, .86, 1), (0, 0, 41))
    scene.world = bpy.data.worlds.new("Studio ambient")
    scene.world.use_nodes = True
    environment = scene.world.node_tree.nodes.get("Background")
    environment.inputs["Color"].default_value = (.16, .20, .33, 1)
    environment.inputs["Strength"].default_value = .32
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.render.image_settings.file_format = "PNG"
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 112
    scene.cycles.use_denoising = False
    scene.cycles.max_bounces = 5
    scene.render.resolution_percentage = 100

    def camera(name, xyz, focus, scale):
        lens = bpy.data.cameras.new(name)
        lens.type = "ORTHO"
        lens.ortho_scale = scale
        lens.clip_end = 4000
        obj = bpy.data.objects.new(name, lens)
        stage.objects.link(obj)
        obj.location = xyz
        aim(obj, focus)
        return obj

    hero = camera("Three-quarter", (122, -245, 121), (0, 0, 59), 139)
    camera("Front", (0, -245, 89), (0, 0, 59), 136)
    camera("Right side", (245, 0, 89), (0, 0, 59), 136)
    camera("Back", (0, 245, 89), (0, 0, 59), 136)
    camera("Left side", (-245, 0, 89), (0, 0, 59), 136)
    scene.camera = hero
    for screen in bpy.data.screens:
        for view in screen.areas:
            if view.type == "VIEW_3D":
                space = view.spaces.active
                space.clip_end = 1500
                space.region_3d.view_location = (0, 0, 59)
                space.region_3d.view_distance = 182
                space.region_3d.view_rotation = hero.rotation_euler.to_quaternion()
                space.overlay.show_overlays = False
                space.shading.color_type = "MATERIAL"


def render_views(output, draft=False):
    scene = bpy.context.scene
    for name in (("Three-quarter",) if draft else
                 ("Three-quarter", "Front", "Right side", "Back", "Left side")):
        scene.camera = bpy.data.objects[name]
        if name == "Three-quarter":
            scene.cycles.samples = 32 if draft else 112
            scene.render.resolution_x = 480 if draft else 864
            scene.render.resolution_y = 600 if draft else 1080
        else:
            scene.cycles.samples = 48
            scene.render.resolution_x = 512
            scene.render.resolution_y = 640
        scene.render.filepath = str(output / (name.lower().replace(" ", "-")+".png"))
        bpy.ops.render.render(write_still=True)

    if not draft:
        layer = bpy.context.view_layer
        clay = material("QA | matte print clay", (.38, .38, .38), 0, .48)
        layer.material_override = clay
        lights = list(bpy.data.lights)
        saved_colors = [tuple(light.color) for light in lights]
        for light in lights:
            light.color = (1, 1, 1)
        try:
            scene.camera = bpy.data.objects["Three-quarter"]
            scene.cycles.samples = 64
            scene.render.resolution_x = 720
            scene.render.resolution_y = 900
            scene.render.filepath = str(output / "clay.png")
            bpy.ops.render.render(write_still=True)
        finally:
            layer.material_override = None
            for light, color in zip(lights, saved_colors):
                light.color = color


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--render", choices=("none", "draft", "all"), default="all")
    settings = parser.parse_args(sys.argv[sys.argv.index("--")+1:])
    output = settings.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = .001
    scene.unit_settings.length_unit = "MILLIMETERS"
    s = Sculpture()
    build_base(s)
    legs, arms = build_body(s)
    build_mantle(s)
    build_chest(s)
    build_limbs(s, legs, arms)
    build_helmet(s)
    print_mesh, discarded = build_print(s)
    report = inspection(print_mesh.data)
    stl = output / "astral-sentinel.stl"
    package = output / "astral-sentinel.3mf"
    select_only(print_mesh)
    bpy.ops.wm.stl_export(filepath=str(stl), ascii_format=False, export_selected_objects=True,
                          use_scene_unit=False, forward_axis="Y", up_axis="Z")
    write_3mf(package, print_mesh.data)
    bpy.ops.wm.stl_import(filepath=str(stl), use_scene_unit=False, forward_axis="Y", up_axis="Z")
    roundtrip = bpy.context.object
    roundtrip_report = inspection(roundtrip.data)
    assert roundtrip_report == report, (roundtrip_report, report)
    bpy.data.objects.remove(roundtrip, do_unlink=True)
    report["stl_sha256"] = sha256(stl.read_bytes()).hexdigest()
    report["3mf_sha256"] = sha256(package.read_bytes()).hexdigest()
    report["discarded_remesh_component_vertices"] = discarded
    report["blender"] = bpy.app.version_string
    (output / "mesh-report.json").write_text(json.dumps(report, indent=2)+"\n")
    print(json.dumps(report, indent=2), flush=True)

    setup_studio(s)
    scene.render.resolution_x = 960
    scene.render.resolution_y = 1200
    select_only(print_mesh)
    bpy.ops.wm.save_as_mainfile(filepath=str(output / "astral-sentinel.blend"), compress=True)
    if settings.render != "none":
        render_views(output, draft=settings.render == "draft")


if __name__ == "__main__":
    main()
