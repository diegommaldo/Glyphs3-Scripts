# MenuTitle: Stylistic Set Generator
# -*- coding: utf-8 -*-
__doc__="""
Creates an OpenType Stylistic Set Feature based on user input for the glyph name suffix and SS number. Optionally overrides an existing stylistic set feature if one already exists.

Created by Chat GPT & Diego Maldonado
https://www.diegomaldonado.com.br
"""

import GlyphsApp
import vanilla

class StylisticSetCreator(object):
    def __init__(self):
        # Create the window
        self.w = vanilla.Window((300, 160), "Stylistic Set Generator")
        
        # Add text boxes and inputs
        self.w.suffixText = vanilla.TextBox((15, 15, 130, 20), "Glyphs Name Suffix")
        self.w.suffixInput = vanilla.EditText((150, 12, 130, 25), "")  # Default to empty
        
        self.w.ssNumberText = vanilla.TextBox((15, 45, 130, 20), "Stylistic Set Number")
        self.w.ssNumberInput = vanilla.EditText((150, 42, 130, 25), "")  # Default to empty
        
        # Add checkbox for overriding existing feature
        self.w.overrideCheckbox = vanilla.CheckBox((15, 75, 250, 20), "Override existing feature", value=True)
        
        # Add the "Generate Feature" button
        self.w.createButton = vanilla.Button((15, 110, 270, 30), "Generate Feature", callback=self.createFeature)
        
        # Open the window
        self.w.open()

    def createFeature(self, sender):
        # Get the font
        font = Glyphs.font
        
        # Get user inputs
        suffix = self.w.suffixInput.get().strip()  # Remove any leading/trailing whitespace
        ss_number = self.w.ssNumberInput.get().strip().zfill(2)  # Ensures two-digit ss number
        override = self.w.overrideCheckbox.get()  # Get the checkbox state
        
        # Initialize feature text
        feature_text = []
        
        # Loop through all glyphs in the font
        for glyph in font.glyphs:
            # Check if suffix is provided and if the glyph name ends with the given suffix
            if suffix and glyph.name.endswith(suffix):
                base_name = glyph.name[:-len(suffix)]  # Remove the suffix
                # Add substitution rule to the feature
                feature_text.append(f"sub {base_name} by {glyph.name};")
            elif not suffix:
                # If no suffix is provided, process all glyphs
                base_name = glyph.name  # Use the entire name if suffix is empty
                feature_text.append(f"sub {base_name} by {glyph.name};")
        
        # Combine all substitution rules into a single feature string
        feature_code = "\n".join(feature_text)
        
        # Feature name in the form "ssXX" where XX is the ss number
        feature_tag = f"ss{ss_number}"
        
        # Check if the feature already exists
        existing_feature = None
        for feature in font.features:
            if feature.name == feature_tag:
                existing_feature = feature
                break
        
        if existing_feature:
            if override:
                # Remove the existing feature if override is checked
                font.features.remove(existing_feature)
                print(f"Existing {feature_tag} feature deleted.")
            else:
                # Create a new feature with the same name
                print(f"Feature {feature_tag} already exists. Creating a new feature with the same name.")
        
        # Create a new feature
        new_feature = GSFeature()
        new_feature.name = feature_tag  # Use name for the feature
        new_feature.code = feature_code
        new_feature.automatic = False  # Disable automatic name
        font.features.append(new_feature)
        
        print(f"{feature_tag} feature created successfully.")

# Run the Stylistic Set Creator
StylisticSetCreator()
