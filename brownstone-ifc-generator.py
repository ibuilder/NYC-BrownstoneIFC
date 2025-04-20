"""
Brownstone IFC Generator

This script generates a simplified IFC model of a New York brownstone based on
the specifications provided. It uses IfcOpenShell to create the model.

Requirements:
- ifcopenshell
- numpy

Installation:
pip install ifcopenshell numpy

Note: On some systems, you may need to install ifcopenshell from its GitHub repository.
"""

import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.placement
import time
import os
import sys
import math
import uuid
import tempfile
import numpy as np
from datetime import datetime

# Global parameters for the brownstone
BUILDING_WIDTH = 40.0  # feet
BUILDING_DEPTH = 80.0  # feet
BASEMENT_HEIGHT = 9.0  # feet
FIRST_FLOOR_HEIGHT = 10.0  # feet
SECOND_FLOOR_HEIGHT = 14.0  # feet
THIRD_FLOOR_HEIGHT = 12.0  # feet
FOURTH_FLOOR_HEIGHT = 12.0  # feet
WALL_THICKNESS = 1.0  # feet
FLOOR_THICKNESS = 1.0  # feet
ROOF_THICKNESS = 1.5  # feet

# Convert to metric (IFC uses meters)
FOOT_TO_METER = 0.3048
INCH_TO_METER = 0.0254

def convert_to_meter(feet):
    """Convert feet to meters"""
    return feet * FOOT_TO_METER

def create_guid():
    """Generate a GUID for IFC entities"""
    return ifcopenshell.guid.compress(uuid.uuid4().hex)

def create_ifc_model():
    """Create a new IFC model with basic setup"""
    # Create a new IFC file
    model = ifcopenshell.file()
    
    # Add IFC schema
    model.schema = "IFC4"
    
    # Create head entities
    timestamp = int(time.time())
    timestring = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    
    # Create the person, organization and application
    person = model.createIfcPerson("John", "Doe")
    organization = model.createIfcOrganization(name="Brownstone Architects")
    application = model.createIfcApplication(organization, "1.0", "Brownstone IFC Generator", "Brownstone Generator")
    
    # Create person and organization combination
    person_and_org = model.createIfcPersonAndOrganization(person, organization)
    
    # Create ownership information
    owner_history = model.createIfcOwnerHistory(person_and_org, application, "READWRITE", None, None, None, None, timestring)
    
    # Create project context
    project_context = model.createIfcGeometricRepresentationContext(None, "Model", 3, 1.0E-5, 
                                                                   model.createIfcAxis2Placement3D(
                                                                       model.createIfcCartesianPoint([0.0, 0.0, 0.0]),
                                                                       model.createIfcDirection([0.0, 0.0, 1.0]),
                                                                       model.createIfcDirection([1.0, 0.0, 0.0])
                                                                   ), None)
    
    # Define units
    length_unit = model.createIfcSIUnit(None, "LENGTHUNIT", None, "METRE")
    area_unit = model.createIfcSIUnit(None, "AREAUNIT", None, "SQUARE_METRE")
    volume_unit = model.createIfcSIUnit(None, "VOLUMEUNIT", None, "CUBIC_METRE")
    units = model.createIfcUnitAssignment([length_unit, area_unit, volume_unit])
    
    # Create the project
    project = model.createIfcProject(create_guid(), owner_history, "New York Brownstone", 
                                     "Brownstone on 50'x100' lot", None, None, None, [project_context], units)
    
    return model, project, owner_history, project_context

def create_site(model, project, owner_history):
    """Create a site object"""
    site = model.createIfcSite(create_guid(), owner_history, "Brownstone Site", "Site for brownstone building", 
                              None, None, None, None, "ELEMENT", None, None, None, None, None)
    
    # Relate site to project
    model.createIfcRelAggregates(create_guid(), owner_history, "Project Container", None, project, [site])
    
    return site

def create_building(model, site, owner_history):
    """Create a building object"""
    building = model.createIfcBuilding(create_guid(), owner_history, "New York Brownstone", "Classic brownstone building", 
                                      None, None, None, None, "ELEMENT", None, None, None)
    
    # Relate building to site
    model.createIfcRelAggregates(create_guid(), owner_history, "Site Container", None, site, [building])
    
    return building

def create_storeys(model, building, owner_history):
    """Create building storeys"""
    storeys = []
    storey_names = ["Basement", "First Floor", "Second Floor", "Third Floor", "Fourth Floor", "Roof"]
    storey_elevations = [
        -convert_to_meter(BASEMENT_HEIGHT),
        0.0,
        convert_to_meter(FIRST_FLOOR_HEIGHT),
        convert_to_meter(FIRST_FLOOR_HEIGHT + SECOND_FLOOR_HEIGHT),
        convert_to_meter(FIRST_FLOOR_HEIGHT + SECOND_FLOOR_HEIGHT + THIRD_FLOOR_HEIGHT),
        convert_to_meter(FIRST_FLOOR_HEIGHT + SECOND_FLOOR_HEIGHT + THIRD_FLOOR_HEIGHT + FOURTH_FLOOR_HEIGHT)
    ]
    
    for i, (name, elevation) in enumerate(zip(storey_names, storey_elevations)):
        storey = model.createIfcBuildingStorey(create_guid(), owner_history, name, 
                                              f"{name} of the brownstone", None,
                                              model.createIfcLocalPlacement(None, 
                                                                          model.createIfcAxis2Placement3D(
                                                                              model.createIfcCartesianPoint([0.0, 0.0, elevation]),
                                                                              model.createIfcDirection([0.0, 0.0, 1.0]),
                                                                              model.createIfcDirection([1.0, 0.0, 0.0])
                                                                          )),
                                              None, None, "ELEMENT", elevation)
        storeys.append(storey)
    
    # Relate storeys to building
    model.createIfcRelAggregates(create_guid(), owner_history, "Building Container", None, building, storeys)
    
    return storeys

def create_walls(model, storeys, owner_history, context):
    """Create the walls for each storey"""
    all_walls = []
    
    # Wall heights for each storey
    wall_heights = [
        BASEMENT_HEIGHT,
        FIRST_FLOOR_HEIGHT,
        SECOND_FLOOR_HEIGHT,
        THIRD_FLOOR_HEIGHT,
        FOURTH_FLOOR_HEIGHT
    ]
    
    for i, storey in enumerate(storeys[:-1]):  # Skip roof "storey"
        # Get the storey elevation
        storey_elevation = storey.Elevation
        wall_height = convert_to_meter(wall_heights[i])
        
        # Calculate width and depth in meters
        width = convert_to_meter(BUILDING_WIDTH)
        depth = convert_to_meter(BUILDING_DEPTH)
        thickness = convert_to_meter(WALL_THICKNESS)
        
        walls = []
        
        # Wall material based on floor
        if i == 0:  # Basement
            material_name = "Concrete"
        elif i == 1 or i == 2:  # First and Second Floor
            material_name = "Brownstone"
        else:  # Upper floors
            material_name = "Brick"
        
        # Create a material
        material = model.createIfcMaterial(material_name)
        material_layer = model.createIfcMaterialLayer(material, convert_to_meter(WALL_THICKNESS), None)
        material_layer_set = model.createIfcMaterialLayerSet([material_layer], None)
        material_layer_set_usage = model.createIfcMaterialLayerSetUsage(material_layer_set, "AXIS2", "POSITIVE", 0.0)
        
        # Create front wall (with potential openings)
        front_wall = create_wall(model, owner_history, context, 
                                "Front Wall", 
                                [0, 0, storey_elevation], 
                                [width, 0, storey_elevation], 
                                thickness, wall_height, material_layer_set_usage)
        walls.append(front_wall)
        
        # Create back wall
        back_wall = create_wall(model, owner_history, context, 
                               "Back Wall", 
                               [0, depth, storey_elevation], 
                               [width, depth, storey_elevation], 
                               thickness, wall_height, material_layer_set_usage)
        walls.append(back_wall)
        
        # Create left wall
        left_wall = create_wall(model, owner_history, context, 
                               "Left Wall", 
                               [0, 0, storey_elevation], 
                               [0, depth, storey_elevation], 
                               thickness, wall_height, material_layer_set_usage)
        walls.append(left_wall)
        
        # Create right wall
        right_wall = create_wall(model, owner_history, context, 
                                "Right Wall", 
                                [width, 0, storey_elevation], 
                                [width, depth, storey_elevation], 
                                thickness, wall_height, material_layer_set_usage)
        walls.append(right_wall)
        
        # Add interior walls for a simplified layout
        if i > 0:  # Not in basement
            # Central corridor wall
            corridor_wall = create_wall(model, owner_history, context,
                                       "Corridor Wall",
                                       [0, depth/2, storey_elevation],
                                       [width, depth/2, storey_elevation],
                                       thickness, wall_height, material_layer_set_usage)
            walls.append(corridor_wall)
            
            # Cross walls
            for j in range(1, 3):
                cross_wall = create_wall(model, owner_history, context,
                                        f"Cross Wall {j}",
                                        [width/3 * j, 0, storey_elevation],
                                        [width/3 * j, depth, storey_elevation],
                                        thickness, wall_height, material_layer_set_usage)
                walls.append(cross_wall)
        
        # Relate walls to storey
        model.createIfcRelContainedInSpatialStructure(create_guid(), owner_history, 
                                                     f"Storey {i} Walls", None, walls, storey)
        
        all_walls.extend(walls)
    
    return all_walls

def create_wall(model, owner_history, context, name, start_point, end_point, thickness, height, material_layer_set_usage):
    """Create a wall with the given parameters"""
    # Calculate direction and length
    direction = [end_point[0] - start_point[0], end_point[1] - start_point[1], 0]
    length = math.sqrt(direction[0]**2 + direction[1]**2)
    
    if length == 0:
        return None
    
    # Normalize direction
    normalized_direction = [direction[0] / length, direction[1] / length, 0]
    
    # Create perpendicular direction (for wall thickness)
    perp_direction = [-normalized_direction[1], normalized_direction[0], 0]
    
    # Create placement
    wall_placement = model.createIfcLocalPlacement(None,
                                                 model.createIfcAxis2Placement3D(
                                                     model.createIfcCartesianPoint(start_point),
                                                     model.createIfcDirection([0.0, 0.0, 1.0]),
                                                     model.createIfcDirection(normalized_direction)
                                                 ))
    
    # Create wall shape representation
    extrusion = create_wall_extrusion(model, context, length, thickness, height)
    
    # Create wall
    wall = model.createIfcWallStandardCase(create_guid(), owner_history, name, "Exterior Wall", 
                                          None, wall_placement, extrusion, None, None)
    
    # Assign material
    model.createIfcRelAssociatesMaterial(create_guid(), owner_history, None, None, [wall], material_layer_set_usage)
    
    return wall

def create_wall_extrusion(model, context, length, thickness, height):
    """Create an extrusion for a wall"""
    # Create profile
    points = [
        [0, -thickness/2],
        [length, -thickness/2],
        [length, thickness/2],
        [0, thickness/2],
        [0, -thickness/2]
    ]
    
    polyline = model.createIfcPolyline([model.createIfcCartesianPoint(point) for point in points])
    profile = model.createIfcArbitraryClosedProfileDef("AREA", None, polyline)
    
    # Create extrusion
    extrusion_direction = model.createIfcDirection([0.0, 0.0, 1.0])
    extrusion = model.createIfcExtrudedAreaSolid(profile, 
                                              model.createIfcAxis2Placement3D(
                                                  model.createIfcCartesianPoint([0.0, 0.0, 0.0]),
                                                  model.createIfcDirection([0.0, 0.0, 1.0]),
                                                  model.createIfcDirection([1.0, 0.0, 0.0])
                                              ),
                                              extrusion_direction,
                                              height)
    
    # Create shape representation
    shape_representation = model.createIfcShapeRepresentation(context, "Body", "SweptSolid", [extrusion])
    
    # Create product definition shape
    product_definition_shape = model.createIfcProductDefinitionShape(None, None, [shape_representation])
    
    return product_definition_shape

def create_slabs(model, storeys, owner_history, context):
    """Create floor slabs for each level"""
    all_slabs = []
    
    for i, storey in enumerate(storeys[:-1]):  # Skip the roof "storey"
        # Get the storey elevation
        storey_elevation = storey.Elevation
        next_elevation = storeys[i+1].Elevation
        
        # Calculate width and depth in meters
        width = convert_to_meter(BUILDING_WIDTH)
        depth = convert_to_meter(BUILDING_DEPTH)
        
        # Material based on floor
        material_name = "Concrete" if i == 0 else "Wood Floor"
        
        # Create material
        material = model.createIfcMaterial(material_name)
        material_layer = model.createIfcMaterialLayer(material, convert_to_meter(FLOOR_THICKNESS), None)
        material_layer_set = model.createIfcMaterialLayerSet([material_layer], None)
        material_layer_set_usage = model.createIfcMaterialLayerSetUsage(material_layer_set, "AXIS2", "POSITIVE", 0.0)
        
        # Create placement at the next floor level (bottom of the slab)
        slab_placement = model.createIfcLocalPlacement(None,
                                                    model.createIfcAxis2Placement3D(
                                                        model.createIfcCartesianPoint([0.0, 0.0, next_elevation - convert_to_meter(FLOOR_THICKNESS)]),
                                                        model.createIfcDirection([0.0, 0.0, 1.0]),
                                                        model.createIfcDirection([1.0, 0.0, 0.0])
                                                    ))
        
        # Create slab shape representation
        extrusion = create_slab_extrusion(model, context, width, depth, convert_to_meter(FLOOR_THICKNESS))
        
        # Create slab
        slab_name = "Roof" if i == len(storeys) - 2 else f"Floor {i+1}"
        slab_type = "ROOF" if i == len(storeys) - 2 else "FLOOR"
        slab = model.createIfcSlab(create_guid(), owner_history, slab_name, 
                                  f"{slab_name} of the brownstone", None,
                                  slab_placement, extrusion, None, slab_type)
        
        # Assign material
        model.createIfcRelAssociatesMaterial(create_guid(), owner_history, None, None, [slab], material_layer_set_usage)
        
        # Relate slab to storey
        model.createIfcRelContainedInSpatialStructure(create_guid(), owner_history, 
                                                    f"Storey {i} Slab", None, [slab], storeys[i+1])
        
        all_slabs.append(slab)
    
    # Create roof slab
    top_storey = storeys[-1]
    top_elevation = top_storey.Elevation
    
    # Calculate width and depth in meters
    width = convert_to_meter(BUILDING_WIDTH)
    depth = convert_to_meter(BUILDING_DEPTH)
    
    # Create roof material
    roof_material = model.createIfcMaterial("Roof Membrane")
    roof_material_layer = model.createIfcMaterialLayer(roof_material, convert_to_meter(ROOF_THICKNESS), None)
    roof_material_layer_set = model.createIfcMaterialLayerSet([roof_material_layer], None)
    roof_material_layer_set_usage = model.createIfcMaterialLayerSetUsage(roof_material_layer_set, "AXIS2", "POSITIVE", 0.0)
    
    # Create roof placement
    roof_placement = model.createIfcLocalPlacement(None,
                                                model.createIfcAxis2Placement3D(
                                                    model.createIfcCartesianPoint([0.0, 0.0, top_elevation]),
                                                    model.createIfcDirection([0.0, 0.0, 1.0]),
                                                    model.createIfcDirection([1.0, 0.0, 0.0])
                                                ))
    
    # Create roof shape representation
    roof_extrusion = create_slab_extrusion(model, context, width, depth, convert_to_meter(ROOF_THICKNESS))
    
    # Create roof
    roof = model.createIfcSlab(create_guid(), owner_history, "Roof Slab", 
                             "Roof of the brownstone", None,
                             roof_placement, roof_extrusion, None, "ROOF")
    
    # Assign material
    model.createIfcRelAssociatesMaterial(create_guid(), owner_history, None, None, [roof], roof_material_layer_set_usage)
    
    # Relate roof to top storey
    model.createIfcRelContainedInSpatialStructure(create_guid(), owner_history, 
                                                "Roof Slab", None, [roof], top_storey)
    
    all_slabs.append(roof)
    
    return all_slabs

def create_slab_extrusion(model, context, width, depth, thickness):
    """Create an extrusion for a slab"""
    # Create profile
    points = [
        [0, 0],
        [width, 0],
        [width, depth],
        [0, depth],
        [0, 0]
    ]
    
    polyline = model.createIfcPolyline([model.createIfcCartesianPoint(point) for point in points])
    profile = model.createIfcArbitraryClosedProfileDef("AREA", None, polyline)
    
    # Create extrusion
    extrusion_direction = model.createIfcDirection([0.0, 0.0, 1.0])
    extrusion = model.createIfcExtrudedAreaSolid(profile,
                                              model.createIfcAxis2Placement3D(
                                                  model.createIfcCartesianPoint([0.0, 0.0, 0.0]),
                                                  model.createIfcDirection([0.0, 0.0, 1.0]),
                                                  model.createIfcDirection([1.0, 0.0, 0.0])
                                              ),
                                              extrusion_direction,
                                              thickness)
    
    # Create shape representation
    shape_representation = model.createIfcShapeRepresentation(context, "Body", "SweptSolid", [extrusion])
    
    # Create product definition shape
    product_definition_shape = model.createIfcProductDefinitionShape(None, None, [shape_representation])
    
    return product_definition_shape

def create_door_extrusion(model, context, width, height, thickness):
    """Create an extrusion for a door"""
    # Create profile
    points = [
        [0, 0],
        [width, 0],
        [width, height],
        [0, height],
        [0, 0]
    ]
    
    polyline = model.createIfcPolyline([model.createIfcCartesianPoint(point) for point in points])
    profile = model.createIfcArbitraryClosedProfileDef("AREA", None, polyline)
    
    # Create extrusion
    extrusion_direction = model.createIfcDirection([0.0, 1.0, 0.0])
    extrusion = model.createIfcExtrudedAreaSolid(profile,
                                              model.createIfcAxis2Placement3D(
                                                  model.createIfcCartesianPoint([0.0, 0.0, 0.0]),
                                                  model.createIfcDirection([0.0, 0.0, 1.0]),
                                                  model.createIfcDirection([1.0, 0.0, 0.0])
                                              ),
                                              extrusion_direction,
                                              thickness)
    
    # Create shape representation
    shape_representation = model.createIfcShapeRepresentation(context, "Body", "SweptSolid", [extrusion])
    
    # Create product definition shape
    product_definition_shape = model.createIfcProductDefinitionShape(None, None, [shape_representation])
    
    return product_definition_shape

def create_door(model, owner_history, context, name, position, width, height):
    """Create a door with the given parameters"""
    # Create door placement
    door_placement = model.createIfcLocalPlacement(None,
                                                 model.createIfcAxis2Placement3D(
                                                     model.createIfcCartesianPoint(position),
                                                     model.createIfcDirection([0.0, 0.0, 1.0]),
                                                     model.createIfcDirection([1.0, 0.0, 0.0])
                                                 ))
    
    # Create door shape representation
    extrusion = create_door_extrusion(model, context, width, height, convert_to_meter(WALL_THICKNESS))
    
    # Create door
    door = model.createIfcDoor(create_guid(), owner_history, name, 
                             "Door", None, door_placement, extrusion, None, height)
    
    return door

def create_doors(model, storeys, owner_history, context):
    """Create doors in the brownstone"""
    all_doors = []
    
    # Create front door
    front_door_width = convert_to_meter(4.0)
    front_door_height = convert_to_meter(8.0)
    
    # Calculate building width in meters
    building_width = convert_to_meter(BUILDING_WIDTH)
    building_depth = convert_to_meter(BUILDING_DEPTH)
    
    # Create front door at the first floor (main entrance)
    front_door_position = [building_width/2 - front_door_width/2, 0, storeys[1].Elevation]
    front_door = create_door(model, owner_history, context,
                           "Front Door",
                           front_door_position,
                           front_door_width, front_door_height)
    all_doors.append(front_door)
    
    # Relate front door to first floor
    model.createIfcRelContainedInSpatialStructure(create_guid(), owner_history, 
                                                "Front Door", None, [front_door], storeys[1])
    
    # Create interior doors
    for i, storey in enumerate(storeys[:-1]):  # Skip roof
        storey_elevation = storey.Elevation
        
        # Skip basement for simplicity
        if i == 0:
            continue
        
        # Create interior doors
        interior_doors = []
        door_width = convert_to_meter(3.0)
        door_height = convert_to_meter(7.0)
        
        # Doors along the central corridor
        for j in range(2):
            # Door positions along the central corridor
            door_position = [building_width/3 * (j+1), building_depth/2, storey_elevation]
            door = create_door(model, owner_history, context,
                             f"Interior Door {i}-{j}",
                             door_position,
                             door_width, door_height)
            interior_doors.append(door)
        
        # Relate interior doors to storey
        all_doors.extend(interior_doors)
        model.createIfcRelContainedInSpatialStructure(create_guid(), owner_history, 
                                                    f"Storey {i} Doors", None, interior_doors, storey)
    
    return all_doors

def create_window_extrusion(model, context, width, height, thickness):
    """Create an extrusion for a window"""
    # Create profile
    points = [
        [0, 0],
        [width, 0],
        [width, height],
        [0, height],
        [0, 0]
    ]
    
    polyline = model.createIfcPolyline([model.createIfcCartesianPoint(point) for point in points])
    profile = model.createIfcArbitraryClosedProfileDef("AREA", None, polyline)
    
    # Create extrusion
    extrusion_direction = model.createIfcDirection([0.0, 1.0, 0.0])
    extrusion = model.createIfcExtrudedAreaSolid(profile,
                                              model.createIfcAxis2Placement3D(
                                                  model.createIfcCartesianPoint([0.0, 0.0, 0.0]),
                                                  model.createIfcDirection([0.0, 0.0, 1.0]),
                                                  model.createIfcDirection([1.0, 0.0, 0.0])
                                              ),
                                              extrusion_direction,
                                              thickness)
    
    # Create shape representation
    shape_representation = model.createIfcShapeRepresentation(context, "Body", "SweptSolid", [extrusion])
    
    # Create product definition shape
    product_definition_shape = model.createIfcProductDefinitionShape(None, None, [shape_representation])
    
    return product_definition_shape

def create_window(model, owner_history, context, name, position, width, height):
    """Create a window with the given parameters"""
    # Create window placement
    window_placement = model.createIfcLocalPlacement(None,
                                                   model.createIfcAxis2Placement3D(
                                                       model.createIfcCartesianPoint(position),
                                                       model.createIfcDirection([0.0, 0.0, 1.0]),
                                                       model.createIfcDirection([1.0, 0.0, 0.0])
                                                   ))
    
    # Create window shape representation
    extrusion = create_window_extrusion(model, context, width, height, convert_to_meter(WALL_THICKNESS))
    
    # Create window
    window = model.createIfcWindow(create_guid(), owner_history, name, 
                                  "Window", None, window_placement, extrusion, None, None)
    
    return window

def create_windows(model, storeys, owner_history, context):
    """Create windows on the front and back facades"""
    all_windows = []
    
    # Window properties for each floor
    window_heights = {
        0: 3.0,  # Basement
        1: 6.0,  # First Floor
        2: 8.0,  # Second Floor (Parlor)
        3: 6.0,  # Third Floor
        4: 6.0,  # Fourth Floor
    }
    
    window_widths = {
        0: 3.0,  # Basement
        1: 3.5,  # First Floor
        2: 4.0,  # Second Floor (Parlor)
        3: 3.5,  # Third Floor
        4: 3.5,  # Fourth Floor
    }
    
    # Skip the roof "storey"
    for i, storey in enumerate(storeys[:-1]):
        # Skip basement for front windows (brownstones typically have fewer/smaller basement windows)
        if i == 0:
            window_count = 2  # Fewer windows in basement
        else:
            window_count = 3  # Standard floors
        
        # Get the storey elevation
        storey_elevation = storey.Elevation
        
        # Calculate width in meters
        building_width = convert_to_meter(BUILDING_WIDTH)
        building_depth = convert_to_meter(BUILDING_DEPTH)
        
        # Window dimensions
        window_width = convert_to_meter(window_widths[i])
        window_height = convert_to_meter(window_heights[i])
        
        # Window sill height (distance from floor to bottom of window)
        sill_height = convert_to_meter(3.0)
        
        # Create front windows
        front_windows = []
        for j in range(window_count):
            # Calculate window position
            if window_count == 1:
                x_position = building_width / 2 - window_width / 2
            else:
                x_position = building_width * (j + 1) / (window_count + 1) - window_width / 2
            
            # Create window
            window = create_window(model, owner_history, context,
                                  f"Front Window {i}-{j}",
                                  [x_position, 0, storey_elevation + sill_height],
                                  window_width, window_height)
            front_windows.append(window)
        
        # Create back windows
        back_windows = []
        for j in range(window_count):
            # Calculate window position
            if window_count == 1:
                x_position = building_width / 2 - window_width / 2
            else:
                x_position = building_width * (j + 1) / (window_count + 1) - window_width / 2
            
            # Create window
            window = create_window(model, owner_history, context,
                                  f"Back Window {i}-{j}",
                                  [x_position, building_depth, storey_elevation + sill_height],
                                  window_width, window_height)
            back_windows.append(window)
        
        # Relate windows to storey
        all_windows.extend(front_windows)
        all_windows.extend(back_windows)
        
        model.createIfcRelContainedInSpatialStructure(create_guid(), owner_history, 
                                                    f"Storey {i} Windows", None, 
                                                    front_windows + back_windows, storey)
    
    return all_windows

def create_stoop_extrusion(model, context, width, depth, height):
    """Create an extrusion for the stoop"""
    # Create profile for base
    points = [
        [0, 0],
        [width, 0],
        [width, depth],
        [0, depth],
        [0, 0]
    ]
    
    polyline = model.createIfcPolyline([model.createIfcCartesianPoint(point) for point in points])
    profile = model.createIfcArbitraryClosedProfileDef("AREA", None, polyline)
    
    # Create extrusion for base
    extrusion_direction = model.createIfcDirection([0.0, 0.0, 1.0])
    extrusion = model.createIfcExtrudedAreaSolid(profile,
                                              model.createIfcAxis2Placement3D(
                                                  model.createIfcCartesianPoint([0.0, 0.0, 0.0]),
                                                  model.createIfcDirection([0.0, 0.0, 1.0]),
                                                  model.createIfcDirection([1.0, 0.0, 0.0])
                                              ),
                                              extrusion_direction,
                                              height)
    
    # Create shape representation
    shape_representation = model.createIfcShapeRepresentation(context, "Body", "SweptSolid", [extrusion])
    
    # Create product definition shape
    product_definition_shape = model.createIfcProductDefinitionShape(None, None, [shape_representation])
    
    return product_definition_shape

def create_stoop(model, storeys, owner_history, context):
    """Create the front stoop typical of brownstones"""
    # Stoop dimensions
    stoop_width = convert_to_meter(12.0)
    stoop_depth = convert_to_meter(8.0)
    stoop_height = convert_to_meter(5.0)
    
    # Calculate building dimensions in meters
    building_width = convert_to_meter(BUILDING_WIDTH)
    building_depth = convert_to_meter(BUILDING_DEPTH)
    
    # Position stoop centered on the front of the building, at the first floor level
    stoop_position = [building_width/2 - stoop_width/2, -stoop_depth, 0]
    
    # Create stoop placement
    stoop_placement = model.createIfcLocalPlacement(None,
                                                 model.createIfcAxis2Placement3D(
                                                     model.createIfcCartesianPoint(stoop_position),
                                                     model.createIfcDirection([0.0, 0.0, 1.0]),
                                                     model.createIfcDirection([1.0, 0.0, 0.0])
                                                 ))
    
    # Create stoop shape representation
    extrusion = create_stoop_extrusion(model, context, stoop_width, stoop_depth, stoop_height)
    
    # Create stoop as a specialized stair
    stoop = model.createIfcStair(create_guid(), owner_history, "Front Stoop", 
                                "Brownstone front stoop", None,
                                stoop_placement, extrusion, None, "STRAIGHT")
    
    # Create stoop material
    stoop_material = model.createIfcMaterial("Brownstone")
    material_association = model.createIfcMaterialLayerSetUsage(
        model.createIfcMaterialLayerSet([model.createIfcMaterialLayer(stoop_material, 0.2, None)], None),
        "AXIS2", "POSITIVE", 0.0
    )
    
    # Associate material with stoop
    model.createIfcRelAssociatesMaterial(create_guid(), owner_history, None, None, [stoop], material_association)
    
    # Relate stoop to first floor storey
    model.createIfcRelContainedInSpatialStructure(create_guid(), owner_history, 
                                                "Stoop", None, [stoop], storeys[1])
    
    return stoop

def create_fixture_extrusion(model, context, width, depth, height):
    """Create an extrusion for a fixture"""
    # Create profile
    points = [
        [0, 0],
        [width, 0],
        [width, depth],
        [0, depth],
        [0, 0]
    ]
    
    polyline = model.createIfcPolyline([model.createIfcCartesianPoint(point) for point in points])
    profile = model.createIfcArbitraryClosedProfileDef("AREA", None, polyline)
    
    # Create extrusion
    extrusion_direction = model.createIfcDirection([0.0, 0.0, 1.0])
    extrusion = model.createIfcExtrudedAreaSolid(profile,
                                              model.createIfcAxis2Placement3D(
                                                  model.createIfcCartesianPoint([0.0, 0.0, 0.0]),
                                                  model.createIfcDirection([0.0, 0.0, 1.0]),
                                                  model.createIfcDirection([1.0, 0.0, 0.0])
                                              ),
                                              extrusion_direction,
                                              height)
    
    # Create shape representation
    shape_representation = model.createIfcShapeRepresentation(context, "Body", "SweptSolid", [extrusion])
    
    # Create product definition shape
    product_definition_shape = model.createIfcProductDefinitionShape(None, None, [shape_representation])
    
    return product_definition_shape

def create_fixture(model, owner_history, context, name, position, width, depth, height, fixture_type):
    """Create a sanitary fixture"""
    # Create fixture placement
    fixture_placement = model.createIfcLocalPlacement(None,
                                                   model.createIfcAxis2Placement3D(
                                                       model.createIfcCartesianPoint(position),
                                                       model.createIfcDirection([0.0, 0.0, 1.0]),
                                                       model.createIfcDirection([1.0, 0.0, 0.0])
                                                   ))
    
    # Create fixture shape representation
    extrusion = create_fixture_extrusion(model, context, width, depth, height)
    
    # Create fixture
    fixture = model.createIfcSanitaryTerminal(create_guid(), owner_history, name, 
                                           f"Sanitary fixture", None,
                                           fixture_placement, extrusion, None, fixture_type)
    
    # Create fixture material
    if fixture_type == "SINK":
        material_name = "Porcelain"
    else:
        material_name = "Ceramic"
    
    fixture_material = model.createIfcMaterial(material_name)
    material_association = model.createIfcMaterialLayerSetUsage(
        model.createIfcMaterialLayerSet([model.createIfcMaterialLayer(fixture_material, 0.05, None)], None),
        "AXIS2", "POSITIVE", 0.0
    )
    
    # Associate material with fixture
    model.createIfcRelAssociatesMaterial(create_guid(), owner_history, None, None, [fixture], material_association)
    
    return fixture

def create_fixtures(model, storeys, owner_history, context):
    """Create simplified fixtures in the brownstone"""
    all_fixtures = []
    
    # Kitchen fixtures on first floor
    building_width = convert_to_meter(BUILDING_WIDTH)
    building_depth = convert_to_meter(BUILDING_DEPTH)
    
    # Create kitchen sink
    sink_width = convert_to_meter(3.0)
    sink_depth = convert_to_meter(2.0)
    sink_height = convert_to_meter(0.5)
    
    sink_position = [building_width * 0.25, building_depth * 0.3, storeys[1].Elevation + convert_to_meter(3.0)]
    
    sink = create_fixture(model, owner_history, context,
                         "Kitchen Sink",
                         sink_position,
                         sink_width, sink_depth, sink_height,
                         "SINK")
    all_fixtures.append(sink)
    
    # Create bathroom fixtures on upper floors
    for i in range(2, 5):  # Floors 2-4
        storey = storeys[i]
        
        # Create toilet
        toilet_width = convert_to_meter(1.5)
        toilet_depth = convert_to_meter(2.0)
        toilet_height = convert_to_meter(1.0)
        
        toilet_position = [building_width * 0.75, building_depth * 0.25, storey.Elevation + convert_to_meter(0.0)]
        
        toilet = create_fixture(model, owner_history, context,
                              f"Toilet Floor {i}",
                              toilet_position,
                              toilet_width, toilet_depth, toilet_height,
                              "WCCISTERN")
        all_fixtures.append(toilet)
        
        # Create sink
        bath_sink_width = convert_to_meter(2.0)
        bath_sink_depth = convert_to_meter(1.5)
        bath_sink_height = convert_to_meter(0.5)
        
        bath_sink_position = [building_width * 0.75, building_depth * 0.35, storey.Elevation + convert_to_meter(3.0)]
        
        bath_sink = create_fixture(model, owner_history, context,
                                 f"Bathroom Sink Floor {i}",
                                 bath_sink_position,
                                 bath_sink_width, bath_sink_depth, bath_sink_height,
                                 "SINK")
        all_fixtures.append(bath_sink)
        
        # Relate fixtures to their storeys
        model.createIfcRelContainedInSpatialStructure(create_guid(), owner_history, 
                                                    f"Storey {i} Fixtures", None,
                                                    [toilet, bath_sink], storey)
    
    # Relate kitchen fixtures to first floor
    model.createIfcRelContainedInSpatialStructure(create_guid(), owner_history, 
                                                "Kitchen Fixtures", None, [sink], storeys[1])
    
    return all_fixtures

def create_mep_element(model, owner_history, context, name, position, width, depth, height, element_type):
    """Create an MEP element"""
    # Create element placement
    element_placement = model.createIfcLocalPlacement(None,
                                                    model.createIfcAxis2Placement3D(
                                                        model.createIfcCartesianPoint(position),
                                                        model.createIfcDirection([0.0, 0.0, 1.0]),
                                                        model.createIfcDirection([1.0, 0.0, 0.0])
                                                    ))
    
    # Create element shape representation
    extrusion = create_fixture_extrusion(model, context, width, depth, height)  # Reuse fixture extrusion function
    
    # Create element based on type
    if element_type == "AIRHANDLER":
        element = model.createIfcUnitaryEquipment(create_guid(), owner_history, name, 
                                                "HVAC equipment", None,
                                                element_placement, extrusion, None, element_type)
    elif element_type == "SWITCHBOARD":
        element = model.createIfcElectricDistributionBoard(create_guid(), owner_history, name, 
                                                         "Electrical equipment", None,
                                                         element_placement, extrusion, None, element_type)
    elif element_type == "WATERHEATER":
        element = model.createIfcFlowTerminal(create_guid(), owner_history, name, 
                                            "Plumbing equipment", None,
                                            element_placement, extrusion, None, None)
    
    # Create element material
    element_material = model.createIfcMaterial("Metal")
    material_association = model.createIfcMaterialLayerSetUsage(
        model.createIfcMaterialLayerSet([model.createIfcMaterialLayer(element_material, 0.05, None)], None),
        "AXIS2", "POSITIVE", 0.0
    )
    
    # Associate material with element
    model.createIfcRelAssociatesMaterial(create_guid(), owner_history, None, None, [element], material_association)
    
    return element

def create_mep_elements(model, storeys, owner_history, context):
    """Create simplified MEP elements in the brownstone"""
    all_mep_elements = []
    
    # Building dimensions
    building_width = convert_to_meter(BUILDING_WIDTH)
    building_depth = convert_to_meter(BUILDING_DEPTH)
    
    # Create HVAC system in basement
    hvac_width = convert_to_meter(6.0)
    hvac_depth = convert_to_meter(4.0)
    hvac_height = convert_to_meter(2.0)
    
    hvac_position = [building_width * 0.2, building_depth * 0.2, storeys[0].Elevation + convert_to_meter(1.0)]
    
    hvac_unit = create_mep_element(model, owner_history, context,
                                 "HVAC System",
                                 hvac_position,
                                 hvac_width, hvac_depth, hvac_height,
                                 "AIRHANDLER")
    all_mep_elements.append(hvac_unit)
    
    # Create electrical panel in basement
    panel_width = convert_to_meter(2.0)
    panel_depth = convert_to_meter(0.5)
    panel_height = convert_to_meter(3.0)
    
    panel_position = [building_width * 0.8, building_depth * 0.1, storeys[0].Elevation + convert_to_meter(1.0)]
    
    electrical_panel = create_mep_element(model, owner_history, context,
                                        "Electrical Panel",
                                        panel_position,
                                        panel_width, panel_depth, panel_height,
                                        "SWITCHBOARD")
    all_mep_elements.append(electrical_panel)
    
    # Create water heater in basement
    water_heater_width = convert_to_meter(2.0)
    water_heater_depth = convert_to_meter(2.0)
    water_heater_height = convert_to_meter(2.0)
    
    water_heater_position = [building_width * 0.5, building_depth * 0.1, storeys[0].Elevation + convert_to_meter(1.0)]
    
    water_heater = create_mep_element(model, owner_history, context,
                                    "Water Heater",
                                    water_heater_position,
                                    water_heater_width, water_heater_depth, water_heater_height,
                                    "WATERHEATER")
    all_mep_elements.append(water_heater)
    
    # Relate MEP elements to basement
    model.createIfcRelContainedInSpatialStructure(create_guid(), owner_history, 
                                                "MEP Systems", None,
                                                [hvac_unit, electrical_panel, water_heater], storeys[0])
    
    return all_mep_elements

def create_brownstone_ifc(output_file="new_york_brownstone.ifc"):
    """Main function to create the complete brownstone IFC model"""
    print("Creating New York Brownstone IFC model...")
    
    # Create the IFC model
    model, project, owner_history, context = create_ifc_model()
    
    # Create site
    site = create_site(model, project, owner_history)
    
    # Create building
    building = create_building(model, site, owner_history)
    
    # Create storeys (including roof level)
    storeys = create_storeys(model, building, owner_history)
    
    # Create walls
    walls = create_walls(model, storeys, owner_history, context)
    print(f"Created {len(walls)} walls")
    
    # Create slabs (floors and roof)
    slabs = create_slabs(model, storeys, owner_history, context)
    print(f"Created {len(slabs)} slabs")
    
    # Create windows
    windows = create_windows(model, storeys, owner_history, context)
    print(f"Created {len(windows)} windows")
    
    # Create doors
    doors = create_doors(model, storeys, owner_history, context)
    print(f"Created {len(doors)} doors")
    
    # Create front stoop
    stoop = create_stoop(model, storeys, owner_history, context)
    print("Created front stoop")
    
    # Create fixtures (sinks, toilets, etc.)
    fixtures = create_fixtures(model, storeys, owner_history, context)
    print(f"Created {len(fixtures)} fixtures")
    
    # Create MEP elements
    mep_elements = create_mep_elements(model, storeys, owner_history, context)
    print(f"Created {len(mep_elements)} MEP elements")
    
    # Write the model to a file
    model.write(output_file)
    print(f"IFC model written to {output_file}")
    
    return output_file

if __name__ == "__main__":
    # Check if ifcopenshell is installed
    try:
        import ifcopenshell
        print("IfcOpenShell is installed. Creating IFC model...")
        
        # Create the brownstone IFC model
        ifc_file = create_brownstone_ifc()
        print(f"Successfully created brownstone IFC model: {ifc_file}")
        
    except ImportError:
        print("IfcOpenShell is not installed. Please install it using:")
        print("pip install ifcopenshell")
        print("or visit: https://ifcopenshell.org/")
        print("for more information.")
        sys.exit(1)
    except Exception as e:  
        print(f"An error occurred: {e}")
        sys.exit(1)
