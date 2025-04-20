# New York Brownstone IFC Implementation Guide

## Introduction

This guide provides instructions for implementing the New York brownstone design as a proper Industry Foundation Classes (IFC) model using professional Building Information Modeling (BIM) software. While the IFC structure representation provided earlier demonstrates the conceptual organization, this guide will help professionals develop a complete, functional IFC file.

## 1. Software Selection

### 1.1 Recommended BIM Platforms
For optimal IFC creation and export, consider using one of these professional BIM platforms:

- **Autodesk Revit**: Provides robust IFC export capabilities with extensive customization options
- **ArchiCAD**: Offers native IFC support with strong architectural modeling features
- **Vectorworks Architect**: Good IFC compatibility with strong design-oriented workflow
- **Bentley AECOsim Building Designer**: Advanced modeling with comprehensive IFC support
- **Nemetschek Allplan**: Strong in structural modeling with reliable IFC implementation

### 1.2 IFC Version Selection
- Implement using **IFC4** or newer for maximum feature support
- Ensure software is configured to use the correct schema version
- Consider using the IFC4 Design Transfer View or Reference View as appropriate

## 2. Project Setup

### 2.1 Project Coordinates
- Set project coordinates to match actual site location in New York City
- Establish the 0,0,0 point at the southwest corner of the property
- Set project north to true north
- Define elevation 0.0 at street level

### 2.2 Units Configuration
- Use Imperial units (feet and inches) for modeling
- Configure IFC export to use metric units (meters) for maximum compatibility
- Ensure angle measurements are set to degrees

### 2.3 Project Organization
- Create a logical structure of building stories as defined in specifications
- Set up proper story heights with adequate offsets for floor assemblies
- Define discipline-specific worksets or layers (architectural, structural, MEP)
- Establish naming conventions that will translate properly to IFC

## 3. Building Elements Modeling

### 3.1 Architectural Elements

#### 3.1.1 Walls
- Model exterior walls with correct brownstone cladding, brick backing, and interior finishes
- Include proper wall construction layers (exterior material, structure, insulation, interior finish)
- Use specific IFC wall types:
  - `IfcWallStandardCase` for standard walls
  - `IfcWall` for complex geometries

#### 3.1.2 Floors/Slabs
- Model each floor system with accurate thickness and material layers
- Include structural elements, sound isolation, and finish materials
- Properly model transitions between different floor types
- For IFC export, use `IfcSlab` with appropriate predefined type

#### 3.1.3 Roofs
- Model the parapet and cornice as separate elements from the main roof structure
- Include roof drain systems and mechanical penetrations
- For roof surfaces, use `IfcRoof` with component `IfcRoofSlab` elements

#### 3.1.4 Stairs
- Model full stair geometry including stringers, treads, risers, and railings
- Include the front stoop as a specialized stair element
- For IFC export, use `IfcStair` with component elements

#### 3.1.5 Windows and Doors
- Create detailed window models with frame, glazing, and hardware components
- Use parametric door families with proper swing directions and clearances
- Include transoms and side lites as part of door assemblies
- Apply proper IFC types:
  - `IfcWindow` with appropriate parameters
  - `IfcDoor` with detailed property sets

### 3.2 Structural Elements

#### 3.2.1 Foundations
- Model foundation walls and footings with proper dimensions
- Include waterproofing and drainage systems
- Apply `IfcFooting` and `IfcSlab` as appropriate

#### 3.2.2 Structural Framing
- Model steel beams and columns with proper profiles and connections
- Include wood/steel joists and subfloor systems
- For IFC export, use:
  - `IfcBeam` for horizontal framing
  - `IfcColumn` for vertical supports
  - `IfcMember` for other framing elements

### 3.3 MEP Systems

#### 3.3.1 HVAC
- Model ductwork with proper dimensions and connections
- Include diffusers, returns, and mechanical equipment
- Model hydronic piping systems for radiant heating
- For IFC export, use:
  - `IfcDuctSegment` for ducts
  - `IfcAirTerminal` for diffusers
  - `IfcPipeSegment` for pipes
  - `IfcUnitaryEquipment` for HVAC equipment

#### 3.3.2 Plumbing
- Model supply and drainage piping systems
- Include fixtures with proper connections
- For IFC export, use:
  - `IfcPipeSegment` for pipes
  - `IfcFlowFitting` for fittings
  - `IfcSanitaryTerminal` for fixtures

#### 3.3.3 Electrical
- Model conduit and cable tray routing for major systems
- Place fixtures, outlets, and switches with proper clearances
- Include panel boards and service equipment
- For IFC export, use:
  - `IfcCableCarrierSegment` for conduit/trays
  - `IfcLightFixture` for lighting
  - `IfcElectricAppliance` for devices
  - `IfcElectricDistributionBoard` for panels

## 4. Property Sets and Parameters

### 4.1 Common Property Sets
- Apply standard IFC property sets to all elements:
  - `Pset_BuildingCommon` for building-level data
  - `Pset_WallCommon` for walls
  - `Pset_SlabCommon` for floors
  - `Pset_WindowCommon` for windows
  - etc.

### 4.2 Custom Property Sets
- Create brownstone-specific property sets for historic elements:
  - `Pset_BrownstoneExterior` with parameters for material, color, finish
  - `Pset_HistoricElement` with parameters for age, restoration details, preservation requirements
  - `Pset_MEPSystemPerformance` with parameters for system ratings and capacities

### 4.3 IFC Parameters
- Include necessary IFC parameters on all elements:
  - Name
  - Description
  - Tag/Mark
  - Fire rating
  - Acoustic rating
  - Load bearing (true/false)
  - Exterior (true/false)

## 5. Spatial Organization

### 5.1 Spaces/Rooms
- Create space objects for all rooms with proper boundaries
- Include ceiling height and finish parameters
- For IFC export, use `IfcSpace` with appropriate property sets

### 5.2 Zones
- Create functional zones grouping related spaces:
  - Public areas
  - Private areas
  - Service areas
  - Mechanical zones
- For IFC export, use `IfcZone` referencing the appropriate spaces

### 5.3 Building Storeys
- Properly define each level as a building storey
- Include elevation parameters and height relationships
- For IFC export, use `IfcBuildingStorey`

## 6. Relationships and Connections

### 6.1 Element Relationships
- Establish proper hosting relationships between elements
- Define wall-to-floor connections correctly
- Ensure beam-to-column relationships are modeled properly
- Use appropriate IFC relationship entities:
  - `IfcRelAggregates`
  - `IfcRelContainedInSpatialStructure`
  - `IfcRelConnectsElements`

### 6.2 System Connections
- Model proper connections between MEP system components
- Ensure connectivity of duct and pipe networks
- Define electrical circuit connections
- Use appropriate IFC connection entities:
  - `IfcRelConnectsPortToElement`
  - `IfcRelConnectsPorts`
  - `IfcRelFlowControlElements`

## 7. IFC Export Configuration

### 7.1 General Export Settings
- Set IFC schema version to IFC4
- Configure coordination view or design transfer view as appropriate
- Enable property set export
- Set up correct unit conversion

### 7.2 Element Filtering
- Configure which elements are included in export
- Set up filtering for temporary elements or construction aids
- Configure visibility of internal component geometry

### 7.3 Property Mapping
- Map custom parameters to IFC property sets
- Configure classification system mapping (e.g., Uniformat, Masterformat)
- Set up material property mapping

## 8. Quality Control and Validation

### 8.1 Model Checking
Before export, verify:
- No unconnected elements
- No significant geometric intersections
- All required parameters populated
- Proper spatial containment

### 8.2 IFC Validation
After export, validate using:
- Solibri Model Checker
- IFC validation utilities (e.g., IfcDoc)
- Visual inspection in IFC viewers (e.g., BIMvision, Solibri Anywhere)

### 8.3 Common Issues to Check
- Proper geometric representation
- Correct property set data
- Spatial containment hierarchy
- Material assignments
- Type classifications

## 9. Implementation Workflow

### 9.1 Recommended Process
1. Create architectural model with primary elements
2. Add structural elements and verify coordination
3. Integrate MEP systems and resolve conflicts
4. Apply properties and parameters
5. Validate internal model
6. Export to IFC
7. Validate IFC model
8. Revise as needed

### 9.2 Special Considerations for Historic Elements
- Use specialized modeling techniques for ornate details:
  - Cornice and molding profiles
  - Decorative ironwork
  - Carved brownstone features
- Balance detail level with file performance
- Use proxy elements with detailed geometry when appropriate

## 10. Software-Specific Instructions

### 10.1 Autodesk Revit
- Use the IFC Export Settings dialog to customize export
- Apply IFC Export mapping tables for custom parameter mapping
- Consider using the "IFC" tab in element properties for direct IFC parameter assignment
- Install the latest IFC export plugin from Autodesk

### 10.2 ArchiCAD
- Use the dedicated IFC Manager for mapping and configuration
- Apply IFC properties directly through the IFC Manager
- Configure proper translator settings for export
- Utilize ArchiCAD's native IFC connection management

### 10.3 Vectorworks
- Use the IFC Export Settings dialog for configuration
- Apply IFC data to objects through the Object Info palette
- Configure data mapping in the workspace settings
- Use space objects for proper room definition

### 10.4 Other Software
- Follow vendor-specific recommendations for IFC implementation
- Check for updated IFC export plugins or modules
- Verify compliance with IFC4 standard

By following this implementation guide, professionals can create a complete, standards-compliant IFC model of the New York brownstone design that will facilitate collaboration across disciplines and support accurate construction documentation.
