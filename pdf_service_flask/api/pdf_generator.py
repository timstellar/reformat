import os
import jinja2
from weasyprint import HTML
from typing import Dict, Any

# Setup Jinja2 environment
template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_dir),
    autoescape=jinja2.select_autoescape(['html', 'xml'])
)

def generate_pdf(template_name: str, data: Dict[str, Any], output_path: str) -> str:
    """
    Generate a PDF document from a template and data.
    
    Args:
        template_name: Name of the template file (without extension)
        data: Dictionary containing the data to be rendered in the template
        output_path: Path where the generated PDF will be saved
    
    Returns:
        Path to the generated PDF file
    """
    try:
        # Get the template
        template = jinja_env.get_template(f"{template_name}.html")
        
        # Render the template with the provided data
        html_content = template.render(**data)
        
        # Create a temporary HTML file
        temp_html_path = output_path.replace('.pdf', '.html')
        with open(temp_html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Generate PDF from HTML
        HTML(string=html_content).write_pdf(output_path)
        
        # Remove temporary HTML file
        if os.path.exists(temp_html_path):
            os.remove(temp_html_path)
        
        return output_path
    
    except jinja2.exceptions.TemplateNotFound:
        raise Exception(f"Template '{template_name}' not found")
    
    except Exception as e:
        raise Exception(f"Error generating PDF: {str(e)}")
