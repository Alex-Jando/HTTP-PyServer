import re

class TemplateError(Exception):
    '''Raised when there is an error whilst rendering a template.'''

    pass

def _template(data: str,
             **templated_values: dict) -> str:
    '''Returns the contents of a template file with the templated variables'''
    
    if not templated_values:
        
        templated_values = {}

    template_spots = re.findall(r'{{.*?}}',
                                data,
                                re.DOTALL)
    
    for template_spot in template_spots:

        template_spot_indented = \
'\n    '.join([line for line in template_spot.split('\n')])
        
        output = {}

        try:

            exec(f'''def template_item():
    {template_spot_indented.strip('{}')}
output= template_item()''', templated_values, output)
            
        except Exception as e:

            raise TemplateError(f'''Error in template:

{template_spot}

{e}''')
        
        data = data.replace(template_spot, str(output['output']))

    return data