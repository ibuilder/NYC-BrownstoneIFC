"""
Brownstone IFC Viewer

This script provides a simple way to visualize the IFC model of the brownstone
using IfcOpenShell and PyVista for 3D visualization.

Requirements:
- ifcopenshell
- pyvista
- numpy

Installation:
pip install ifcopenshell pyvista numpy

Note: On some systems, you may need to install ifcopenshell from its GitHub repository.
"""

import ifcopenshell
import ifcopenshell.geom
import numpy as np
import pyvista as pv
import sys
import os
import argparse

def setup_style():
    """Set up visualization style"""
    # Create a custom color map for different IFC entities
    colors = {
        'IfcWallStandardCase': [0.8, 0.7, 0.6],  # Brownstone color
        'IfcWall': [0.8, 0.7, 0.6],
        'IfcSlab': [0.7, 0.7, 0.7],  # Grey for floors
        'IfcWindow': [0.3, 0.5, 0.8, 0.3],  # Translucent blue for windows
        'IfcDoor': [0.6, 0.3, 0.1],  # Brown for doors
        'IfcStair': [0.8, 0.6, 0.5],  # Stoop color (similar to brownstone)
        'IfcSanitaryTerminal': [0.9, 0.9, 0.9],  # White for fixtures
        'IfcUnitaryEquipment': [0.5, 0.5, 0.5],  # Grey for HVAC
        'IfcElectricDistributionBoard': [0.2, 0.2, 0.2],  # Dark grey for electrical
        'IfcFlowTerminal': [0.4, 0.4, 0.7],  # Bluish for plumbing
        'default': [0.7, 0.7, 0.7]  # Default grey
    }
    
    return colors

def create_entity_mesh(settings, entity, colors):
    """Create a mesh for a single IFC entity"""
    # Get shape data
    shape = ifcopenshell.geom.create_shape(settings, entity)
    
    # Extract geometry data
    verts = shape.geometry.verts
    faces = shape.geometry.faces
    
    # Reshape vertices and faces
    vertices = np.array(verts).reshape(-1, 3)
    faces_count = len(faces) // 3
    faces_array = np.array(faces).reshape(faces_count, 3)
    
    # Create face arrays with count of vertices per face (always 3 for triangles)
    faces_with_count = np.column_stack((np.ones(faces_count, dtype=np.int8) * 3, faces_array))
    faces_with_count = faces_with_count.flatten()
    
    # Create mesh
    mesh = pv.PolyData(vertices, faces_with_count)
    
    # Assign color based on entity type
    entity_type = entity.is_a()
    if entity_type in colors:
        color = colors[entity_type]
    else:
        color = colors['default']
    
    # Add color information
    if len(color) == 3:
        mesh['color'] = color
        mesh['opacity'] = 1.0
    else:
        mesh['color'] = color[:3]
        mesh['opacity'] = color[3]
    
    return mesh, entity_type

def visualize_ifc(ifc_file):
    """Visualize an IFC file using PyVista"""
    print(f"Loading IFC file: {ifc_file}")
    
    # Load the IFC file
    model = ifcopenshell.open(ifc_file)
    
    # Set up visualization style
    colors = setup_style()
    
    # Set up the IFC geometry settings
    settings = ifcopenshell.geom.settings()
    settings.set(settings.USE_WORLD_COORDS, True)
    
    # Create the PyVista plotter
    plotter = pv.Plotter()
    plotter.set_background('white')
    
    # Entity types to visualize
    entity_types = [
        'IfcWallStandardCase', 'IfcWall', 'IfcSlab', 'IfcWindow', 'IfcDoor',
        'IfcStair', 'IfcSanitaryTerminal', 'IfcUnitaryEquipment',
        'IfcElectricDistributionBoard', 'IfcFlowTerminal'
    ]
    
    # Process entities in groups to show progress
    entity_count = 0
    meshes_by_type = {}
    
    # Initialize counts by type
    for entity_type in entity_types:
        meshes_by_type[entity_type] = []
    
    # Process all entities of the specified types
    for entity_type in entity_types:
        entities = model.by_type(entity_type)
        print(f"Processing {len(entities)} {entity_type} entities...")
        
        for entity in entities:
            try:
                mesh, actual_type = create_entity_mesh(settings, entity, colors)
                meshes_by_type[actual_type].append(mesh)
                entity_count += 1
            except RuntimeError as e:
                print(f"Error processing {entity_type} entity: {e}")
    
    # Add meshes to plotter by type
    for entity_type, meshes in meshes_by_type.items():
        if meshes:
            print(f"Adding {len(meshes)} {entity_type} entities to visualization")
            combined_mesh = meshes[0]
            if len(meshes) > 1:
                for mesh in meshes[1:]:
                    combined_mesh = combined_mesh.merge(mesh)
            
            # Get color from the first mesh
            color = meshes[0]['color']
            opacity = meshes[0]['opacity']
            
            # Add to plotter
            plotter.add_mesh(combined_mesh, color=color, opacity=opacity, show_edges=False)
    
    print(f"Visualization complete with {entity_count} entities")
    
    # Set up a nice initial view
    plotter.view_isometric()
    plotter.camera.elevation = 20
    plotter.camera.azimuth = 225
    
    # Add a title
    plotter.add_title("New York Brownstone IFC Model", font_size=16)
    
    # Add a legend
    labels = [entity_type.replace('Ifc', '') for entity_type in meshes_by_type if meshes_by_type[entity_type]]
    colors_list = [colors[entity_type] if len(colors[entity_type]) == 3 else colors[entity_type][:3] 
                  for entity_type in meshes_by_type if meshes_by_type[entity_type]]
    
    if labels and colors_list:
        plotter.add_legend(labels, colors_list, size=(0.15, 0.15), loc='upper right')
    
    # Start the visualization
    plotter.show()

def main():
    """Main function to parse arguments and start visualization"""
    parser = argparse.ArgumentParser(description='Visualize a brownstone IFC model')
    parser.add_argument('ifc_file', type=str, nargs='?', default='new_york_brownstone.ifc',
                       help='Path to the IFC file to visualize')
    args = parser.parse_args()
    
    # Check if the file exists
    if not os.path.exists(args.ifc_file):
        print(f"Error: IFC file '{args.ifc_file}' does not exist")
        return 1
    
    # Visualize the IFC file
    visualize_ifc(args.ifc_file)
    return 0

if __name__ == "__main__":
    sys.exit(main())
