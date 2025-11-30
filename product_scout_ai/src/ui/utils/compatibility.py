"""
Compatibility fixes for Gradio 6.0+

This module provides workarounds for Gradio version compatibility issues.
"""
import gradio as gr
import warnings


def safe_textbox(**kwargs):
    """
    Create a Textbox component with Gradio 6.x compatibility.
    """
    # Filter out problematic parameters that might cause internal errors
    safe_kwargs = kwargs.copy()

    # Handle max_lines to lines conversion for Gradio 6.x
    if 'max_lines' in safe_kwargs:
        safe_kwargs['lines'] = safe_kwargs.pop('max_lines')
        warnings.warn("Converting max_lines to lines for Gradio 6.x compatibility", DeprecationWarning)

    return gr.Textbox(**safe_kwargs)


def safe_number(**kwargs):
    """
    Create a Number component with Gradio 6.x compatibility.
    """
    # Filter out parameters that might cause issues
    safe_kwargs = kwargs.copy()

    # Remove any potentially problematic parameters
    # (Gradio 6.x Number component should work fine)

    return gr.Number(**safe_kwargs)


def safe_dropdown(**kwargs):
    """
    Create a Dropdown component with Gradio 6.x compatibility.
    """
    safe_kwargs = kwargs.copy()

    # Handle max_choices to choices conversion for Gradio 6.x
    if 'max_choices' in safe_kwargs:
        safe_kwargs['choices'] = safe_kwargs.pop('max_choices')
        warnings.warn("Converting max_choices to choices for Gradio 6.x compatibility", DeprecationWarning)

    return gr.Dropdown(**safe_kwargs)


def apply_gradio_fixes():
    """
    Apply monkey patches to fix known Gradio 6.x issues.
    """
    try:
        # Try to patch the fill_expected_parents method
        original_fill_expected_parents = gr.blocks.fill_expected_parents

        def safe_fill_expected_parents(self):
            """Safe version that avoids the .page attribute error."""
            try:
                return original_fill_expected_parents(self)
            except AttributeError as e:
                if "'page' attribute" in str(e):
                    # Fallback: create a simple parent mapping
                    return {}
                else:
                    raise e

        # Apply the patch
        gr.blocks.fill_expected_parents = safe_fill_expected_parents

        print("✅ Applied Gradio 6.x compatibility fixes")
        return True

    except Exception as e:
        print(f"⚠️  Could not apply Gradio fixes: {e}")
        return False