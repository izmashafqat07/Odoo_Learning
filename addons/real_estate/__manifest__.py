# /home/$USER/src/tutorials/estate/__manifest__.py
{
    "name": "Estate",
    "summary": "Real estate advertisements (tutorial module)",
    "author": "Your Name",
    "license": "LGPL-3",
    "depends": ["base"], 
    "data": [
        "security/ir.model.access.csv",
        "views/estate_property_views.xml",
    ],         # Only the base framework for now
    "application": True,          # <- This makes it show up under the 'Apps' filter
    "installable": True,
    
}
