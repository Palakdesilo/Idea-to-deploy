import os
import json
import sys
from typing import Dict, List, Any

def load_layout_plan(filepath: str) -> Dict[str, Any]:
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def create_rectangle_node(component_key: str, x: float, y: float) -> Dict[str, Any]:
    return {
        'type': 'RECTANGLE',
        'name': component_key,
        'x': x,
        'y': y,
        'width': 200,
        'height': 50,
        'fills': [{'type': 'SOLID', 'color': {'r': 0.9, 'g': 0.9, 'b': 0.9, 'a': 1}}],
        'strokes': [],
        'strokeWeight': 0
    }

def create_section_frame(section_name: str, components: List[Dict[str, Any]], y_offset: float) -> Dict[str, Any]:
    children = []
    current_y = 20
    
    for component in components:
        component_key = component.get('key', 'Component')
        rect = create_rectangle_node(component_key, 20, current_y)
        children.append(rect)
        current_y += 70
    
    return {
        'type': 'FRAME',
        'name': section_name,
        'x': 0,
        'y': y_offset,
        'width': 240,
        'height': max(current_y + 20, 100),
        'children': children,
        'fills': [{'type': 'SOLID', 'color': {'r': 0.98, 'g': 0.98, 'b': 0.98, 'a': 1}}],
        'strokes': [{'type': 'SOLID', 'color': {'r': 0.8, 'g': 0.8, 'b': 0.8, 'a': 1}}],
        'strokeWeight': 1,
        'cornerRadius': 4
    }

def create_frame_node(frame_data: Dict[str, Any]) -> Dict[str, Any]:
    name = frame_data.get('name', 'Frame')
    description = frame_data.get('description', '')
    layout_type = frame_data.get('layoutType', 'fullPage')
    sections = frame_data.get('sections', [])
    
    children = []
    current_y = 0
    
    if layout_type == 'twoColumn':
        left_sections = []
        right_sections = []
        
        for section in sections:
            section_name = section.get('name', '')
            if section_name in ['Sidebar', 'Order Summary']:
                right_sections.append(section)
            else:
                left_sections.append(section)
        
        left_y = 0
        for section in left_sections:
            section_frame = create_section_frame(section.get('name', 'Section'), section.get('components', []), left_y)
            section_frame['x'] = 20
            children.append(section_frame)
            left_y += section_frame['height'] + 20
        
        right_y = 0
        for section in right_sections:
            section_frame = create_section_frame(section.get('name', 'Section'), section.get('components', []), right_y)
            section_frame['x'] = 280
            children.append(section_frame)
            right_y += section_frame['height'] + 20
    
    elif layout_type == 'dashboardShell':
        sidebar_sections = []
        main_sections = []
        header_sections = []
        footer_sections = []
        
        for section in sections:
            section_name = section.get('name', '')
            if section_name == 'Sidebar':
                sidebar_sections.append(section)
            elif section_name == 'Header':
                header_sections.append(section)
            elif section_name == 'Footer':
                footer_sections.append(section)
            else:
                main_sections.append(section)
        
        header_y = 0
        for section in header_sections:
            section_frame = create_section_frame(section.get('name', 'Section'), section.get('components', []), header_y)
            section_frame['x'] = 20
            section_frame['width'] = 760
            children.append(section_frame)
            header_y += section_frame['height'] + 20
        
        sidebar_y = header_y
        for section in sidebar_sections:
            section_frame = create_section_frame(section.get('name', 'Section'), section.get('components', []), sidebar_y)
            section_frame['x'] = 20
            children.append(section_frame)
            sidebar_y += section_frame['height'] + 20
        
        main_y = header_y
        for section in main_sections:
            section_frame = create_section_frame(section.get('name', 'Section'), section.get('components', []), main_y)
            section_frame['x'] = 280
            section_frame['width'] = 500
            children.append(section_frame)
            main_y += section_frame['height'] + 20
        
        footer_y = max(sidebar_y, main_y)
        for section in footer_sections:
            section_frame = create_section_frame(section.get('name', 'Section'), section.get('components', []), footer_y)
            section_frame['x'] = 20
            section_frame['width'] = 760
            children.append(section_frame)
            footer_y += section_frame['height'] + 20
    
    elif layout_type == 'centeredForm':
        for section in sections:
            section_frame = create_section_frame(section.get('name', 'Section'), section.get('components', []), current_y)
            section_frame['x'] = 200
            children.append(section_frame)
            current_y += section_frame['height'] + 20
    
    else:
        for section in sections:
            section_frame = create_section_frame(section.get('name', 'Section'), section.get('components', []), current_y)
            section_frame['x'] = 20
            section_frame['width'] = 760
            children.append(section_frame)
            current_y += section_frame['height'] + 20
    
    return {
        'type': 'FRAME',
        'name': name,
        'description': description,
        'x': 0,
        'y': 0,
        'width': 800,
        'height': 600,
        'children': children,
        'fills': [{'type': 'SOLID', 'color': {'r': 1, 'g': 1, 'b': 1, 'a': 1}}],
        'strokes': [{'type': 'SOLID', 'color': {'r': 0.7, 'g': 0.7, 'b': 0.7, 'a': 1}}],
        'strokeWeight': 2,
        'cornerRadius': 8
    }

def generate_figma_nodes(layout_plan: Dict[str, Any]) -> Dict[str, Any]:
    pages = []
    
    for page_data in layout_plan.get('figma', {}).get('pages', []):
        page_name = page_data.get('name', 'Wireframes')
        frames = page_data.get('frames', [])
        frame_nodes = []
        
        for idx, frame_data in enumerate(frames):
            frame_node = create_frame_node(frame_data)
            frame_node['x'] = (idx % 5) * 850
            frame_node['y'] = (idx // 5) * 650
            frame_nodes.append(frame_node)
        
        pages.append({
            'name': page_name,
            'frames': frame_nodes
        })
    
    return {'pages': pages}

def main():
    try:
        layout_plan = load_layout_plan('docs/figma_layout.json')
        figma_nodes = generate_figma_nodes(layout_plan)
        
        output_file = 'docs/figma_nodes_output.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(figma_nodes, f, indent=2)
        
        print(f"[OK] Successfully generated Figma nodes")
        print(f"[OK] Output saved to: {output_file}")
        print(f"[OK] Total frames generated: {sum(len(page['frames']) for page in figma_nodes['pages'])}")
        print(f"\nNote: The Figma REST API does not support direct node creation.")
        print(f"Use the generated JSON with a Figma plugin or import tool.")
        
        return 0
    except FileNotFoundError:
        print("Error: figma_layout.json not found in current directory")
        return 1
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
