import unittest
from pydantic import BaseModel
from typing import Dict
from aisuite.utils.tool_manager import ToolManager  # Import your ToolManager class


# Define a sample tool function and Pydantic model for testing
class TemperatureParams(BaseModel):
    location: str
    unit: str = "Celsius"


def get_current_temperature(location: str, unit: str = "Celsius") -> Dict[str, str]:
    """Gets the current temperature for a specific location and unit."""
    return {"location": location, "unit": unit, "temperature": "72"}


def missing_annotation_tool(location, unit="Celsius"):
    """Tool function without type annotations."""
    return {"location": location, "unit": unit, "temperature": "72"}


class TestToolManager(unittest.TestCase):
    def setUp(self):
        self.tool_manager = ToolManager()

    def test_add_tool_with_pydantic_model(self):
        """Test adding a tool with an explicit Pydantic model."""
        self.tool_manager.add_tool(get_current_temperature, TemperatureParams)
        tools = self.tool_manager.tools()
        self.assertIn(
            "get_current_temperature", [tool["function"]["name"] for tool in tools]
        )

    def test_add_tool_with_signature_inference(self):
        """Test adding a tool and inferring parameters from the function signature."""
        self.tool_manager.add_tool(get_current_temperature)  # No model provided
        tools = self.tool_manager.tools()
        self.assertIn(
            "get_current_temperature", [tool["function"]["name"] for tool in tools]
        )

    def test_add_tool_missing_annotation_raises_exception(self):
        """Test that adding a tool with missing type annotations raises a TypeError."""
        with self.assertRaises(TypeError):
            self.tool_manager.add_tool(missing_annotation_tool)

    def test_execute_tool_valid_parameters(self):
        """Test executing a registered tool with valid parameters."""
        self.tool_manager.add_tool(get_current_temperature, TemperatureParams)
        tool_call = {
            "name": "get_current_temperature",
            "arguments": {"location": "San Francisco", "unit": "Celsius"},
        }
        result, result_message = self.tool_manager.execute_tool(tool_call)

        # Check that the result matches expected output
        self.assertEqual(result["location"], "San Francisco")
        self.assertEqual(result["unit"], "Celsius")
        self.assertEqual(result["temperature"], "72")

    def test_execute_tool_invalid_parameters(self):
        """Test that executing a tool with invalid parameters returns an error message."""
        self.tool_manager.add_tool(get_current_temperature, TemperatureParams)
        tool_call = {
            "name": "get_current_temperature",
            "arguments": {"location": 123},  # Invalid type for location
        }
        result, result_message = self.tool_manager.execute_tool(tool_call)

        # Check that an error message was returned
        self.assertIn("error", result)
        self.assertIn("Error in tool", result["error"])


if __name__ == "__main__":
    unittest.main()
