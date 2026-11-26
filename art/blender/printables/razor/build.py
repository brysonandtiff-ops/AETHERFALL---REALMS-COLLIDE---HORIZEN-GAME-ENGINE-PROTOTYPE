"""Aetherfall Razor collectible proposal. All dimensions are millimeters."""
import argparse
from hashlib import sha256
import json
from math import cos, pi, sin
from pathlib import Path
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "astral_sentinel"))
from build import Sculpture, aim, build_print, inspection, material, select_only, setup_studio, write_3mf


def body_section(s, name, stations, mat, sides=28):
    return s.rings(name, [
        [(x+w*cos(2*pi*i/sides), y, z+h*sin(2*pi*i/sides)) for i in range(sides)]
        for y, x, z, w, h in stations
    ], mat, True)


def spike(s, name, path, mat):
    s.tube(name, path, mat, sides=12)


def base(s):
    s.section("01  Rail plinth")
    s.loft("Beveled obsidian base", [
        (0, 0, 1, 34.5, 58), (.7, 0, 1, 36, 60), (2.3, 0, 1, 36, 60),
        (3.0, 0, 1, 35, 59), (5.9, 0, 1, 32.9, 56.5), (6.5, 0, 1, 33.7, 57.3),
        (7.3, 0, 1, 33.7, 57.3), (8.8, 0, 1, 31.5, 55)], s.stone, sides=144)
    for z, rx, ry, radius, mat in [(3.0, 35.15, 59.15, .53, s.purple),
                                     (6.05, 33.10, 56.77, .54, s.rune),
                                     (8.68, 30.85, 53.75, .53, s.rune)]:
        s.line("Inset luminous rail", [(rx*cos(2*pi*i/112), 1+ry*sin(2*pi*i/112), z)
            for i in range(113)], radius, mat)
    for i in range(12):
        angle = i*pi/6
        def p(delta, z, rx, ry):
            return (rx*cos(angle+delta), 1+ry*sin(angle+delta), z)
        n = (cos(angle), sin(angle), 0)
        s.plate("Rail chassis segment", [p(-.115, 3.1, 35.2, 59.3), p(.115, 3.1, 35.2, 59.3),
             p(.084, 5.8, 33.25, 57), p(-.084, 5.8, 33.25, 57)],
             p(0, 4.55, 34.91, 58.7), s.iron, s.violet, n)


def trunk(s):
    s.section("02  Hound anatomy and tail")
    body_section(s, "Digitigrade hound trunk", [
        (-32, 0, 55, 5.8, 7.3), (-27, 0, 54, 11.5, 13.5), (-20, 0, 51.5, 15.5, 17.6),
        (-11, 0, 48, 16.0, 16.0), (-2, 0, 46.5, 12.2, 13.4),
        (7, 0, 45, 10.4, 10.8), (15, .3, 44, 12.2, 11.5),
        (23, .35, 42.9, 12.1, 11.4), (30, .7, 42.9, 8.1, 8.2), (34, 1.1, 43, 4, 4.5)], s.dark)
    s.limb("Rising neck", (0, -22, 53), (0, -32.3, 72), 11.5, 12.6, s.dark)
    s.limb("Throat joining mandible", (0, -24, 48), (0, -38, 65), 7.1, 7.7, s.iron)
    tail = [(30, 1, 44, 5.9, 6.2), (35, 1.8, 43.8, 5.25, 5.5), (41, 3.1, 40.8, 4.8, 5.2),
            (47, 5.5, 36.0, 4.25, 4.5), (53, 8.15, 30.7, 3.45, 3.9),
            (58, 10.4, 25.75, 2.65, 3.1), (62, 12.75, 19.4, 1.55, 2.3),
            (65.5, 13.7, 14.8, .6, .63)]
    body_section(s, "Tapered vertebral tail", tail, s.dark)
    for i, (y, x, z, w, h) in enumerate(tail[:-1]):
        for k in (-1, 1):
            n = (k*.53, .07, .84)
            s.feather("Interlocking tail scute", [
                ((x+k*w*.63, y-1, z+h*.60), w*.57, 1.1),
                ((x+k*w*.81, y+1, z+h*.78), w*.75, 1.3),
                ((x+k*w*.88, y+3.1, z+h*.43), w*.61, 1.1),
                ((x+k*w*.63, y+5.1, z-.9), .47, .49)], s.gold, s.blue, n)

    s.section("03  Dorsal bone rails")
    rail = [(-33, 79, 12), (-28.8, 80, 15.4), (-23.2, 77.4, 16), (-17.4, 72.0, 15),
            (-11.1, 65.7, 13.7), (-3.5, 60.5, 12), (3.5, 56.9, 11),
            (10.3, 55.5, 9.7), (17.7, 54.9, 9.2), (24.6, 54, 8.1),
            (31.3, 50.1, 7.8), (37.7, 47.9, 7.15), (44.3, 43.4, 6.64),
            (50.4, 38.6, 6.05), (56.5, 33.2, 5.55), (61.3, 27.3, 4.9)]
    for i, (y, z, rise) in enumerate(rail):
        x = max(y-31, 0)*.355
        w = 1.5 + rise*.12
        s.ellipsoid("Vertebral saddle", (x, y, z-1.1), (w*1.25, w*1.1, 2.7), s.gold)
        s.feather("Crimson hooked rail", [
            ((x, y-.6, z-.8), w*.91, 1.87),
            ((x-.4, y-.05, z+rise*.46), w*.83, 1.65),
            ((x-.22, y+rise*.22, z+rise*.83), w*.67, 1.39),
            ((x, y+rise*.71, z+rise), .46, .50)],
            s.red, s.crimson, (.98, 0, .15))
    for k in (-1, 1):
        for i in range(9):
            y = -30 + i*6.65
            z = 70.2 - min(i, 5)*3.65
            x = (8.8, 11.7, 14, 14.4, 12.7, 10, 9, 9.7, 10.4)[i]
            s.feather("Interlocking scapular and flank plate", [
                ((k*(x-3.5), y-.8, z+2.4), 2.8, 1.7),
                ((k*(x-.6), y+.3, z-.65), 3.8, 2.1),
                ((k*(x+1.7), y+1.25, z-5.55), 3.25, 1.8),
                ((k*(x+1.1), y+4.7, z-10.4), 1.42, 1.23),
                ((k*(x-.75), y+7, z-14.6), .49, .52)],
                s.blue if i % 3 == 0 else s.gold, s.purple if i % 3 == 0 else s.bone_shadow,
                (k, -.07, .16))
            s.line("Raised aether fissure", [(k*(x-2.0), y-3.5, z),
                 (k*(x+.62), y-2.4, z-6.2), (k*(x+.10), y-.35, z-8.3),
                 (k*(x-.55), y-1.3, z-12.0)], .53, s.crimson)


def limbs(s):
    s.section("04  Legs, paws and claws")
    for front, triplets in [(True, [
        ((-12, -19.7, 49), (-14.4, -18.3, 31.3), (-16.3, -27.8, 13.1)),
        ((12, -18.7, 49), (14.8, -17.1, 30.6), (15.3, -19.9, 13.1))]), (False, [
        ((-9.5, 22, 43.8), (-12.3, 15.1, 30.0), (-13.5, 31.8, 17.7)),
        ((9.4, 20.7, 42.5), (12, 13.9, 29.3), (13.2, 26.6, 17.8))])]:
        for hip, knee, ankle in triplets:
            x, y, z = ankle
            side = -1 if x < 0 else 1
            s.limb("Heavy upper leg", hip, knee, 6.1 if front else 5.6, 7.3, s.dark)
            s.ellipsoid("Carpal joint", knee, (4.7, 5.1, 4.9), s.iron)
            s.limb("Digitigrade shin", knee, ankle, 3.8, 4.7, s.dark)
            if not front:
                s.limb("Raised rear hock", ankle, (x, y-2.8, 10.4), 2.98, 3.2, s.iron)
            else:
                s.limb("Forepaw pastern", ankle, (x, y-.6, 10.25), 3.3, 3.4, s.iron)
            paw = (x, y-1.65, 10.28)
            s.ellipsoid("Weighted paw", paw, (4.8, 4.3, 2.5), s.dark)
            for toe in (-1.5, -.5, .5, 1.5):
                tx = x + toe*2.05
                ty = y - 5.2 + .63*abs(toe)
                s.ellipsoid("Toe knuckle", (tx, ty+.44, 10.45), (1.49, 2.12, 1.98), s.bone_shadow)
                spike(s, "Curved ivory talon", [
                    ((tx, ty-.18, 11.3), 1.15), ((tx+.13*toe, ty-1.22, 10.86), .94),
                    ((tx+.26*toe, ty-2.23, 9.55), .64), ((tx+.39*toe, ty-2.76, 8.79), .42)], s.gold)
            for n, start, end in [("Scapula", hip, knee), ("Gait armor", knee, (x, y, 13.7))]:
                a, b = Vector(start), Vector(end)
                length = (b-a).length
                outward = Vector((side, -.50, .1))
                path = []
                for t, off, span, depth in [(.06, 2.8, .17, 1.4), (.30, 4.8, .23, 2),
                    (.64, 4.95, .174, 1.9), (.87, 4.05, .10, 1.3), (.99, 2.3, .03, .51)]:
                    path.append((a.lerp(b, t)+outward*off, max(.48, span*length), depth))
                s.feather(n+" relief", path, s.gold, s.bone_shadow, outward)
                a0 = a.lerp(b, .30)+Vector((side*3.4, 2.1, 0))
                a1 = a.lerp(b, .66)+Vector((side*3.8, 3.4, 0))
                s.blade("Crimson cartilage strip", [(a0, 1.10, 1.15), (a1, 1.30, 1.26),
                         (b+Vector((side*2.2, 1.75, .5)), .43, .52)], s.red,
                         (side, .4, 0), s.crimson)


def head(s):
    s.section("05  Skull, teeth and yoke")
    body_section(s, "Ivory angular skull", [
        (-57.0, 0, 73.0, 2.8, 2.2), (-55.1, 0, 72.8, 4.9, 3.9),
        (-50.5, 0, 73.8, 6.1, 4.2), (-46.0, 0, 75.9, 7.5, 5.6),
        (-40.9, 0, 77.0, 8.6, 7.15), (-35, 0, 76.9, 8.65, 7.2),
        (-29.7, 0, 74.5, 7.85, 7.0), (-27.6, 0, 73.4, 5.4, 4.8)], s.gold, sides=28)
    body_section(s, "Hinged open mandible", [
        (-54.65, 0, 62.8, 2.3, 1.8), (-52.5, 0, 61.4, 3.8, 2.3),
        (-47.8, 0, 60.5, 5.1, 2.8), (-43.4, 0, 61.8, 6.22, 3.58),
        (-39.6, 0, 64.8, 7.15, 5.15), (-34.5, 0, 68.1, 7.65, 6.2),
        (-30.7, 0, 67.4, 6.1, 4.0)], s.bone_shadow)
    for k in (-1, 1):
        n = (k, -.12, .3)
        s.ellipsoid("Recessed eye socket", (k*7.17, -44.16, 77.8), (1.76, 3.0, 2.03), s.dark)
        s.ellipsoid("Molten eye", (k*8.28, -44.43, 78.0), (.87, 1.56, 1.18), s.crimson)
        s.ellipsoid("Nasal cavity paint guide", (k*2.8, -55.8, 73.77), (1.01, .99, 1.08), s.dark)
        s.feather("Barbed supraorbital bridge", [
            ((k*2.5, -54.5, 75.0), 1.3, .86), ((k*5.0, -49.4, 77.9), 2.05, 1.06),
            ((k*7.3, -44.0, 80.36), 2.15, 1.3), ((k*8.2, -39.4, 81.16), 1.9, 1.35),
            ((k*10.4, -32.2, 83), .44, .56)], s.gold, s.bone_shadow, n)
        s.feather("Hooked cheek arch", [
            ((k*5.1, -50.3, 72.85), 1.8, 1.1), ((k*7.65, -44.0, 74.02), 2.75, 1.55),
            ((k*8.51, -38.3, 72.7), 3.3, 1.75), ((k*9.32, -37.9, 68.3), 1.4, 1.25),
            ((k*7.23, -42.8, 61.7), .49, .53)], s.gold, s.bone_shadow, n)
        for i, (y, z) in enumerate([(-54.9, 70.68), (-52.5, 70.66), (-49.8, 70.6), (-47.12, 70.67), (-44.6, 71.15)]):
            x = k*(2.7+.59*i)
            size = (3.1, 4.15, 6.87, 4.0, 3.7)[i]
            spike(s, "Upper fang", [((x, y, z+1.02), 1.09),
                  ((x, y-.15, z-size*.46), .83),
                  ((x-k*.27, y+.63, z-size), .365)], s.gold)
        for i, (y, z) in enumerate([(-52.2, 62.7), (-49.4, 62.75), (-46.5, 62.89), (-43.5, 64.0)]):
            x = k*(2.7+i*.63)
            spike(s, "Lower fang", [((x, y, z-.56), .9), ((x, y+.1, z+1.3), .64),
                  ((x-k*.18, y+.55, z+(2.65 if i != 2 else 4.08)), .36)], s.gold)
    s.ellipsoid("Sternum yoke", (0, -31.5, 52.7), (10.8, 4.2, 5.15), s.iron)
    for k in (-1, 1):
        s.feather("Yoke shoulder clasps", [
            ((k*10.25, -24.3, 59.7), 2.1, 1.53), ((k*13.7, -26.5, 54.3), 3.35, 1.99),
            ((k*12.8, -31.75, 50.7), 2.2, 1.48), ((k*8.2, -35, 50.1), .64, .6)],
            s.blue, s.gold, (k*.54, -.81, .34))
    # Interwoven links have deliberately overlapping joints and two structural anchors.
    guide = [(-12.6, -29.0, 54.1), (-14.9, -36.5, 49.6), (-13.7, -45.7, 48.7),
             (-10.1, -54.7, 51.1), (-5.3, -58.3, 55.5), (0, -56.05, 64.0)]
    positions = [Vector(guide[0])]
    for a, b in zip(guide, guide[1:]):
        a, b = Vector(a), Vector(b)
        count = round((b-a).length/3.17)
        positions.extend(a.lerp(b, i/count) for i in range(1, count+1))
    for i, center in enumerate(positions):
        tangent = (positions[min(i+1, len(positions)-1)] - positions[max(i-1, 0)]).normalized()
        across = tangent.cross(Vector((1, .15, 0))).normalized()
        if i % 2:
            across = tangent.cross(across).normalized()
        loop = [center + tangent*2.65*cos(j*pi/12) + across*1.45*sin(j*pi/12) for j in range(25)]
        s.line("Structural chain link", loop, .66, s.silver)
        if i:
            s.ellipsoid("Welded pin inside chain overlap", center.lerp(positions[i-1], .5),
                        (.72, .78, .73), s.silver, detail=2)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--draft", action="store_true")
    options = parser.parse_args(sys.argv[sys.argv.index("--")+1:])
    out = options.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = .001
    scene.unit_settings.length_unit = "MILLIMETERS"
    s = Sculpture()
    s.gold = material("Aged ivory | bone armor", (.64, .46, .32), .16, .37)
    s.bone_shadow = material("Bone | darker bevel", (.26, .13, .10), .22, .40)
    s.blue = material("Forged amethyst | structural plates", (.20, .065, .34), .56, .31)
    s.red = material("Sanguine rail | lacquer", (.40, .009, .027), .40, .28, .34)
    s.crimson = material("Scarlet aether | fissure", (.75, .014, .03), .21, .21, 1.2)
    s.rune = material("Magenta | plinth circuit", (.51, .018, .33), .25, .26, .94)
    s.palette.extend([s.gold, s.bone_shadow, s.blue, s.red, s.crimson, s.rune])
    base(s)
    trunk(s)
    limbs(s)
    head(s)
    mesh, fragments = build_print(s)
    mesh.name = "Razor • fused print"
    report = inspection(mesh.data)
    report["discarded_remesh_component_vertices"] = fragments
    select_only(mesh)
    bpy.ops.wm.stl_export(filepath=str(out/"razor.stl"), export_selected_objects=True,
                          use_scene_unit=False, forward_axis="Y", up_axis="Z")
    write_3mf(out/"razor.3mf", mesh.data, title="Aetherfall - Razor")
    for suffix in ("stl", "3mf"):
        report[suffix+"_sha256"] = sha256((out/f"razor.{suffix}").read_bytes()).hexdigest()
    (out/"mesh-report.json").write_text(json.dumps(report, indent=2)+"\n")
    setup_studio(s)
    hero = bpy.data.objects["Three-quarter"]
    hero.location = (-224, -136, 123)
    aim(hero, (0, 0, 45))
    hero.data.ortho_scale = 147
    scene.render.resolution_x = 680 if options.draft else 1180
    scene.render.resolution_y = 520 if options.draft else 900
    scene.cycles.samples = 24 if options.draft else 72
    bpy.ops.wm.save_as_mainfile(filepath=str(out/"razor.blend"), compress=True)
    scene.render.filepath = str(out/"razor-color.png")
    bpy.ops.render.render(write_still=True)
    if not options.draft:
        s.parts.hide_render = True
        bpy.context.view_layer.material_override = material("Print clay", (.38, .38, .38), 0, .49)
        for light in bpy.data.lights:
            light.color = (1, 1, 1)
        scene.render.filepath = str(out/"razor-clay.png")
        bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
