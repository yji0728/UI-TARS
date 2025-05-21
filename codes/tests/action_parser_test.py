import unittest
from ui_tars.action_parser import (
    parsing_response_to_pyautogui_code,
    parse_action,
    parse_action_to_structure_output,
)


class TestActionParser(unittest.TestCase):
    def test_parse_action(self):
        action_str = "click(start_box='(10,20,30,40)')"
        result = parse_action(action_str)
        self.assertEqual(result['function'], 'click')
        self.assertEqual(result['args']['start_box'], '(10,20,30,40)')

    def test_parse_action_to_structure_output(self):
        text = "Thought: test\nAction: click(start_box='(10,20,30,40)')"
        actions = parse_action_to_structure_output(
            text, factor=28, origin_resized_height=224, origin_resized_width=224
        )
        self.assertEqual(actions[0]['action_type'], 'click')
        self.assertIn('start_box', actions[0]['action_inputs'])

    def test_parsing_response_to_pyautogui_code(self):
        responses = {"action_type": "hotkey", "action_inputs": {"hotkey": "ctrl v"}}
        code = parsing_response_to_pyautogui_code(responses, 224, 224)
        self.assertIn('pyautogui.hotkey', code)


if __name__ == '__main__':
    unittest.main()
