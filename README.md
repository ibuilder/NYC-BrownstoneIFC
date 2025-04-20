# New York Brownstone IFC Model Generator

This package provides Python scripts to generate and visualize a 3D model of a New York brownstone building in Industry Foundation Classes (IFC) format. The model is based on detailed architectural specifications for a brownstone on a 50'×100' lot.

## Contents

1. **brownstone-ifc-generator.py**: Python script to generate the IFC model
2. **brownstone-ifc-viewer.py**: Python script to visualize the generated IFC model
3. **Documentation**: Detailed specifications for the brownstone design

## Requirements

The scripts require the following Python packages:

- **ifcopenshell**: For IFC file creation and manipulation
- **numpy**: For numerical operations
- **pyvista**: For 3D visualization (viewer script only)

## Installation

1. Install Python 3.7 or newer
2. Install the required packages:

```bash
pip install numpy pyvista
```

3. Install IfcOpenShell:

The installation of IfcOpenShell depends on your operating system. You can find the latest instructions at [ifcopenshell.org](https://ifcopenshell.org/). Some common methods include:

- **PyPI (if available for your platform):**
```bash
pip install ifcopenshell
```

- **From source:**
```bash
git clone https://github.com/IfcOpenShell/IfcOpenShell.git
cd IfcOpenShell
# Follow platform-specific build instructions
```

## Usage

### Generating the IFC Model

Run the generator script to create an IFC file of the brownstone:

```bash
python brownstone-ifc-generator.py
```

This will create a file called `new_york_brownstone.ifc` in the current directory.

### Visualizing the IFC Model

After generating the IFC file, you can visualize it using the viewer script:

```bash
python brownstone-ifc-viewer.py [path_to_ifc_file]
```

If you don't specify a file path, it will look for `new_york_brownstone.ifc` in the current directory.

The viewer provides an interactive 3D visualization where you can:
- Rotate, pan, and zoom the model
- See different elements color-coded by type
- Explore the overall structure of the brownstone

## Model Details

The generated brownstone model includes:

- **Structure**:
  - 5 floors (basement + 4 floors)
  - Approximately 16,000 sq ft of space
  - Traditional brownstone facade

- **Elements**:
  - Exterior walls with brownstone facade
  - Interior walls defining room layouts
  - Floors and roof slabs
  - Front stoop (traditional brownstone entry stair)
  - Windows and doors
  - Basic plumbing fixtures (sinks, toilets)
  - Basic MEP elements (HVAC, electrical panel, water heater)

## Customization

You can modify the brownstone model by editing the parameters at the top of the `brownstone-ifc-generator.py` file:

```python
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
```

You can also customize the model by modifying the individual functions that create different building elements.

## Using in BIM Software

The generated IFC file can be imported into most BIM (Building Information Modeling) software, including:

- Autodesk Revit
- ArchiCAD
- Vectorworks
- BIM Vision
- Solibri
- Navisworks

Note that this model is a simplified representation. For a professional-grade BIM model, you would typically want to use dedicated BIM software to create more detailed geometry and add comprehensive metadata.

## Limitations

This generator creates a simplified model with:

- Basic geometric representations of building elements
- Limited material definitions
- Simplified MEP systems
- No detailed architectural features (moldings, decorative elements)
- No furniture or fixtures beyond basic plumbing elements

For a production-quality IFC model, consider using this as a starting point and enhancing it with professional BIM software.

## Advanced Usage

### Adding More Detail

You can extend the model by adding functions to create additional elements:

1. Furniture
2. Light fixtures
3. HVAC distribution
4. Plumbing distribution
5. Electrical distribution
6. Detailed architectural features

Follow the pattern of existing functions in the generator script, creating appropriate IFC entities for each new element type.

### Exporting to Other Formats

To convert the IFC file to other 3D formats (OBJ, STL, STEP, etc.), you can use tools like:

- IfcConvert (part of the IfcOpenShell toolkit)
- Blender with IFC import plugins
- BIMserver

Example using IfcConvert:

```bash
ifcconvert new_york_brownstone.ifc new_york_brownstone.obj
```

## Troubleshooting

### Common Issues

1. **ImportError: No module named ifcopenshell**
   - Ensure IfcOpenShell is correctly installed for your platform
   - Try installing from the official website if pip installation fails

2. **Visualization shows no geometry**
   - Check if the IFC file was generated correctly
   - Verify PyVista is properly installed with all dependencies

3. **Memory errors during generation**
   - Reduce the level of detail in the model
   - Run the script on a machine with more RAM

## Credits

This brownstone IFC generator is based on detailed architectural specifications for a traditional New York brownstone. It uses:

- IfcOpenShell: An open-source software library for working with IFC files
- PyVista: A Python library for 3D visualization
- NumPy: A Python library for numerical operations

## License

This code is provided under the MIT License. Feel free to use, modify, and distribute it as needed.

## Contributing

Contributions to improve the model generator are welcome. Please feel free to fork the repository, make improvements, and submit pull requests.

Potential areas for enhancement:
- More detailed architectural elements
- Better material definitions
- More sophisticated MEP systems
- Improved visualization options
- Additional building types